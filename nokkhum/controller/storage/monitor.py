'''
Created on Feb 20, 2012

@author: boatkrap
'''

import threading
from nokkhum.cloud.storage import s3
from nokkhum import models
from nokkhum import config
import datetime

import logging
logger = logging.getLogger(__name__)


class StorageMonitoring(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = self.__class__.__name__
        self.daemon = True

        settings = config.Configurator.settings

        access_key_id = settings.get('nokkhum.storage.s3.access_key_id')
        secret_access_key = settings.get(
            'nokkhum.storage.s3.secret_access_key')
        host = settings.get('nokkhum.storage.s3.host')
        port = settings.get('nokkhum.storage.s3.port')
        secure = settings.get('nokkhum.storage.s3.secure_connection')
        self.s3_storage = s3.S3Client(
            access_key_id, secret_access_key, host, port, secure)

        logger.debug("start " + self.name)

    def run(self):
        # buckets = self.s3_storage.get_all_buckets()
        processors = models.Processor.objects().all()

#         for bucket in buckets:
        for processor in processors:
            self.s3_storage.set_bucket_name(str(processor.id))
            bucket = self.s3_storage.get_bucket()
            if bucket is None:
                continue
            logger.debug("bucket: " + bucket.name)
#             processor = models.Processor.objects(id=bucket.name).first()
#             if processor is None:
#                 continue

            for key_name in self.s3_storage.list_file():
                #                logger.debug( "date: "+ key_name)
                dir_date = key_name
                year = int(dir_date[:4])
                month = int(dir_date[4:6])
                day = int(dir_date[6:8])
                dir_time = datetime.datetime(year, month, day)
                current_time = datetime.datetime.now()
                diff_time = current_time - dir_time

#                 logger.debug( "diff date: %d"% diff_time.days)
#                 logger.debug( "storage_period: %d"% processor.storage_period)
                if processor.storage_period > 0 \
                        and diff_time.days > processor.storage_period:
                    #                        print "diff: ", diff_time.days
                    logger.debug("delete key name: %s" % key_name)

                    try:
                        self.s3_storage.delete(key_name)
                        logger.debug("delete bucket: %s key: %s " %
                                     (bucket.name, key_name))
                    except Exception as e:
                        logger.exception(e)

    def __del__(self):
        logger.debug("stop " + self.name)
