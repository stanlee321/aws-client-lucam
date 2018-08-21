import logging

from .paths import CloudPaths


class CloudLogs:
    # Set Logging configs
    LOG_FORMAT = "%(levelname)s %(asctime)s - - %(message)s"
    logging.basicConfig(filename=CloudPaths.LOG_PATH,
                        level=logging.DEBUG,
                        format=LOG_FORMAT)
    logger = logging.getLogger()

    @classmethod
    def warning(cls, script, message):
        cls.logger.info('LOG in :{}: with message: {}'.format(script, message))

    @classmethod
    def info(cls, script, message):
        cls.logger.info('LOG in :{}: with message: {}'.format(script, message))
