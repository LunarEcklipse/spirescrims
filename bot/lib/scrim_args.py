import argparse
from enum import StrEnum

class ScrimArgs:
    _args: argparse.Namespace = None
    log_level: str = None
    disable_reader: bool = None
    num_reader_threads: int = None
    reader_cpu_only: bool = None

    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="ScrimBot")
        parser.add_argument("--log-level", type=str, default="INFO", help="The logging level to use. Options are: DEBUG, INFO, WARNING, ERROR, CRITICAL.")
        parser.add_argument("--disable-reader", action="store_true", help="Disables OCR reader functionality. Useful for systems that can not run the reader.")
        parser.add_argument("--num-reader-threads", type=int, default=8, help="The number of OCR reader threads to use for reading images. Lower this if performance is poor.")
        parser.add_argument("--reader-cpu-only", action="store_true", help="Disables the use of the GPU for OCR reading. Useful for systems that can not run the reader.")
        return parser.parse_args()
    
    def __init__(self):
        self._args = self.parse_args()
        self.log_level = self._args.log_level
        self.disable_reader = self._args.disable_reader
        self.num_reader_threads = self._args.num_reader_threads
        self.reader_cpu_only = self._args.reader_cpu_only