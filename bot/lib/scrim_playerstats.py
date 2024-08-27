
from lib.DI_API_Obj.sweet_user import SweetUser
from lib.DI_API_Obj.gamemode import GameMode
from PIL import Image
from typing import Union, List, Tuple
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io



class ScrimPieCharts:
    @staticmethod
    def generate_agent_pickrate_pie_chart(user: SweetUser, gamemode: Union[GameMode, None] = None, season: int = None) -> Image:
        '''Generates a pie chart showing the agent pick rate for a specific gamemode and season. If no season is specified, uses lifetime stats.'''
        agent_stats = user.agent_stats
        agents: List[Tuple[str, int]] = []
        title: str = f"Agent Pick Rate for {user.display_name}"
        if gamemode is not None:
            match gamemode:
                case GameMode.SOLO:
                    title += " (Solo)"
                case GameMode.DUO:
                    title += " (Duo)"
                case GameMode.TRIO:
                    title += " (Trio)"
        if season is None:
            title += " (Lifetime)"
            for i in agent_stats.items():
                agents.append((i[0], i[1].lifetime_stats.get_pick_count(gamemode)))
        else:
            title += f" (Season {int(season)})"
            for i in agent_stats.items():
                if season not in i[1].seasonal_stats: # We don't record anything if there's no data for this agent this season
                    continue
                agents.append((i[0], i[1].seasonal_stats[season].get_pick_count(gamemode)))
        agents.sort(key=lambda x: x[1], reverse=True)
        # Remove any agents with 0 pick counts
        agents = [i for i in agents if i[1] > 0]
        agent_names = [i[0] for i in agents]
        agent_pick_counts = np.array([i[1] for i in agents])
        plt.title(title)
        plt.tight_layout()
        plt.pie(agent_pick_counts, labels=agent_names, startangle=0, autopct='%1.1f%%', pctdistance=0.85, labeldistance=1.1)
        
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        return Image.open(img_buf)
    
    @staticmethod
    def generate_gadget_pickrate_pie_chart(user: SweetUser, gamemode: Union[GameMode, None] = None, season: Union[int, None] = None) -> Image.Image:
        '''Generates a pie chart showing the gadget pick rate for a specific gamemode and season. If no season is specified, uses lifetime stats.
        ### Parameters
        * `user` - `SweetUser` - The SweetUser to generate the data from.
        * `gamemode` - `Union[Gamemode, None]` - Default `None` - The game mode (Solo/Duo/Trio) to generate stats for. If no game mode is specified, uses data from all game modes.
        * `season` - `Union[int, None]` - Default `None` - The season to generate stats for. If no season is supplied, uses lifetime stats.'''
        gadget_stats = user.gadget_stats
        gadgets: List[Tuple[str, int]] = []
        title: str = f"Gadget Pick Rate for {user.display_name}"
        if gamemode is not None:
            match gamemode:
                case GameMode.SOLO:
                    title += " (Solo)"
                case GameMode.DUO:
                    title += " (Duo)"
                case GameMode.TRIO:
                    title += " (Trio)"
        if season is None:
            title += " (Lifetime)"
            if "lifetime" not in gadget_stats:
                return None
            for i in gadget_stats.items():
                gadgets.append((i[0], i[1].lifetime_stats.get_number_of_picks(gamemode)))
        else:
            title += f" (Season {int(season)})"
            for i in gadget_stats.items():
                if season not in i[1].seasonal_stats:
                    continue
                gadgets.append((i[0], i[1].seasonal_stats[season].get_number_of_picks(gamemode)))
        gadgets.sort(key=lambda x: x[1], reverse=True)
        # Remove any gadgets with 0 pick rates
        gadgets = [i for i in gadgets if i[1] > 0]
        gadget_names = [i[0] for i in gadgets]
        gadget_pick_rates = np.array([i[1] for i in gadgets])
        plt.title(title)
        plt.tight_layout()
        plt.pie(gadget_pick_rates, labels=gadget_names, startangle=0, autopct='%1.1f%%', pctdistance=0.85, labeldistance=1.1)

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        return Image.open(img_buf)
            
class ScrimPlots:
    @staticmethod
    def calculate_agent_pickrates_over_seasons(sw: SweetUser, gamemode: Union[GameMode, None] = None) -> Image:
        '''Calculates the agent pick rates over all seasons for a specific gamemode. If no gamemode is supplied uses all gamemodes.'''
        pass
