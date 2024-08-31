import os, sys, io, easyocr, re, warnings, multiprocessing
from typing import Union, List
from datetime import datetime, timedelta
from threading import Thread
from PIL import Image
from queue import Queue
import discord
from discord.ext import commands, tasks
import lib.scrim_sysinfo as scrim_sysinfo

channel_id_list: List[int] = [1224071523187425320, 1256544655072428113, 1224071542854516739, 1266861462085959800] # Add your channel IDs here
warnings.filterwarnings("ignore", category=FutureWarning, module="easyocr")

class MatchScore:
    total_score: int
    eliminations: int
    eliminations_known: bool
    vault_terminals_disabled: int
    terminals_disabled_known: bool
    allies_revived: int
    allies_revived_known: bool
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
        self.eliminations_known = False if self.eliminations == -1 else True
        self.vault_terminals_disabled = vault_terminals_disabled if vault_terminals_disabled is not None else 0
        self.terminals_disabled_known = False if self.vault_terminals_disabled == -1 else True
        self.allies_revived = allies_revived if allies_revived is not None else 0
        self.allies_revived_known = False if self.allies_revived == -1 else True
        self.vault_entered = vault_entered
        self.last_spy_standing = last_spy_standing
        self.extracted = extracted

    def is_score_uncertain(self) -> bool:
        '''Returns whether the score is uncertain.'''
        return not self.eliminations_known or not self.terminals_disabled_known or not self.allies_revived_known

    def _get_elimination_score_formatted(self) -> Union[str, None]:
        '''Returns the Elimination score as a formatted string.'''
        match self.eliminations:
            case 0:
                return None
            case -1:
                return 'Unknown Eliminations: ?'
            case 1:
                return '1 Elimination: 1'
            case _:
                return f'{self.eliminations} Eliminations: {self.eliminations}'
    
    def _get_vault_entered_score_formatted(self) -> Union[str, None]:
        '''Returns the Vault Entered score as a formatted string.'''
        return 'Vault Entered: 1' if self.vault_entered else None
    
    def _get_vault_terminals_disabled_score_formatted(self) -> Union[str, None]:
        '''Returns the Vault Terminals Disabled score as a formatted string.'''
        match self.vault_terminals_disabled:
            case 0:
                return None
            case -1:
                return 'Unknown Vault Terminals Disabled: ?'
            case 1:
                return '1 Vault Terminal Disabled: 1'
            case _:
                return f'{self.vault_terminals_disabled} Vault Terminals Disabled: {self.vault_terminals_disabled}'

    def _get_allies_revived_score_formatted(self) -> Union[str, None]:
        '''Returns the Allies Revived score as a formatted string.'''
        match self.allies_revived:
            case 0:
                return None
            case -1:
                return 'Unknown Allies Revived: ?'
            case 1:
                return '1 Ally Revived: -1'
            case _:
                return f'{self.allies_revived} Allies Revived: -{self.allies_revived}'

    def _get_last_spy_standing_score_formatted(self) -> Union[str, None]:
        '''Returns the Last Spy Standing score as a formatted string.'''
        return 'Last Spy Standing: 4' if self.last_spy_standing else None

    def _print_extracted_score(self) -> Union[str, None]:
        '''Returns the Extracted score as a formatted string.'''
        return 'Extracted: 4' if self.extracted else None

    def has_no_score_events(self) -> bool:
        '''Returns whether the MatchScore has no score-affecting events.'''
        return self.eliminations == 0 and self.vault_terminals_disabled == 0 and self.allies_revived == 0 and not self.vault_entered and not self.last_spy_standing and not self.extract
    
    def __repr__(self) -> str:
        return f"MatchScore(total_score={self.total_score}, eliminations={self.eliminations}, vault_terminals_disabled={self.vault_terminals_disabled}, allies_revived={self.allies_revived}, vault_entered={self.vault_entered}, last_spy_standing={self.last_spy_standing}, extracted={self.extracted})"
    
    def __str__(self) -> str:
        out = f"**Estimated Score:** {self.total_score}"
        if self.is_score_uncertain():
            out += " (**Score is Uncertain: See Below**)"
        if self.has_no_score_events():
            return out
        out += "\n## Rationale\n"
        if self.eliminations > 0:
            out += f"* {self._get_elimination_score_formatted()}\n"
        if self.vault_entered:
            out += f"* {self._get_vault_entered_score_formatted()}\n"
        if self.vault_terminals_disabled > 0:
            out += f"* {self._get_vault_terminals_disabled_score_formatted()}\n"
        if self.allies_revived > 0:
            out += f"* {self._get_allies_revived_score_formatted()}\n"
        if self.last_spy_standing:
            out += f"* {self._get_last_spy_standing_score_formatted()}\n"
        if self.extracted:
            out += f"* {self._print_extracted_score()}\n"
        return out

    def create_embed(self, image_url: Union[str, None] = None) -> discord.Embed:
        emb: discord.Embed = discord.Embed(title=f"Estimated Score: {self.total_score}", color=0x8000ff, timestamp=datetime.now())
        emb.description = "**NOTE: Score Is Uncertain! Please Manually Verify Results!**" if self.is_score_uncertain() else ""
        emb.set_author(name="Scoreboard Analysis")
        embed_str: str = ""
        if self.eliminations != 0:
            embed_str += f"* {self._get_elimination_score_formatted()}\n"
        if self.vault_entered:
            embed_str += f"* {self._get_vault_entered_score_formatted()}\n"
        if self.vault_terminals_disabled != 0:
            embed_str += f"* {self._get_vault_terminals_disabled_score_formatted()}\n"
        if self.allies_revived != 0:
            embed_str += f"* {self._get_allies_revived_score_formatted()}\n"
        if self.last_spy_standing:
            embed_str += f"* {self._get_last_spy_standing_score_formatted()}\n"
        if self.extracted:
            embed_str += f"* {self._print_extracted_score()}\n"
        if self.has_no_score_events() == False:
            emb.add_field(name = "**Rationale**", value=embed_str)
        if image_url is not None:
            emb.set_image(url=image_url)
        emb.set_footer(text="Calculated by Scrims Helper")
        return emb
        
