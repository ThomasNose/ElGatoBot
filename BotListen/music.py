import yt_dlp
import asyncio
import discord

queues = {}
voice_clients = {}
yt_dl_options = {"format": "bestaudio/best", "noplaylist": False}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

queue = []

class audio():
    """
        This class supports the main commands for playing audio in discord voice chats.
    """
    
    async def play_audio(self, interaction, url):

        # This condition is for later checks to return the status of the player.
        if url == None:
            return(voice_clients[interaction.guild.id].is_playing())

        try:
            voice_client = await interaction.user.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

        except Exception as e:
            # Already connected to voice channel
            # This checks if a song is already playing and if so adds to the queue.
            if voice_clients[interaction.guild.id].is_playing():

                # Since the bot can be in multiple servers, I've changed this so the queue is a dictionary object.
                # This is important for now considering the bot is ran from one instance while in multiple discords.
                if f"{interaction.guild.id}" not in queues:
                    queues[f"{interaction.guild.id}"] = []
                    queues[f"{interaction.guild.id}"].append(url)
                else:
                    queues[f"{interaction.guild.id}"].append(url)
                msg = await interaction.response.send_message(content = "Added to queue.")
                return(voice_clients[interaction.guild.id].is_playing())
            print(e)

        try:

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
            voice_clients[interaction.guild.id].play(player)
            #if len(queue) < 1:
            if len(queues[f"{interaction.guild.id}"]) < 1:
                msg = await interaction.response.send_message(content = "Audio now playing.")
                return()

            #if len(queue) >= 1:
            if len(queues[f"{interaction.guild.id}"]) >= 1:

                # removing the song from queue
                queues[f"{interaction.guild.id}"].pop(0)
                msg = await interaction.response.send_message(content = "Audio skipped.")
                return()
            
        except Exception as e:
            # Song already playing
            msg = await interaction.response.send_message(content = "There was an exception.")
            print(e)
            return()

    async def pause_audio(interaction):
        try:
            voice_clients[interaction.guild.id].pause()
            return(await interaction.response.send_message(content = "Audio paused."))
        except Exception as e:
            print(e)
            return(await interaction.response.send_message(content = "Error pausing."))

    async def resume_audio(interaction):
        try:
            voice_clients[interaction.guild.id].resume()
            return(await interaction.response.send_message(content = "Audio resumed."))
        except Exception as e:
            print(e)
            return(await interaction.response.send_message(content = "Error resuming"))

    async def audio_disconnect(interaction):
        try:
            voice_clients[interaction.guild.id].stop()
            await voice_clients[interaction.guild.id].disconnect()
            return(await interaction.response.send_message(content = "Bot disconnected."))
        except Exception as e:
            print(e)
            return(await interaction.response.send_message(content = "Error disconnecting"))
        
    async def audio_skip(self, interaction):
        try:
            # When the queue >= 1 then we skip and move on to the next queue item.
            if len(queues[f"{interaction.guild.id}"]) >= 1:
                voice_clients[interaction.guild.id].stop()
                playing = await self.play_audio(interaction, queues[f"{interaction.guild.id}"][0])
                return()
            # When the queue isn't >= 1 then the queue is empty and a single audio was playing so we
            # stop the player like normal but don't recall the play_audio function.
            else:
                # This condition is required to know if there's anything playing currently and thus
                # anything possible to skip, if not we just return "Nothing to skip.".
                playing = await self.play_audio(interaction, None)
                if playing == True:
                    voice_clients[interaction.guild.id].stop()
                    msg = await interaction.response.send_message(content = "Audio skipped.")
                else:
                    msg = await interaction.response.send_message(content = "Nothing to skip.")
                return()

        except Exception as e:
            print(e)
            return(await interaction.response.send_message(content = "Error skipping."))