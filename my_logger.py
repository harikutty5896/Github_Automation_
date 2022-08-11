import logging

logging.basicConfig(filename="VersionUpdater_log.log", format='%(asctime)s - %(levelname)s  - %(message)s',
                    filemode='a', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)