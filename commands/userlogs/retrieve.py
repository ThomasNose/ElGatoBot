
def user_logs(userid, guildid, num):
    path = f"logs/{userid}/{guildid}"
    with open(f"{path}/data.txt", "r") as logs:
        return(logs.readlines()[-num:])
#user_logs("189471724130140160",5)