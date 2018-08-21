import os
from .tools import CloudTools


class CloudPaths():
    S3Path = 'https://s3.amazonaws.com/'
    S3Bucket = 'raw-assets-dems'
    subDirName = None

    # log dirs
    HOME = os.getenv('HOME') + '/'
    WORKDIR_PATH = HOME + 'WORKDIR/'
    LOG_FOLDER = WORKDIR_PATH + 'Logs/'
    LOG_PATH = LOG_FOLDER + 'LOGGIN_cloudsync_{}.log'.format(CloudTools.today_date)
