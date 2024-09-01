import logging, os, sys
from typing import Union

if __name__ == "__main__":
    print("This file is not meant to be run directly.")
    sys.exit()

# Set up logging

class ScrimLogger:
    logger: logging.Logger
    file_handler: logging.FileHandler
    stream_handler: logging.StreamHandler

    formatter: logging.Formatter
    def __init__(self):
        log_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
        if not os.path.exists(log_dir): # Create log directory if does not exist
            os.mkdir(log_dir)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.file_handler = logging.FileHandler("logs/scrim_helper_logs.log", encoding="utf-8", mode="a")
        self.stream_handler = logging.StreamHandler()

        self.formatter = logging.Formatter("{asctime} - {name} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S")

        self.file_handler.setFormatter(self.formatter)
        self.stream_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stream_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: Union[str, Exception]):
        if isinstance(message, Exception):
            self.logger.error(message, exc_info=True)
        else:
            self.logger.error(message)
    
    def critical(self, message: Union[str, Exception]):
        if isinstance(message, Exception):
            self.logger.critical(message, exc_info=True)
        else:
            self.logger.critical(message)

scrim_logger: ScrimLogger = ScrimLogger()