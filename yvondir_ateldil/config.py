import os
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
RAIDS = os.getenv('RAIDS_VOCAL_CATEGORY')
# TANK = int(os.getenv('TANK_ID'))
# DD = int(os.getenv('DD_ID'))
# HEAL = int(os.getenv('HEAL_ID'))
# TIMER = int(os.getenv('TIME_ID'))