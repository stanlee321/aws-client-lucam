# -*- coding: utf-8 -*-

import json
import io
import os
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from .tools import CloudTools
from .paths import CloudPaths
from ..pathsandnames import PathsAndNames

import uuid

class CreateJSON():

    def __init__(self):
        """
            Create a subfolder in s3 bucket
            Creates a JSON in local directory
        """
        pass

    @staticmethod
    def create_json(loc='', plate='', prob='', infraction_date='', infraction_hour='', image_on_s3='', video_on_s3=''):
        old_hour = iter(infraction_hour)
        new_hour = ':'.join(a + b for a, b in zip(old_hour, old_hour))
        toJSON = {
            'location': loc,
            'plate': plate,
            'prob': prob,
            'datetime': str(infraction_date),
            'hour': new_hour,
            'image_path': image_on_s3,
            'video_path': video_on_s3
        }
        return toJSON

    @staticmethod
    def create_json_private(path_to_new_image='', prob=0, plate='', json_null=False):
        """
        Creates JSON output with assets information

        :param path_to_new_image: Path to image with plate
        :param prob: prob of the detection
        :param plate: plate number
        :return: JSON object as dict with information to be upload to S3
        """
        path_to_folder, image_name, video_name, subDirName = CloudTools.getNames(path_to_new_image)
        destination = str(uuid.uuid4())


        # Create names placeholders
        path_to_image_on_S3 = CloudPaths.S3Path + 'infractor-serve-assets-to-app' + '/' + 'NoPlate' + '/' + destination + '/' + image_name
        path_to_video_on_S3 = CloudPaths.S3Path + 'infractor-serve-assets-to-app' + '/' + 'NoPlate' + '/' + destination + '/' + video_name

        # Prepare route for upload files to s3 into the subfolder /subDirName in S3
        CloudTools.createSubDirOnS3(CloudPaths.S3Bucket, subDirName)

        # Check for Location path

        location = CloudTools.load_loation()

        if plate == 'NOPLATE':
            """
            Normal sync behavior
            """

            infractionDate = video_name.split('_')[0]
            infractionHour = video_name.split('_')[1].replace('-', ':')

            toJSON = CreateJSON.create_json(loc=location,
                                            plate='x',
                                            prob=str(prob),
                                            infraction_date=infractionDate,
                                            infraction_hour=infractionHour,
                                            image_on_s3=path_to_image_on_S3,
                                            video_on_s3=path_to_video_on_S3)

            # Write JSON file
            with io.open('{}/{}.json'.format(path_to_folder, destination), 'w', encoding='utf8') as outfile:
                str_ = json.dumps(toJSON,
                                  indent=4,
                                  sort_keys=True,
                                  separators=(',', ': '), ensure_ascii=False)
                # Out
                outfile.write(to_unicode(str_))
        # Return parameters for AWS Sync
        params = {
            'plate': plate,
            'local_directory': path_to_folder,
            'bucket': 'infractor-serve-assets-to-app',
            'destination': destination,
            'img-name': image_name,
            'vid-name': video_name,
            'json-name': '{}.json'.format(destination)
        }

        return params

    def __call__(self, path_to_new_image='', prob=0, plate='', json_null=False):
        """
        Creates JSON output with assets information

        :param path_to_new_image: Path to image with plate
        :param prob: prob of the detection
        :param plate: plate number
        :return: JSON object as dict with information to be upload to S3
        """
        path_to_folder, image_name, video_name, subDirName = CloudTools.getNames(path_to_new_image)

        if json_null is False:

            # Create names placeholders
            path_to_image_on_S3 = CloudPaths.S3Path + CloudPaths.S3Bucket + '/' + subDirName + '/' + image_name
            path_to_video_on_S3 = CloudPaths.S3Path + CloudPaths.S3Bucket + '/' + subDirName + '/' + video_name

            # Prepare route for upload files to s3 into the subfolder /subDirName in S3
            CloudTools.createSubDirOnS3(CloudPaths.S3Bucket, subDirName)

            # Check for Location path

            location = CloudTools.load_loation()

            if video_name != 'NOVIDEO' and plate != 'NOPLATE':
                """
                Normal sync behavior
                """
                infractionDate = video_name.split('_')[0]
                infractionHour = video_name.split('_')[1].replace('-', ':')

                toJSON = CreateJSON.create_json(loc=location,
                                                plate=plate,
                                                prob=str(prob),
                                                infraction_date=infractionDate,
                                                infraction_hour=infractionHour,
                                                image_on_s3=path_to_image_on_S3,
                                                video_on_s3=path_to_video_on_S3)

                # Write JSON file
                with io.open('{}/{}.json'.format(path_to_folder, subDirName), 'w', encoding='utf8') as outfile:
                    str_ = json.dumps(toJSON,
                                      indent=4,
                                      sort_keys=True,
                                      separators=(',', ': '), ensure_ascii=False)
                    # Out
                    outfile.write(to_unicode(str_))

            elif plate != 'NOPLATE' and video_name == 'NOVIDEO':
                """
                Extreme case, not sync this
                """

                toJSON = {
                    'location': location,
                    'plate': plate,
                    'prob': prob,
                    'datetime': 'NODATE',
                    'hour': 'NOHOUR',
                    'image_path': path_to_image_on_S3,
                    'video_path': 'NOVIDEO'
                }

                toJSON = CreateJSON.create_json(loc=location,
                                                plate=plate,
                                                prob=str(prob),
                                                infraction_date='NODATE',
                                                infraction_hour='NOHOUR',
                                                image_on_s3=path_to_image_on_S3,
                                                video_on_s3=path_to_video_on_S3)
                # Write JSON file
                with io.open('{}/{}.json'.format(path_to_folder, subDirName), 'w', encoding='utf8') as outfile:
                    str_ = json.dumps(toJSON,
                                      indent=4,
                                      sort_keys=True,
                                      separators=(',', ': '), ensure_ascii=False)
                    # Out
                    outfile.write(to_unicode(str_))
            else:
                """
                Also exterme case, not sync this
                """

                toJSON = CreateJSON.create_json(loc=location,
                                                plate=plate,
                                                prob=str(prob),
                                                infraction_date='NODATE',
                                                infraction_hour='NOHOUR',
                                                image_on_s3='NOIMAGE',
                                                video_on_s3='NOVIDEO')
                # Write JSON file
                with io.open('{}/{}.json'.format(path_to_folder, subDirName), 'w', encoding='utf8') as outfile:
                    str_ = json.dumps(toJSON,
                                      indent=4,
                                      sort_keys=True,
                                      separators=(',', ': '), ensure_ascii=False)
                    # Out
                    outfile.write(to_unicode(str_))

            # Return parameters for AWS Sync
            params = {
                'plate': plate,
                'local_directory': path_to_folder,
                'bucket': CloudPaths.S3Bucket,
                'destination': subDirName,
                'img-name': image_name,
                'vid-name': video_name,
                'json-name': '{}.json'.format(subDirName)
            }

            return params
        else:
            """
            Create default null json 
            """
            # Check for Location path
            location = CloudTools.load_loation()

            toJSON = CreateJSON.create_json(loc=location,
                                            plate='NOPLATE',
                                            prob='NOPROB',
                                            infraction_date='NODATE',
                                            infraction_hour='NOHOUR',
                                            image_on_s3='NOIMAGE',
                                            video_on_s3='NOVIDEO')

            # Write JSON file
            with io.open('{}/{}.json'.format(path_to_folder, subDirName), 'w', encoding='utf8') as outfile:
                str_ = json.dumps(toJSON,
                                  indent=4,
                                  sort_keys=True,
                                  separators=(',', ': '), ensure_ascii=False)
                # Out
                outfile.write(to_unicode(str_))

            return True



if __name__ == '__main__':
    pass