from utils.timer import voiceactivity
import datetime as datetime
import json

def voicelog(before, after, member, path):
    dict = {}
    if not before.channel and after.channel:
        with open(str(path) + "voiceactivity.txt", "a") as a:
            dict['channel'] = f"{after.channel}"
            dict['username'] = f"{member}"
            dict['state'] = "joined"
            dict['time'] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            json.dump(dict, a)
            a.write("\n")
            a.close()
    if before.channel and not after.channel:
        with open(str(path) + "voiceactivity.txt", "a") as a:
            dict['channel'] = f"{before.channel}"
            dict['username'] = f"{member}"
            dict['state'] = "left"
            dict['time'] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            json.dump(dict, a)
            a.write("\n")
            a.close()
            return voiceactivity(member)
