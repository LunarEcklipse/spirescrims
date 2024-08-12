import os, sys, easyocr, re
from typing import Union, List
from PIL import Image

reader: easyocr.Reader = easyocr.Reader(['en'])

def read_image(img_path: str) -> Union[List[str], str, None]:
    '''Reads text from an image using EasyOCR. Returns a list of strings.
    ### Parameters
    `img_path` : str - The path to the image file.'''
    try:
        img = Image.open(img_path)
        result = reader.readtext(img)
        out: list = []
        for detection in result:
            out.append(detection[1])
        return out
    except Exception as e:
        return None
    
class ScrimReader:
    @staticmethod
    def find_num_eliminations(text: Union[List[str], str, None]) -> Union[int, None]:
        '''Finds the number of eliminations in a list of strings.'''
        if text is None:
            return None
        # Create the regex pattern
        pattern = re.compile(r'(?i)([0-9]+) ?eliminations?')
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern.search(line)
            if match:
                # Get the number of eliminations on the front of the line
                return int(match.group(1))


    @staticmethod
    def find_num_field_upgrades(text: Union[List[str], str, None]) -> Union[int, None]:
        '''Finds the number of field upgrades in a list of strings.
        ### Parameters
        `text` : Union[List[str], str, None - The list of strings to search.'''
        if text is None:
            return None
        # Create the regex pattern
        pattern = re.compile(r'(?i)([0-9]+) ?field ?upgrades?')
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern.search(line)
            if match:
                # Get the number of field upgrades on the front of the line
                return int(match.group(1))
        return None
    
    @staticmethod
    def find_num_keycards(text: Union[List[str], str, None]) -> Union[int, None]:
        '''Finds the number of keycards in a list of strings.
        ### Parameters
        `text` : Union[List[str], str, None - The list of strings to search.'''
        if text is None:
            return None
        # Create the regex pattern
        pattern = re.compile(r'(?i)([0-9]+) ?keycards?')
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern.search(line)
            if match:
                # Get the number of keycards on the front of the line
                return int(match.group(1))
        return None

    @staticmethod
    def find_num_package(text: Union[List[str], str, None]) -> Union[int, None]:
        '''Finds the number of packages in a list of strings.
        ### Parameters
        `text` : Union[List[str], str, None - The list of strings to search.'''
        if text is None:
            return None
        # Create the regex pattern
        pattern = re.compile(r'(?i)([0-9]+) ?package?')
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern.search(line)
            if match:
                # Get the number of packages on the front of the line
                return int(match.group(1))
        return None

    @staticmethod
    def find_if_entered_vault(text: Union[List[str], str, None]) -> bool:
        '''Finds if the word "vault entered" is in a list of strings.
        ### Parameters
        `text` : Union[List[str], str, None - The list of strings to search.'''
        if text is None:
            return False
        # Create the regex pattern
        pattern = re.compile(r'(?i)vault ?entered')
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern.search(line)
            if match:
                return True
        return False
    
    @staticmethod
    def find_if_mission_ended(text:Union[List[str], str, None]) -> bool:
        '''Finds if the word "mission ended" is in a list of strings.
        ### Parameters
        `text` : Union[List[str], str, None - The list of strings to search.'''
        if text is None:
            return False
        # Create the regex pattern
        pattern = re.compile(r'(?i)mission ?ended')
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern.search(line)
            if match:
                return True
        return False

    @staticmethod
    def find_if_extracted(text: Union[List[str], str, None]) -> bool:
        '''Finds if the word "extracted" is in a list of strings.'''
        if text is None:
            return False
        # Create the regex pattern
        pattern = re.compile(r'(?i)extracted')
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern.search(line)
            if match:
                return True