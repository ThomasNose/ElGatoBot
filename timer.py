import json
from datetime import datetime


def format_seconds(seconds):
    # Calculate days, hours, minutes, and remaining seconds
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    # Format the result
    formatted_time = f"{int(days):02}:{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    return formatted_time

def voiceactivity(name):

    data = []
    Total = 0
    with open(f"logs/{name}/voiceactivity.txt", 'r') as file:
        for line in file:
            data.append(json.loads(line))

        even = None
        odd = None

    file.close()

    for i in range(len(data)):
        if (i % 2) == 0:
            even = data[i]
            joined = datetime.strptime(even["time"], '%Y-%m-%d %H:%M:%S')
        if (i % 2) != 0:
            odd = data[i]
            left = datetime.strptime(odd["time"], '%Y-%m-%d %H:%M:%S')
        if even is not None and odd is not None:
            difference = joined - left
            Total += int(abs(difference.total_seconds()))
            even = None
            odd = None

    Total = format_seconds(Total)
    with open(f"logs/{name}/TotalVoiceTime.txt", 'w') as file:
        file.write(str(Total))
    file.close()
    
    return Total


