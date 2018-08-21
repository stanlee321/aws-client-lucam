import collections
import multiprocessing
# Cloud Tools
from .CloudDetectPlate import PlateRecognition
from .CloudUploadtoS3 import UploadToS3
from .CloudCreateJSON import CreateJSON
from .CloudCarDetector import CarDetector
from .logs import CloudLogs as LOGGER
from .tools import CloudTools
# from ..object_detection.model_cardetector import CarDetector
from .createPlate import WritePlate


class CloudSyncProcess(multiprocessing.Process):
    def __init__(self, out_pipe=None, metadata=False):
        """
        CloudSync process, this method allows to sync the generated
        assets into a production folder to be uploaded to AWS.

        :param out_pipe: absolute folder path to be sync as string
        """
        super(CloudSyncProcess, self).__init__()

        # Instantiate objects
        self.plateRegionDetector = CarDetector()
        self.plateRecog = PlateRecognition()
        self.writePlate = WritePlate()
        self.createJSON = CreateJSON()
        self.uploadToS3 = UploadToS3()
        self.out_pipe = out_pipe
        self.inputs_queue = collections.deque(maxlen=50)
        self.state = True
        self.metadata = metadata
        
    def run(self):
        while True:
            # Receive the input path
            _input = self.out_pipe.recv()

            # Append this job to a list of jobs
            self.inputs_queue.appendleft(_input)
            LOGGER.info('input in while loop from out of pipe', _input)

            # compare if exist doubles in ante last append
            LOGGER.info('QUEUE is', self.inputs_queue)
            print('queue', self.inputs_queue[-1])

            if len(self.inputs_queue) > 0 and self.state is True:

                self.state = False
                LOGGER.info('I AM INTO THE PROCESS with this work', self.inputs_queue[-1])
                path_to_folder = self.inputs_queue[-1]

                # Cut cars region with API
                img_objs = self.plateRegionDetector.get_objects(folder_to_images=path_to_folder)

                # Detect plate in cropped images as feed
                img_objs = self.plateRecog.get_plates(img_objs)
                img_objs['detected_plate'] = {}
                for original_image, _detection in img_objs['plate-detection'].items():

                    LOGGER.info('INTO the plate.detection for loop with: ',
                                'original: {} and detection: {}'.format(original_image, _detection))

                    # Read data
                    path_to_image, plate, box, prob = _detection['path'], _detection['plate'], \
                                                      _detection['box'], _detection['prob']

                    if _detection['plate'] != 'NOPLATE':
                        # Start Sync to AWS S3
                        LOGGER.info('DETECTION WITH PLATE_ ', _detection['plate'])

                        # Write the detected plate as png with bounding box
                        path_to_new_image = self.writePlate(path_to_image=path_to_image,
                                                            region=box,
                                                            plate=plate['plate'])

                        # Keep track of original image and his plate region detection
                        img_objs['detected_plate'][original_image] = path_to_new_image

                        # Get parameters for the sync to s3 and also write JSON with thre
                        # routes to video and detected plate

                        parameters = self.createJSON(path_to_new_image=path_to_new_image,
                                                     prob=prob,
                                                     plate=plate['plate'])

                        if parameters['vid-name'] == 'NOVIDEO':
                            print('No video in this folder, passing...')
                        else:
                            print('Syncing...')

                            # Upload to S3
                            if self.metadata is True:
                                self.uploadToS3.upload(parameters,
                                                       metadata=img_objs)
                            else:
                                self.uploadToS3.upload(parameters)
                                print('Upload Successful!')
                                print('Deleting unused assets')
                                # Delete unused assets
                                delete_status = CloudTools.delete_track_images(img_objs)
                                if delete_status is True:
                                    print('Deletion Successful')
                                else:
                                    print('Cant Delete with status', delete_status)

                    elif _detection['plate'] == 'NOPLATE':
                        """
                        UPLOAD TO PRIVATE BUCKET
                        """
                        print('PRIVATE CLOUD UPLOAD STARTED')
                        print('PLATE TO UPLOAD', plate)
                        # Write the detected plate as png with bounding box
                        path_to_new_image = self.writePlate(path_to_image=path_to_image,
                                                            region=box,
                                                            plate=plate)

                        img_objs['detected_plate'][original_image] = path_to_new_image

                        # Get parameters for the sync to s3 and also write JSON with thre
                        # routes to video and detected plate

                        parameters = self.createJSON.create_json_private(path_to_new_image=path_to_new_image,
                                                                        prob=prob,
                                                                        plate=plate)
                        # Upload to S3
                        self.uploadToS3.upload_private(parameters)

                        # Delete unused assets
                        delete_status = CloudTools.delete_track_images(img_objs)
                        if delete_status is True:
                            print('Deletion Successful')
                        else:
                            print('Cant Delete with status', delete_status)

                    else:
                        print('WARNING, NO INTERNET CONNECTION OR API NANONETS DIE!!!')
                        print('WRITING NULL JSON,')

                        path_to_new_image = path_to_image[:path_to_image.rfind('.')]

                        parameters = self.createJSON(path_to_new_image=path_to_new_image,
                                                     prob=0,
                                                     plate='NOPLATE',
                                                     json_null=True)

                        print('NULL JSON IN DISK?', parameters)

                self.inputs_queue.pop()
                self.state = True
            else:
                LOGGER.warning('passing because I receive the same image', self.inputs_queue)
                pass


if __name__ == '__main__':
    pass
