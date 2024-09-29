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
    if track[horse_index - 1] == " " and random.choice([0, 1]):
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


class horse_race(discord.ui.View):
    def __init__(self, interaction):
        self.interaction = interaction

        # Track layout, extra space for 1 because it looks weird otherwise
        # The only variable that impacts the length they "run" is the 80 * " "
        # so regardless of how it looks, they're all even
        self.track_top = "**=========================================**"
        self.track_1 = "**1  |**" + 80 * " " + ":horse_racing:"
        self.track_2 = "**2 |**" + 80 * " " + ":horse_racing:"
        self.track_3 = "**3 |**" + 80 * " " + ":horse_racing:"
        self.track_4 = "**4 |**" + 80 * " " + ":horse_racing:"
        self.track_5 = "**5 |**" + 80 * " " + ":horse_racing:"
        self.track_6 = "**6 |**" + 80 * " " + ":horse_racing:"
        self.track_bottom = "**=========================================**"

        self.track_pos = {"1":None,
                          "2": None,
                          "3": None,
                          "4": None,
                          "5": None,
                          "6": None,
                          "pos": 1}

        self.tracks = [self.track_1, self.track_2, self.track_3, self.track_4, self.track_5, self.track_6]
    
    async def start_race(self):

        await self.interaction.response.send_message(content="Race starting in 5 seconds.")
        self.message = await self.interaction.original_response()
        await asyncio.sleep(5)


        start_time = asyncio.get_event_loop().time()

        # While any track has space before the horse
        while any(" " in self.track.split(":horse_racing:")[0] for self.track in self.tracks):
            # Shuffle the indices for moving the horses
            shuffled_indices = random.sample(range(len(self.tracks)), len(self.tracks))

            # Move each horse randomly based on shuffled indices
            for i in shuffled_indices:
                self.tracks[i] = move_horse(self, i, self.tracks[i], start_time)
            
            # Update each track variable
            track_1, track_2, track_3, track_4, track_5, track_6 = self.tracks
            
            # Display the updated race track
            self.race = race_status(self.track_top, self.track_bottom, self.track_pos, *self.tracks)

            try:
                await self.message.edit(content=self.race)
            except Exception as e:
                print(f"Error sending/updating the message: {e}")
            

            # Sleep to simulate the passage of time
            await asyncio.sleep(0.2)
        
        # Final update as previously last place wasn't being recorded.
        self.tracks = [move_horse(self, num, self.track) for num, self.track in enumerate(self.tracks)]
        track_1, track_2, track_3, track_4, track_5, track_6 = self.tracks
        self.race = race_status(self.track_top, self.track_bottom, self.track_pos, *self.tracks)
        try:
            await self.message.edit(content=self.race)
        except Exception as e:
            print(f"Error sending/updating the message: {e}")