import os, sys, io, easyocr, re, warnings
from typing import Union, List
from PIL import Image
import discord
from discord.ext import commands
import lib.scrim_sysinfo as scrim_sysinfo

channel_id_list: List[int] = [1224071523187425320, 1256544655072428113, 1224071542854516739] # Add your channel IDs here
warnings.filterwarnings("ignore", category=FutureWarning, module="easyocr")

class MatchScore:
    total_score: int
    rationale: List[str]

    def __init__(self, total_score: int, rationale: List[str]):
        self.total_score = total_score
        self.rationale = rationale

    def __str__(self):
        return f'{str(self.total_score)}\n### Rationale\n* {"\n* ".join(self.rationale)}'

class ScrimReader(commands.Cog):
    reader: easyocr.Reader
    bot: discord.Bot

    def __init__(self, bot: discord.Bot):
        self.reader = easyocr.Reader(['en'], verbose=False, gpu=scrim_sysinfo.system_has_gpu())
        self.bot = bot

    ### READER FUNCTIONS ###

    def read_image(self, image_bytes: bytes) -> Union[List[str], str, None]:
        '''Reads text from an image using EasyOCR. Returns a list of strings.
        ### Parameters
        `image_bytes` : bytes - The image data in bytes.'''
        img = Image.open(io.BytesIO(image_bytes))
        # Check if the image is larger than 480 pixels on its shortest side. If it is, resize it.
        img = self._resize_image_shortest_side(img, 720)
        # Save the resized image to a BytesIO buffer
        image_buffer = io.BytesIO()
        img.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        # Read text from the image bytes
        result = self.reader.readtext(image_buffer.getvalue())
        out: list = []
        for detection in result:
            out.append(detection[1])
        return out

    def _resize_image_shortest_side(self, img: Image, size: int) -> Image:
        '''Resizes an image so that the shortest side is a certain size.
        ### Parameters
        `img` : Image - The image to resize.
        `size` : int - The size of the shortest side.'''
        if min(img.size) <= size:
            return img
        width, height = img.size
        if width < height:
            ratio = size / width
            new_width = size
            new_height = int(height * ratio)
        else:
            ratio = size / height
            new_height = size
            new_width = int(width * ratio)
        return img.resize((new_width, new_height))

    def _find_num_eliminations(self, text: Union[List[str], str, None]) -> Union[int, None]:
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
        # If we make it here, check for the word "eliminations = X" in the text. We want to capture the X.
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = re.search(r'(?i)eliminations? ?= ([0-9]+)', line)
            if match:
                # Get the number of eliminations on the back of the line. When we do it this way, we calculate by score instead and divide by 100.
                return int(int(match.group(1)) / 100)
        return None

    def _find_if_entered_vault(self, text: Union[List[str], str, None]) -> bool:
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

    def _find_num_vault_terminals_disabled(self, text: Union[List[str], str, None]) -> Union[int, None]:
        '''Finds the number of vault terminals disabled in a list of strings.
        ### Parameters
        `text` : Union[List[str], str, None - The list of strings to search.'''
        if text is None:
            return None
        # Create the regex pattern
        pattern = re.compile(r'(?i)([0-9]+) ?vault ?terminals? ?disabled')
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern.search(line)
            if match:
                # Get the number of vault terminals disabled on the front of the line
                return int(match.group(1))
        return None

    def _find_last_spy_standing(self, text: Union[List[str], str, None]) -> bool:
        '''Finds if the word "last spy standing" is in a list of strings.
        ### Parameters
        `text` : Union[List[str], str, None - The list of strings to search.'''
        if text is None:
            return False
        # Create the regex pattern
        pattern = re.compile(r'(?i)last ?spy ?standing')
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
    
    def _find_if_extracted(self, text: Union[List[str], str, None]) -> bool:
        '''Finds if the word "extracted" is in a list of strings.
        ### Parameters
        `text` : Union[List[str], str, None - The list of strings to search.'''
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
        return False

    def _find_num_allies_revived(self, text: Union[List[str], str, None]) -> Union[int, None]:
        '''Finds the number of allies revived in a list of strings.
        ### Parameters
        `text` : Union[List[str], str, None - The list of strings to search.'''
        if text is None:
            return None
        # Create the regex pattern
        pattern = re.compile(r'(?i)([0-9]+) ?ally ?revived')
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern.search(line)
            if match:
                # Get the number of allies revived on the front of the line
                return int(match.group(1))
        return None
    
    def calculate_score_from_image(self, image_bytes: bytes) -> Union[MatchScore, None]:
        '''Calculates the score from an image of the scoreboard.'''
        text = self.read_image(image_bytes)
        eliminations = self._find_num_eliminations(text)
        vault_entered = self._find_if_entered_vault(text)
        vault_terminals_disabled = self._find_num_vault_terminals_disabled(text)
        last_spy_standing = self._find_last_spy_standing(text)
        extracted = self._find_if_extracted(text)
        allies_revived = self._find_num_allies_revived(text)
        score = 0
        rationale_list = []
        if eliminations is not None:
            score += eliminations
            rationale_list.append(f'{str(eliminations)} Eliminations: {str(eliminations)}')
        if vault_entered:
            score += 1
            rationale_list.append('Vault Entered: 1')
        if vault_terminals_disabled is not None:
            score += vault_terminals_disabled
            rationale_list.append(f'{str(vault_terminals_disabled)} Vault Terminals Disabled: {str(vault_terminals_disabled)}')
        if last_spy_standing:
            score += 4
            rationale_list.append('Last Spy Standing: 4')
        if extracted:
            score += 4
            rationale_list.append('Extracted: 4')
        if allies_revived is not None:
            score -= allies_revived
            rationale_list.append(f'{str(allies_revived)} Allies Revived: -{str(allies_revived)}')
        return MatchScore(score, rationale_list)
    
    ### LISTENERS ###
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Check if the channel is in the list of channels
        if message.channel.id not in channel_id_list:
            return
        if len(message.attachments) > 0:
            message_handle: discord.Message = await message.reply('Processing image, please wait...')
            for attachment in message.attachments:
                if attachment.content_type.startswith('image'):
                    score = self.calculate_score_from_image(await attachment.read())
                    await message_handle.edit(f'**Estimated Match Score:** {str(score)}')