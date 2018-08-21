# -*- coding: utf-8 -*-

from .tools import CloudTools


class PlateRecognition():
    def __init__(self):
        """
        Take a cropped image and returns json with plate detection if not return empty list
        """
        pass

    @staticmethod
    def get_response(image_path):
        """
        Obtain plate information in image_path input cropped image
        :param image_path: Cropped image
        :return: JSON object as dict, if not possible return empty list
        """
        try:
            # Obtain response from OpenALP API for image_path input
            response = CloudTools.api_call_platesv2(image_path)
            if len(response['results']) > 0:
                plateDict = response['results'][0]
                plate = plateDict['candidates'][0]
                prob = plateDict['confidence']
                prob = str(round(float(prob) / 100, 2))
                box = plateDict['coordinates']
                return [plate, prob, box]
            else:
                return []
        except Exception as e:
            print(' No internet Connection or: {}', e)
            return []

    @classmethod
    def get_plates(cls, img_objs):
        """
        Obtain plates information and append it to dictionary for next process

        :param img_objs: image dict with information of cropped images
        :return: JSON as dict with plate information
        """
        # Make a copy of incoming image objects
        # Place holder for plate information
        img_objs['plate-detection'] = {}

        for original_image, crop_image in img_objs['cropped-images'].items():
            if crop_image != 0:

                # Obtain response from API
                information = cls.get_response(crop_image)

                if len(information) > 0:

                    plate, prob, box = information[0], information[1], information[2]

                    detection = {'path': crop_image,
                                 'plate': plate,
                                 'box': box,
                                 'prob': prob
                                 }

                    img_objs['plate-detection'][original_image] = detection
                else:

                    print(' NO PLATES IN IMAGE {}'.format(crop_image))
                    detection = {'path': crop_image,
                                 'plate': 'NOPLATE',
                                 'box': 0,
                                 'prob': 0
                                 }
                    img_objs['plate-detection'][original_image] = detection
            else:
                detection = {'path': original_image,
                             'plate': 'NOPLATE',
                             'box': 0,
                             'prob': 0
                             }
                img_objs['plate-detection'][original_image] = detection

        return img_objs


if __name__ == '__main__':
    pass
