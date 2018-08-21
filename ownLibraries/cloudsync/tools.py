import glob
import cv2
import json
import requests
import subprocess
import os
import boto3
import datetime
import glob

import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str


class CloudTools:
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')

    def __init__(self):
        pass

    @staticmethod
    def getdatetime():
        return datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    @staticmethod
    def load_images_paths(images_folder):
        """
        Load the images into a list from input images_folder directory

        :param images_folder: Absolute path to folder containing images: String
        :return: List of strings containing Abs. path to images in input images_folder.
        """
        paths_to_images = []
        # List directory
        for image in glob.glob("{}*.jpg".format(images_folder)):
            paths_to_images.append(image)

        return paths_to_images

    @staticmethod
    def getNames(path_to_image):
        """
        Obtain the filenames of assets in local disk,
        this uses path_to_image as reference.

        :param path_to_image: path to image with plate
        :return: tuple of strings with dirs to assets
        """

        splited_path = path_to_image.split('/')
        subDirName = os.path.join(*splited_path[-2:-1])  # folder to images /folder/, subfolder in s3
        path_to_folder = '/' + os.path.join(*splited_path[:-1])

        f = []
        for (dirpath, dirnames, filenames) in os.walk(path_to_folder):
            f.extend(filenames)

        video_name = None
        image_name = path_to_image.split('/')[-1]

        for i, file in enumerate(f):
            if '.mp4' in file:
                video_name = file
                break
            else:
                video_name = 'NOVIDEO'

        return path_to_folder, image_name, video_name, subDirName

    @staticmethod
    def preprocess_images(paths_to_images, new_shape):
        """
        Resize images to new_shape (320,240)

        :param paths_to_images:  HD image to resize :string
        :param new_shape: new shape to be used: array
        :return: Dictionary with 'image-resize-pahts' key and absolute path '_resize.jpg'
                 as value.
        """

        image_paths = {'original_to_resize_images': {}}

        # Resize all the images in target folder
        for i, path in enumerate(paths_to_images):

            # Give name to resize image
            resized_name = '{}_resize.jpg'.format(path[:path.rfind('.')])

            # Keep track of original images and re-sized
            image_paths['original_to_resize_images'][path] = resized_name

            # Read original image and resized it
            raw_image = cv2.imread(path)
            image = cv2.resize(raw_image, new_shape)

            # Save image in disk as meta
            cv2.imwrite(resized_name, image)

        return image_paths

    @staticmethod
    def get_centroid(x, y, w, h):
        """
        Calculates the Centroid of a Rectangle input
        :param x: int
        :param y: int
        :param w: int
        :param h: int
        :return: Tuple Array
        """

        x1 = int(w / 2)
        y1 = int(h / 2)
        cx = x + x1
        cy = y + y1
        return cx, cy

    @staticmethod
    def api_call(image):
        """
        This function Use  https://app.nanonets.com/ API  Call
        for find the cars in the input image, this accepts image path and return JSON
        containing the information about the detection.

        :param image: Pil Image
        :return: bounding boxes prediction
        """
        API_KEY = 'NyEWKG4sr8ymeXOzE9rDfUJ69qBatIOhcbWp0OOVIAx'
        MODEL_ID = 'bee0b774-b81c-401a-ad0d-baf5d3eef886'
        URL = "https://app.nanonets.com/api/v2/ObjectDetection/Model/{}/LabelFile/".format(MODEL_ID)

        # make a prediction on the image
        data = {
            'file': open(image, 'rb'),
            'modelId': ('', MODEL_ID)
        }

        headers = {
            'accept': 'multipart/form-data'
        }

        response = requests.post(URL, headers=headers,
                                 files=data,
                                 auth=requests.auth.HTTPBasicAuth(API_KEY, ''))

        return json.loads(response.text)

    @staticmethod
    def api_call_platesv2(image):
        """
        This method calls OpenALP API for detect plates in cars, this have limited use calls.

        :param image: Absolute path to image: string.
        :return: JSON response as dict
        """
        # make a prediction on the image
        API_KEY = 'sk_DEMODEMODEMODEMODEMODEMO'
        URL = 'https://api.openalpr.com/v2/recognize?recognize_vehicle=1&country=us&secret_key={}'.format(API_KEY)
        data = {
            'image': open(image, 'rb')
        }

        headers = {
            'accept': 'multipart/form-data'
        }

        response = requests.post(URL, headers=headers,
                                 files=data,
                                 auth=requests.auth.HTTPBasicAuth(API_KEY, ''))

        return json.loads(response.text)

    @staticmethod
    def api_send_notification(dict_to_send):
        """
        This method send a POST request to AWS that send a notification to email

        :param dict_to_send: Dict containing the information about the infraction.
        :return: Status code, if 200 send was successfully
        """
        # make a prediction on the image
        URL = 'https://4dvcymrc05.execute-api.us-east-1.amazonaws.com/prod/plate'

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(URL,
                                 headers=headers,
                                 json= dict_to_send)

        return response.status_code

    @staticmethod
    def api_call_plates(image):
        """
        Legacy method to call API for plates detection

        :param image: Absolute path to image: string.
        :return: JSON response as dict
        """
        print('IMAGE is:', image)
        cmd = ['curl', 'X', 'POST', '-F', 'image=@{}'.format(image),
               '']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, err = p.communicate()
        out = out.decode('utf-8')
        m = out
        n = json.dumps(m)
        o = json.loads(n)
        return str(o)

    @staticmethod
    def createSubDirOnS3(bucket='clean-assets-dems', subDirName=''):
        """
        Create sub folder dir in S3

        :param bucket:  Target bucket name in S3
        :param subDirName: folder to be created in this bucket
        :return: Response from S3
        """
        s3_client = boto3.client('s3')

        response = s3_client.put_object(
            Bucket=bucket,
            Body='',
            Key='{}/'.format(subDirName),
            ACL='public-read'
        )

        return response

    @staticmethod
    def write_sync_status(path_to_folder='', file_name='', metadata=False):
        """
        Write a json in target dir specifying the state of the cloud sync,
        if this function is called, so sync was successful and a .json was writed
        if target dir for further confirmation.

        :param path_to_folder:
        :param file_name:
        :param metadata:
        :return:
        """
        toJSON = {
            'upload': True,
            'metadata': metadata
        }

        # Write JSON file
        with io.open('{}/{}.json'.format(path_to_folder, file_name), 'w', encoding='utf8') as outfile:
            str_ = json.dumps(toJSON,
                              indent=4,
                              sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            # Out
            outfile.write(to_unicode(str_))

        return 'UPLOADED'

    @staticmethod
    def delete_track_images(image_objs):
        """
        Delete unused images in target dir
        :param img_objs: dict containing all the traked images
        :return: Bool True
        """
        for k, v in image_objs['detected_plate'].items():
            original_image_path = k
            plate_path = v

            reserved_images = [original_image_path, plate_path]

            splited_path = original_image_path .split('/')
            path_to_folder = '/' + os.path.join(*splited_path[:-1])

            local_images = glob.glob(path_to_folder + '/*.jpg')

            to_delete = list(set(local_images) - set(reserved_images))

            for delete in to_delete:
                try:
                    if delete in reserved_images:
                        pass
                    else:
                        os.remove(delete)
                except Exception as e:
                    print('Cant erase this {} with exception {} '.format(delete, e))
        return True

    @staticmethod
    def load_loation():
        """
        Open location file
        :return: string with location
        """
        home = os.getenv('HOME') + '/'
        with open(home + 'trafficFlow/prototipo/installationFiles/pathsandnames') as f:
            location = f.read()
        return location
if __name__ == '__main__':
    #path_to_image = '/home/stanlee321/sargento_flores/2018-02-11_09-09-39/algo.jpg'
    tools = CloudTools()
    location = tools.load_loation()
    #print('my location is ' + location)
    #tools.delete_track_images(path_to_image)

    data = {'location': location}
    response = tools.api_send_notification(data)

    print(response)