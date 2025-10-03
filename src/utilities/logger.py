from src.utilities.constants import ConstantsFetcher
import os 
import logging 



class Logger:

    def __init__(self):
        ...

    @staticmethod
    def getLogger(name:str):
        
        logging_format = "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)s - %(message)s"

        logs_folder = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)

        log_file = os.path.join(logs_folder, ConstantsFetcher.fetch_constants("logging")['filename'])

        logging.basicConfig(
            level=logging.DEBUG,
            format=logging_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ])
        
        return logging.getLogger(name)

