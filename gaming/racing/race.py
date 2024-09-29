import random
import asyncio
import discord


# Function to remove a single space based on random movement (0 or 1 space per iteration)
def move_horse(self, num, track, start):

    place_map = {"1": "1st",
                 "2": "2nd",
                 "3": "3rd",
                 "4": "4th",
                 "5": "5th",
                 "6": "6th"}

    # Find the position of the ":horse_racing:" emoji
    horse_index = track.index(":horse_racing:")
    
    # Randomly decide if the horse moves or stays in place (0: no move, 1: move forward)
    if track[horse_index - 1] == "\u2003" and random.choice([0, 1]):
        track = track[:horse_index - 1] + track[horse_index:]  # Remove one space

    # Now if the horse finished, what position
    if track[horse_index - 1] == "*" and self.track_pos[str(num+1)] == None:
        self.track_pos[str(num+1)] = place_map[str(self.track_pos["pos"])] + f" - {round(asyncio.get_event_loop().time() - start, 2)}s"
        self.track_pos["pos"] += 1
    return track

# Function to display the race track with horses
def race_status(track_top, track_bottom, pos, *tracks):
    race = track_top + " \n" \
            + tracks[0] + f" {pos['1'] if pos['1'] else ''}" + " \n" \
            + tracks[1] + f" {pos['2'] if pos['2'] else ''}" + " \n" \
            + tracks[2] + f" {pos['3'] if pos['3'] else ''}" + " \n" \
            + tracks[3] + f" {pos['4'] if pos['4'] else ''}" + " \n" \
            + tracks[4] + f" {pos['5'] if pos['5'] else ''}" + " \n" \
            + tracks[5] + f" {pos['6'] if pos['6'] else ''}" + " \n" \
            + track_bottom

    return(race)