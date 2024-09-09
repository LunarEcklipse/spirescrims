from typing import List, Union, Optional, Tuple
from collections import namedtuple

from lib.obj.scrim_format import ScrimFormat
from lib.obj.scrim_team import ScrimTeam
from lib.obj.scrim_user import ScrimUser
from lib.obj.scrim_matchgroups import ScrimMatchGroups



class ScrimMatchmaking:

    @staticmethod
    def average_lobbies(lobbies: List[int], min_groups_per_lobby: int, max_groups_per_lobby: int) -> List[int]:
        if min_groups_per_lobby == max_groups_per_lobby: # return early if the min and max are the same
            return lobbies
        # Get the number of lobbies with 6 or 8 players.
        num_small_lobbies = 0
        num_large_lobbies = 0
        for lobby in lobbies:
            if lobby == min_groups_per_lobby:
                num_small_lobbies += 1
            elif lobby == max_groups_per_lobby:
                num_large_lobbies += 1
        # If there is both at least one lobby with 6 players and one lobby with 8 players, we can take one player from each 8 player lobby and put it into a 6 player lobby to form a 7 player lobby.
        if num_small_lobbies > 0 and num_large_lobbies > 0:
            # Figure out the number of players that can be shifted based on the number of large lobbies or small lobbies, whichever there is less of.
            groups_available_for_shift = num_large_lobbies if num_large_lobbies <= num_small_lobbies else num_small_lobbies
            groups_allocated_for_shift = 0
            # Shift the players from the large lobbies to the small lobbies.
            for i in range(len(lobbies)):
                if groups_available_for_shift == 0:
                    break
                if lobbies[i] == max_groups_per_lobby:
                    lobbies[i] -= 1
                    groups_available_for_shift -= 1
                    groups_allocated_for_shift += 1
            for i in range(len(lobbies)):
                if groups_allocated_for_shift == 0:
                    break
                if lobbies[i] == min_groups_per_lobby:
                    lobbies[i] += 1
                    groups_allocated_for_shift -= 1
        return lobbies

    @staticmethod
    def calculate_lobby_sizes(num_groups: int, format: ScrimFormat, min_per_lobby: int = 0, max_per_lobby: int = 0) -> Optional[ScrimMatchGroups]:
        if min_per_lobby < max_per_lobby:
            return ValueError("Minimum per lobby cannot be greater than maximum per lobby.")
        min_groups_per_lobby, max_groups_per_lobby = None, None
        match format:
            case ScrimFormat.SOLO:
                min_groups_per_lobby, max_groups_per_lobby = 6, 8
            case ScrimFormat.DUO:
                min_groups_per_lobby, max_groups_per_lobby = 4, 6
            case ScrimFormat.TRIO:
                min_groups_per_lobby, max_groups_per_lobby = 3, 4
            case ScrimFormat.CUSTOM:
                min_groups_per_lobby = min_per_lobby if min_per_lobby is not None else 0
                max_groups_per_lobby = max_per_lobby if max_per_lobby is not None else 0
                        # Lobbies are a minimum of 6 players, maximum of 8. Try to capture as many players as possible, while making the lobbies as even as possible.
        if num_groups < min_groups_per_lobby:
            return None
        elif num_groups <= max_groups_per_lobby:
            return ScrimMatchGroups(format, [num_groups], 0)
        else:
            # First, try to make as many lobbies as possible of 8 players each
            lobbies = []
            while num_groups >= max_groups_per_lobby:
                lobbies.append(max_groups_per_lobby)
                num_groups -= max_groups_per_lobby
            # Determine how many players are left. If there are 6 or more, create a new lobby.
            if num_groups >= min_groups_per_lobby:
                lobbies.append(num_groups)
                num_groups = 0
            if num_groups == 0:
                return ScrimMatchGroups(format, ScrimMatchmaking.average_lobbies(lobbies, min_groups_per_lobby, max_groups_per_lobby), 0)
            # Check if we can pull players from other lobbies to create new lobbies to maximize the players playing.
            # First, if the minimum and maximum number of players per lobby is the same we can't do anything, so just return with what we have and waitlist everyone
            if min_groups_per_lobby == max_groups_per_lobby:
                return ScrimMatchGroups(format, lobbies, num_groups)
            potential_extra_groups = 0
            # Calculate how many players can be pulled from lobbies to form new ones if necessary.
            for lobby in lobbies:
                potential_extra_groups += lobby - min_groups_per_lobby
            # If when pulling players from lobbies we can form a new one with the waitlist players, do so.
            if potential_extra_groups + num_groups >= min_groups_per_lobby:
                needed_groups = min_groups_per_lobby - num_groups
                groups_pulled = 0
                # Generate a list of every number between min_groups_per_lobby + 1 and max_groups_per_lobby
                lobby_sizes_to_pull_from = list(range(min_groups_per_lobby + 1, max_groups_per_lobby + 1))
                lobby_sizes_to_pull_from.reverse()
                for size in lobby_sizes_to_pull_from:
                    for i in range(len(lobbies)):
                        if lobbies[i] == size:
                            lobbies[i] -= 1
                            groups_pulled += 1
                        if groups_pulled == needed_groups:
                            break
                    if groups_pulled == needed_groups:
                        break
                lobbies.append(needed_groups + num_groups)
                return ScrimMatchGroups(format, ScrimMatchmaking.average_lobbies(lobbies, min_groups_per_lobby, max_groups_per_lobby), 0)
            # If we can't form a new lobby, add the remaining players to the waitlist.
            return ScrimMatchGroups(format, ScrimMatchmaking.average_lobbies(lobbies, min_groups_per_lobby, max_groups_per_lobby), num_groups)
        return None
    