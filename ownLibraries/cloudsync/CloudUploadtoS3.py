#!/usr/bin/env python

import os
import sys
import boto3
from .tools import CloudTools


class UploadToS3():

    def __init__(self):
        """
        Upload Files from a local folder to  a S3 bucket subfolder with name <destination> as subfolder
        """
        pass

    @staticmethod
    def upload(parameters, metadata=False):
        s3_client = boto3.client('s3')

        local_directory = parameters['local_directory']
        bucket = parameters['bucket']
        destination = parameters['destination']

        video_name = parameters['vid-name']
        image_name = parameters['img-name']
        json_name = parameters['json-name']
        # construct the full local path
        video_path = os.path.join(local_directory, video_name)
        image_path = os.path.join(local_directory, image_name)
        json_path = os.path.join(local_directory, json_name)

        # Set name in s3 to local files
        s3_video = video_name
        s3_imagen = image_name
        s3_json = json_name

        # Upload Video
        state_one = UploadToS3.s3Sync(s3_client, s3_video, video_path, bucket, destination)
        state_two = UploadToS3.s3Sync(s3_client, s3_imagen, image_path, bucket, destination)
        state_three = UploadToS3.s3Sync(s3_client, s3_json, json_path, bucket, destination)

        if state_one is True and state_two is True and state_three is True:
            if metadata != False:
                upload_status = CloudTools.write_sync_status(path_to_folder=local_directory, file_name='sync_status', metadata=metadata)
            else:
                upload_status = CloudTools.write_sync_status(path_to_folder=local_directory, file_name='sync_status')

            print('SYC TO s3 class successful!, status: {}'.format(upload_status))
        else:
            print('THERE WAS A PROBLEM IN SYNC, one state does not pass checks')

    @staticmethod
    def s3Sync(s3_client, s3_path, local_path, bucket, destination):
        try:
            if '.json' in s3_path:
                print("Uploading {} to  {}...".format(local_path, bucket + '/' + 'databases' + '/' + s3_path))
                s3_client.upload_file(local_path,
                                      bucket,
                                      'databases' + '/' + s3_path,
                                      ExtraArgs={'ACL': 'public-read'})
                return True
            else:
                print("Uploading {} to  {}...".format(local_path, bucket + '/' + destination + '/' + s3_path))
                s3_client.upload_file(local_path,
                                      bucket,
                                      destination + '/' + s3_path,
                                      ExtraArgs={'ACL': 'public-read'})
                return True
        except Exception as e:
            print('ERROR in Upload:::', e)
            return False

    @staticmethod
    def upload_private(parameters, metadata=False):
        s3_client = boto3.client('s3')

        local_directory = parameters['local_directory']
        bucket = 'infractor-serve-assets-to-app'
        destination = parameters['destination']

        video_name = parameters['vid-name']
        image_name = parameters['img-name']
        json_name = parameters['json-name']
        # construct the full local path
        video_path = os.path.join(local_directory, video_name)
        image_path = os.path.join(local_directory, image_name)
        json_path = os.path.join(local_directory, json_name)

        # Set name in s3 to local files
        s3_video = video_name
        s3_imagen = image_name
        s3_json = json_name

        # Upload Video
        state_one = UploadToS3.s3Sync_private(s3_client, s3_video, video_path, bucket, destination)
        state_two = UploadToS3.s3Sync_private(s3_client, s3_imagen, image_path, bucket, destination)
        state_three = UploadToS3.s3Sync_private(s3_client, s3_json, json_path, bucket, destination)

        if state_one is True and state_two is True and state_three is True:
            if metadata != False:
                upload_status = CloudTools.write_sync_status(path_to_folder=local_directory, file_name='sync_status_no_plate',
                                                             metadata=metadata)
            else:
                upload_status = CloudTools.write_sync_status(path_to_folder=local_directory, file_name='sync_status_no_plate')

            print('SYC TO s3 class successful!, status: {}'.format(upload_status))
        else:
            print('THERE WAS A PROBLEM IN SYNC, one state does not pass checks')

    @staticmethod
    def s3Sync_private(s3_client, s3_path, local_path, bucket, destination):
        try:
            if '.json' in s3_path:
                print("Uploading {} to  {}...".format(local_path, bucket + '/' + 'databases' + '/' + s3_path))
                s3_client.upload_file(local_path,
                                      bucket,
                                      'databases' + '/' + s3_path,
                                      ExtraArgs={'ACL': 'public-read'})
                return True
            else:
                print("Uploading {} to  {}...".format(local_path, bucket + '/' + 'NoPlate' + '/' + destination + '/' + s3_path))
                s3_client.upload_file(local_path,
                                      bucket,
                                      'NoPlate' + '/' + destination + '/' + s3_path,
                                      ExtraArgs={'ACL': 'public-read'})
                return True
        except Exception as e:
            print('ERROR in Upload:::', e)
            return False


if __name__ == '__main__':
    local_directory, bucket, destination = sys.argv[1:4]

    upload = UploadToS3()

    upload.upload(local_directory, bucket, destination)
