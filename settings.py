import os
import logging
import json
import boto3
from logging.config import dictConfig
from utils.makefile import makedirectory

makedirectory('logging')

#from dotenv import load_dotenv

#load_dotenv()


client = boto3.client('secretsmanager')
secret_name = "SettingsSecrets"
response = client.get_secret_value(SecretId=secret_name)
secret = json.loads(response['SecretString'])
#print(secret)
DISCORD_API_SECRET = secret["DISCORD_API_SECRET"]
OPENAI_API_TOKEN = secret["OPENAI_API_TOKEN"]
POSTGRES_LOGIN_DETAILS = json.loads(secret["POSTGRES_LOGIN_DETAILS"])
#DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
#OPENAI_API_TOKEN = os.getenv("OPENAI_API_TOKEN")
#POSTGRES_LOGIN_DETAILS = json.loads(os.getenv("POSTGRES_LOGIN_DETAILS"))

# Can create, delete, and draw giveaways
GIVEAWAY_CONTROL = [""]
UTILITY = [""]

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters":{
        "verbose":{
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard":{
            "format": "%(levelname)-10s - %(name)-15s : %(message)s"
        }
    },
    "handlers":{
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/logs/infos.Log",
            "mode": "w",
            "formatter": "verbose"
        }
    },
    "loggers":{
        "bot": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "discord": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        }
    }

}
#dictConfig(LOGGING_CONFIG)
