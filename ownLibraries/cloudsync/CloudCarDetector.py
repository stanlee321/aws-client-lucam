from PIL import Image, ImageDraw
import cv2
import os
import operator
# Local imports
from .tools import CloudTools
from .logs import CloudLogs as LOGGER


class CarDetector():
    shape = (2560, 1920)    # Taking the 5 mpx resolution 2560 x 1920 as reference

    scaleX = 8
    scaleY = 8

    new_shape = (int(shape[0] / scaleX), int(shape[1] / scaleY))

    def __init__(self):
        """
        This class takes input image paths and returns coord of object "car" in
        this input image.
        """

        print('Car Detector created')

    @staticmethod
    def get_coord(folder_to_images):
        """
        Take path to folder with  images in it and return coordinates of objects detected on this.

        :param folder_to_images:
        :return: Dictionary with detected object
        """
        paths_to_images_list = CloudTools.load_images_paths(folder_to_images)

        # Process the images, convert to low resolution
        image_objs = CloudTools.preprocess_images(paths_to_images_list,
                                                   CarDetector.new_shape)

        # Placeholder for processed information
        image_objs['detection'] = {}

        # Loop into every low resolution image 'image-resize-paths' dict
        for original_img, resized_img in image_objs['original_to_resize_images'].items():

            try:
                # Call NANONETS API for find the cars in the low res image
                response = CloudTools.api_call(resized_img)
                print('RESponse', response)
                # Obtain prediction from JSON response
                prediction = response["result"][0]["prediction"]

                # Aux array variable for track the response from API over
                # detected object.
                _img = Image.open(resized_img)
                draw = ImageDraw.Draw(_img, mode="RGBA")

                # Aux list for keep track of areas
                possible_detections = []

                # Loop over each prediction
                for index, pred in enumerate(prediction):

                    x, y = pred["xmin"], pred["ymin"]
                    w, h = pred["xmax"], pred["ymax"]

                    area = (w-x)*(h-y)

                    # centroid = CloudTools.get_centroid(x, y, w, h)

                    # Draw simple rectangle over detected object.
                    detection = {
                        'detection': True,
                        'area': area,
                        'cord': (x, y, w, h),
                        }
                    # append this to list comparator
                    possible_detections.append(detection)

                possible_areas = []
                # Append all areas to possible areas list
                for possible in possible_detections:
                    possible_areas.append(possible['area'])

                # Get the max area for this list
                _, max_area = max(enumerate(possible_areas), key=operator.itemgetter(1))

                # Give name to detected image
                detection_image_name = '{}_detected.jpg'.format(resized_img[:resized_img.rfind('.')])

                # Official Detection filter for max area between detections.
                for possible in possible_detections:
                    if possible['area'] == max_area:
                        # Rename this possible as official detection
                        official_detection = possible

                        # Add to this offical detection img-url path for detected object
                        official_detection['img-url'] = detection_image_name

                        # Draw this official detection to image
                        x, y, w, h = official_detection['cord']
                        draw.rectangle((x, y, w, h))

                        # Add to image objects this official detection for original image input
                        image_objs['detection'][original_img] = official_detection

                # Save the images  and draw object with the max area on it.
                _img.save(detection_image_name)

            except Exception as e:
                print('MAYBE API NANONETS DIE !!! with exception {}'.format(e))
                print('returning zeroes ')
                image_objs['detection'][original_img] = {
                                                        'detection': False,
                                                        'area': 0,
                                                        'cord': 0,
                                                    }
        return image_objs

    @classmethod
    def get_objects(cls, folder_to_images='.'):
        """
            Cut the images according to the Detection results

        :param folder_to_images:  string as path to image absolute path
        :return: dictionary with paths to cropped images
        """
        # Get path to image with detected object on it
        img_objs = CarDetector.get_coord(folder_to_images)

        # Placeholder for cropped images
        img_objs['cropped-images'] = {}

        # Loop over every detection
        for original_image_path, detection in img_objs['detection'].items():
            # Set name extension _cropped.jpg to this cropped image
            cropped_image_name = '{}_cropped.jpg'.format(original_image_path[:original_image_path.rfind('.')])

            if detection['detection'] is True:
                x, y, w, h = detection['cord']
                # Read detected images
                original_image_raw = cv2.imread(original_image_path)

                # Rescale low res detected image coordinates to his original resolution values.
                original_image_upscaled = cv2.resize(original_image_raw, cls.shape)
                x0 = x*cls.scaleX
                y0 = y*cls.scaleY

                x1 = w*cls.scaleX
                y1 = h*cls.scaleY

                # Cut image in HR image
                cropped_original_raw = original_image_upscaled[y0: y1, x0: x1]

                # Add cropped-images as key for original-Image-path and route to the cropped image
                img_objs['cropped-images'][original_image_path] = cropped_image_name

                cv2.imwrite(cropped_image_name, cropped_original_raw)
            else:
                img_objs['cropped-images'][original_image_path] = 0

        return img_objs


if __name__ == '__main__':

    cardetector = CarDetector()
    directorioDeTrabajo = os.getenv('HOME') + '/' + '10-02-27_ROJO_izquierdo_x1_-Infraccion_2607AXG_100/'
    paths_to_images = cardetector.get_objects(directorioDeTrabajo)
    print('Cars REGIONS ARE:', paths_to_images)

