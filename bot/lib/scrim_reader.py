import os, sys, io, easyocr, re, warnings
from typing import Union, List
from datetime import datetime, timedelta
from PIL import Image
import discord
from discord.ext import commands
import lib.scrim_sysinfo as scrim_sysinfo

channel_id_list: List[int] = [1224071523187425320, 1256544655072428113, 1224071542854516739] # Add your channel IDs here
warnings.filterwarnings("ignore", category=FutureWarning, module="easyocr")

class MatchScore:
    total_score: int
    eliminations: int
    vault_terminals_disabled: int
    allies_revived: int
    vault_entered: bool
    last_spy_standing: bool
    extracted: bool

    def __init__(self,
                 total_score: int,
                 eliminations: Union[int, None] = 0,
                 vault_terminals_disabled: Union[int, None] = 0,
                 allies_revived: Union[int, None] = 0,
                 vault_entered: bool = False,
                 last_spy_standing: bool = False,
                 extracted: bool = False):
        self.total_score = total_score
        self.eliminations = eliminations if eliminations is not None else 0
        self.vault_terminals_disabled = vault_terminals_disabled if vault_terminals_disabled is not None else 0
        self.allies_revived = allies_revived if allies_revived is not None else 0
        self.vault_entered = vault_entered
        self.last_spy_standing = last_spy_standing
        self.extracted = extracted

    def _get_elimination_score(self) -> Union[str, None]:
        match eliminations:
            case 0:
                return None
            case 1:
                return '1 Elimination: 1'
            case _:
                return f'{self.eliminations} Eliminations: {self.eliminations}'
    
    def _get_vault_entered_score(self) -> Union[str, None]:
        return 'Vault Entered: 1' if self.vault_entered else None
    
    def _print_vault_terminals_disabled_score(self) -> Union[str, None]:
        match vault_terminals_disabled:
            case 0:
                return None
            case 1:
                return '1 Vault Terminal Disabled: 1'
            case _:
                return f'{self.vault_terminals_disabled} Vault Terminals Disabled: {self.vault_terminals_disabled}'

    def _print_allies_revived_score(self) -> Union[str, None]:
        match allies_revived:
            case 0:
                return None
            case 1:
                return '1 Ally Revived: -1'
            case _:
                return f'{self.allies_revived} Allies Revived: -{self.allies_revived}'

    def _print_last_spy_standing_score(self) -> Union[str, None]:
        return 'Last Spy Standing: 4' if self.last_spy_standing else None

    def _print_extracted_score(self) -> Union[str, None]:
        return 'Extracted: 4' if self.extracted else None

    def __str__(self) -> str:
        out = f"**Estimated Score:** {self.total_score}"
        if self.score == 0 and self.allies_revived == 0:
            return out
        out += "\n## Rationale\n"
        if self.eliminations > 0:
            out += f"* {self._get_elimination_score()}\n"
        if self.vault_entered:
            out += f"* {self._get_vault_entered_score()}\n"
        if self.vault_terminals_disabled > 0:
            out += f"* {self._print_vault_terminals_disabled_score()}\n"
        if self.allies_revived > 0:
            out += f"* {self._print_allies_revived_score()}\n"
        if self.last_spy_standing:
            out += f"* {self._print_last_spy_standing_score()}\n"
        if self.extracted:
            out += f"* {self._print_extracted_score()}\n"
        return out

    def create_embed(self, image_url: Union[str, None] = None) -> discord.Embed:
        emb = discord.Embed(title=f"Estimated Score: {self.total_score}", color=0x8000ff, timestamp=datetime.now())
        emb.set_author(name="Scoreboard Analysis")
        embed_str: str = ""
        if self.eliminations > 0:
            embed_str += f"* {self._get_elimination_score()}\n"
        if self.vault_entered:
            embed_str += f"* {self._get_vault_entered_score()}\n"
        if self.vault_terminals_disabled > 0:
            embed_str += f"* {self._print_vault_terminals_disabled_score()}\n"
        if self.allies_revived > 0:
            embed_str += f"* {self._print_allies_revived_score()}\n"
        if self.last_spy_standing:
            embed_str += f"* {self._print_last_spy_standing_score()}\n"
        if self.extracted:
            embed_str += f"* {self._print_extracted_score()}\n"
        emb.add_field(name = "**Rationale**", value=embed_str)
        if image_url is not None:
            emb.set_image(url=image_url)
        emb.set_footer(text="Calculated by Scrims Helper")
        return emb
        


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
        match_score = MatchScore(0)
        if eliminations is not None:
            match_score.total_score += eliminations
            match_score.eliminations = eliminations
        if vault_entered:
            match_score.total_score += 1
            match_score.vault_entered = True
        if vault_terminals_disabled is not None:
            match_score.total_score += vault_terminals_disabled
            match_score.vault_terminals_disabled = vault_terminals_disabled
        if last_spy_standing:
            match_score.total_score += 4
            match_score.last_spy_standing = True
        if extracted:
            match_score.total_score += 4
            match_score.extracted = True
        if allies_revived is not None:
            match_score.total_score -= allies_revived
            match_score.allies_revived = allies_revived
        return match_score
    
    ### LISTENERS ###
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Check if the channel is in the list of channels
        if message.channel.id not in channel_id_list:
            return
        if message.author.bot:
            return
        if len(message.attachments) > 0:
            if len(message.attachments) > 1:
                await message.reply('Please only attach one image at a time.')
                return
            calculation_start: datetime = datetime.now()
            message_handle: discord.Message = await message.reply('Processing image, please wait...')
            for attachment in message.attachments:
                if attachment.content_type.startswith('image'):
                    score = self.calculate_score_from_image(await attachment.read())
                    calculation_time: timedelta = datetime.now() - calculation_start
                    await message_handle.edit(content=f'Calculation took {calculation_time.total_seconds()} seconds.', embed=score.create_embed(attachment.url))
                    return