class ImageProcessTask:
    image: Image
    message: discord.Message
    attachment_url: str
    score: MatchScore

    def __init__(self, image: Image, message: discord.Message, attachment_url: Union[str, None] = None):
        self.image = image if type(image) == Image else Image.open(io.BytesIO(image))
        self.message = message
        self.score = MatchScore(0)
        self.attachment_url = attachment_url

    async def edit_message(self, content: str, embed: discord.Embed):
        await self.message.edit(content=content, embed=embed)

class OCRReaderProcess:
    reader: easyocr.Reader
    read_queue: Queue
    results_queue: Queue
    thread: Thread
    thread_name: str
    ocr_ready: bool

    def __init__(self, read_queue: Queue, results_queue: Queue, thread_name: str):
        self.read_queue = read_queue
        self.results_queue = results_queue
        self.thread_name = thread_name
        self.ocr_ready = False
        self.thread = Thread(target=self._read_image_process, name=self.thread_name)
        self.thread.start()

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
        pattern1 = re.compile(r'(?i)([0-9IiOo]+) ?eliminations?')
        pattern2 = re.compile(r'eliminations?') # We assume 1 here, this is a last ditch backup effort
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern1.search(line)
            if match:
                # Get the number of eliminations on the front of the line
                return int(match.group(1).lower().translate(str.maketrans("IiOo", "1100"))) # Convert all I's to 1's and O's to 0's
            match = pattern2.search(line) # If we reach here, we can't read the number and thus should report -1 to indicate an unknown result.
            if match:
                return -1
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
        pattern1 = re.compile(r'(?i)([0-9IiOo]+) ?vault ?terminals? ?disabled')
        pattern2 = re.compile(r'vault ?terminals? ?disabled') # Our backup regex
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern1.search(line)
            if match:
                # Get the number of vault terminals disabled on the front of the line
                return int(match.group(1).lower().translate(str.maketrans("IiOo", "1100"))) # Convert all I's to 1's and O's to 0's
            match = pattern2.search(line) # Backup, report unknown
            if match:
                return -1
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
        `text` : `Union[List[str], str, None]` - The list of strings to search.'''
        if text is None:
            return None
        # Create the regex pattern
        pattern1 = re.compile(r'(?i)([0-9IiOo]+) ?ally ?revived')
        pattern2 = re.compile(r'ally ?revived') # Our backup regex
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern1.search(line)
            if match:
                # Get the number of allies revived on the front of the line
                return int(match.group(1).lower().translate(str.maketrans("IiOo", "1100"))) # Convert all I's to 1's and O's to 0's
            match = pattern2.search(line) # Backup, report unknown
            if match:
                return -1
        return None
    
    def _calculate_score_from_text(self, text: List[str]) -> MatchScore:
        '''Calculates the score from a list of strings.'''
        eliminations = self._find_num_eliminations(text)
        vault_entered = self._find_if_entered_vault(text)
        vault_terminals_disabled = self._find_num_vault_terminals_disabled(text)
        last_spy_standing = self._find_last_spy_standing(text)
        extracted = self._find_if_extracted(text)
        allies_revived = self._find_num_allies_revived(text)
        match_score = MatchScore(0)
        if eliminations is not None:
            match_score.total_score += eliminations if eliminations != -1 else 0
            match_score.eliminations = eliminations
            match_score.eliminations_known = True if eliminations != -1 else False
        if vault_entered:
            match_score.total_score += 1
            match_score.vault_entered = True
        if vault_terminals_disabled is not None:
            match_score.total_score += vault_terminals_disabled if vault_terminals_disabled != -1 else 0
            match_score.vault_terminals_disabled = vault_terminals_disabled
            match_score.terminals_disabled_known = True if vault_terminals_disabled != -1 else False
        if last_spy_standing:
            match_score.total_score += 4
            match_score.last_spy_standing = True
        if extracted:
            match_score.total_score += 4
            match_score.extracted = True
        if allies_revived is not None:
            match_score.total_score -= allies_revived if allies_revived != -1 else 0
            match_score.allies_revived = allies_revived
            match_score.allies_revived_known = True if allies_revived != -1 else False
        return match_score

    def _read_image_process(self):
        self.reader = easyocr.Reader(['en'], verbose=False, gpu=scrim_sysinfo.system_has_gpu())
        self.ocr_ready = True
        try:
            while True:
                image_task: ImageProcessTask = self.read_queue.get(block=True) # Wait until an image becomes available for the processor
                image_task.image = self._resize_image_shortest_side(image_task.image, 720)
                image_buffer = io.BytesIO()
                image_task.image.save(image_buffer, format='PNG')
                image_buffer.seek(0)
                result = self.reader.readtext(image_buffer.getvalue())
                raw_result: list = []
                for detection in result:
                    raw_result.append(detection[1])
                image_task.score = self._calculate_score_from_text(raw_result)
                self.results_queue.put(image_task)
        except Exception as e:
            ocr_ready = False
            print(e)

class ScrimReader(commands.Cog):
    bot: discord.Bot
    reader_processes: List[OCRReaderProcess]
    read_queue: Queue
    results_queue: Queue
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.read_queue, self.results_queue = Queue(), Queue()
        self.reader_processes = [] # List of reader processes - This needs to be initialized in __main__ to avoid issues with forking
        self.spawn_processes()

    def cog_unload(self):
        for p in self.reader_processes:
            p.terminate()
            p.join()

    def spawn_processes(self, num_ocr_processes: int = 8):
        for i in range(num_ocr_processes):
            self.reader_processes.append(OCRReaderProcess(self.read_queue, self.results_queue, f"OCRReaderProcess_{i}"))

    ### READER FUNCTIONS ###

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
        pattern1 = re.compile(r'(?i)([0-9IiOo]+) ?eliminations?')
        pattern2 = re.compile(r'eliminations?') # We assume 1 here, this is a last ditch backup effort
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern1.search(line)
            if match:
                # Get the number of eliminations on the front of the line
                return int(match.group(1).lower().translate(str.maketrans("IiOo", "1100"))) # Convert all I's to 1's and O's to 0's
            match = pattern2.search(line) # If we reach here, we can't read the number and thus should report -1 to indicate an unknown result.
            if match:
                return -1
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
        pattern1 = re.compile(r'(?i)([0-9IiOo]+) ?vault ?terminals? ?disabled')
        pattern2 = re.compile(r'vault ?terminals? ?disabled') # Our backup regex
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern1.search(line)
            if match:
                # Get the number of vault terminals disabled on the front of the line
                return int(match.group(1).lower().translate(str.maketrans("IiOo", "1100"))) # Convert all I's to 1's and O's to 0's
            match = pattern2.search(line) # Backup, report unknown
            if match:
                return -1
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
        `text` : `Union[List[str], str, None]` - The list of strings to search.'''
        if text is None:
            return None
        # Create the regex pattern
        pattern1 = re.compile(r'(?i)([0-9IiOo]+) ?ally ?revived')
        pattern2 = re.compile(r'ally ?revived') # Our backup regex
        if type(text) == str:
            text = [text]
        for line in text:
            # First make line lowercase
            line = line.lower()
            # Search for the pattern
            match = pattern1.search(line)
            if match:
                # Get the number of allies revived on the front of the line
                return int(match.group(1).lower().translate(str.maketrans("IiOo", "1100"))) # Convert all I's to 1's and O's to 0's
            match = pattern2.search(line) # Backup, report unknown
            if match:
                return -1
        return None
    
    def _calculate_score_from_text(self, text: List[str]) -> MatchScore:
        '''Calculates the score from a list of strings.'''
        eliminations = self._find_num_eliminations(text)
        vault_entered = self._find_if_entered_vault(text)
        vault_terminals_disabled = self._find_num_vault_terminals_disabled(text)
        last_spy_standing = self._find_last_spy_standing(text)
        extracted = self._find_if_extracted(text)
        allies_revived = self._find_num_allies_revived(text)
        match_score = MatchScore(0)
        if eliminations is not None:
            match_score.total_score += eliminations if eliminations != -1 else 0
            match_score.eliminations = eliminations
            match_score.eliminations_known = True if eliminations != -1 else False
        if vault_entered:
            match_score.total_score += 1
            match_score.vault_entered = True
        if vault_terminals_disabled is not None:
            match_score.total_score += vault_terminals_disabled if vault_terminals_disabled != -1 else 0
            match_score.vault_terminals_disabled = vault_terminals_disabled
            match_score.terminals_disabled_known = True if vault_terminals_disabled != -1 else False
        if last_spy_standing:
            match_score.total_score += 4
            match_score.last_spy_standing = True
        if extracted:
            match_score.total_score += 4
            match_score.extracted = True
        if allies_revived is not None:
            match_score.total_score -= allies_revived if allies_revived != -1 else 0
            match_score.allies_revived = allies_revived
            match_score.allies_revived_known = True if allies_revived != -1 else False
        return match_score
    
    ### LISTENERS ###
    @commands.Cog.listener()
    async def on_ready(self):
        self.check_for_results.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Check if the channel is in the list of channels
        if message.channel.id not in channel_id_list:
            return
        if message.author.bot:
            return
        if len(message.attachments) > 0:
            for attachment in message.attachments:
                if attachment.content_type.startswith('image'):
                    message_handle: discord.Message = await message.reply('Processing image, please wait...')
                    self.read_queue.put(ImageProcessTask(await attachment.read(), message_handle, attachment.url))
            return

    @tasks.loop(seconds=1)
    async def check_for_results(self):
        while not self.results_queue.empty():
            task: ImageProcessTask = self.results_queue.get()
            await task.edit_message("", task.score.create_embed(task.attachment_url))