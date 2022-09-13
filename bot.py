import yaml
from WallE.WallE import MyBot

with open("config/bot.yaml", "r")  as stream:
    config= yaml.safe_load(stream)

Heisenberg=MyBot(token= config['TelegramBot']['Token'],name= config['TelegramBot']['Name'])
