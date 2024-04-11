import os
import json

curr_dir = os.getcwd()
logs = f"{curr_dir}/logs"
try:
	A = os.listdir(logs)
except:
	print("Broken for now")
exceptions = []

def clean():
    for file in A:
        
        edited_data = []
        new_data = []

        previous = None
        try:
            with open(f"{logs}/{file}/voiceactivity.txt", 'r') as data:
                edited_data = [json.loads(line) for line in data]
                for lines in edited_data:
                    line = lines
                    if line["state"] == "left" and line["state"] != previous:
                        previous = line["state"]
                        joined = None
                    elif line["state"] == "joined" and line["state"] != previous:
                        previous = line["state"]
                        joined = line
                    else:
                        if joined != None:
                            new_data.append(joined)
                            joined = None
                        else:
                            new_data.append(line)

            with open(f"{logs}/{file}/voiceactivity_dedupe.txt", 'w') as data:
                for line in new_data:
                    if line in edited_data:
                        edited_data.remove(line)
                for line in edited_data:
                    line = json.dumps(line).replace("'",'"')
                    data.write(str(line) + "\n")

        except Exception as e:
            exceptions.append(str(e))
            #print(e)
#with open("logs/cleanlogs.txt",'w') as exp:
#    for line in exceptions:
#        print(line)
#        exp.write(line + "\n")
