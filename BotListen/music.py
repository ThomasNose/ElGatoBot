import yt_dlp
import asyncio
import discord

queues = {}
voice_clients = {}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

async def audio(message):
    channel = message.channel

    if message.content.startswith("?play"):
        try:
            voice_client = await message.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            # Already connected to voice channel
            print(e)
            await channel.send(content = "Song already playing.")

        try:
            url = message.content.split()[1]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            voice_clients[message.guild.id].play(player)
        except Exception as e:
            # Song already playing
            print(e)

    if message.content.startswith("?pause"):
        try:
            voice_clients[message.guild.id].pause()
        except Exception as e:
            print(e)

    if message.content.startswith("?resume"):
        try:
            voice_clients[message.guild.id].resume()
        except Exception as e:
            print(e)

    if message.content.startswith("?stop"):
        try:
            voice_clients[message.guild.id].stop()
            await voice_clients[message.guild.id].disconnect()
        except Exception as e:
            print(e)