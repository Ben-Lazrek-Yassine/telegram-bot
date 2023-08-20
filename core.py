import asyncio
from models import Account, MessageSent, SleepTime
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon import TelegramClient
from utils import *
import csv



title = """
     _______   _                                  ____        _   
    |__   __| | |                                |  _ \      | |  
       | | ___| | ___  __ _ _ __ __ _ _ __ ___   | |_) | ___ | |_ 
       | |/ _ \ |/ _ \/ _` | '__/ _` | '_ ` _ \  |  _ < / _ \| __|
       | |  __/ |  __/ (_| | | | (_| | | | | | | | |_) | (_) | |_ 
       |_|\___|_|\___|\__, |_|  \__,_|_| |_| |_| |____/ \___/ \__|
                       __/ |                                      
                      |___/                                       

"""
class Color:
    COLORS = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }

    @classmethod
    def colorize(cls, text, color):
        return f"{cls.COLORS[color]}{text}{cls.COLORS['ENDC']}"

def core():
    accounts=Account.select()
    print(Color.colorize(title, 'OKGREEN'))
    try:
        while True:
            print(Color.colorize('What do you want to do?', 'HEADER'))
            print(f"[{Color.colorize('1', 'OKBLUE')}] - Add a new Telegram account")
            print(f"[{Color.colorize('2', 'OKBLUE')}] - List Telegram accounts")
            print(f"[{Color.colorize('3', 'OKBLUE')}] - Delete a Telegram account")
            print(f"[{Color.colorize('4', 'OKBLUE')}] - Select which group the bot will use to send next messages")
            print(f"[{Color.colorize('5', 'OKBLUE')}] - Start Mass DM")
            print(f"[{Color.colorize('6', 'OKBLUE')}] - Change min and max sleep seconds per DM sent")
            print(f"[{Color.colorize('7', 'OKBLUE')}] - Forward members to a group")
            print(f"[{Color.colorize('8', 'OKBLUE')}] - Forward messages to a group")

            action = input('Enter: ')

            if action == '1':
                save_credentials()

            elif action == '2':
                list_accounts()

            elif action == '3':
                delete_account()

            elif action == '4':
                choose_group()

            elif action == '5':
                            if len(accounts) > 0:
                                loop = asyncio.get_event_loop()
                                tasks = []
                                for account in accounts:
                                    tasks.append(loop.create_task(run(account)))
                                wait_tasks = asyncio.wait(tasks)
                                loop.run_until_complete(wait_tasks)
                            else:
                                print('No accounts found. Please add an account first.')

            elif action == '6':
                sleep_obj = SleepTime().select().get()
                MIN_SLEEP = sleep_obj.max_sleep_seconds
                MAX_SLEEP = sleep_obj.min_sleep_seconds
                print(f"Minimum sleep time is set to {Color.colorize(MIN_SLEEP, 'OKGREEN')}")
                print(f"Maximum sleep time is set to {Color.colorize(MAX_SLEEP, 'OKGREEN')}")
                print('The greater these values, the best!')
                while True:
                    min_sleep = input('Choose your new minimum sleep time per DM sent (seconds): ')
                    max_sleep = input('Choose your new maximum sleep time per DM sent (seconds): ')
                    if not min_sleep.isnumeric() or not max_sleep.isnumeric():
                        print(Color.colorize('Please, type only numbers!', 'WARNING'))
                        continue
                    if int(min_sleep) > int(max_sleep):
                        print(Color.colorize('Minimum sleep time cannot be greater than maximum sleep time!', 'WARNING'))
                        continue
                    if int(max_sleep) - int(min_sleep) < 60:
                        print(Color.colorize('The difference between maximum sleep time and minimum sleep time must be equal or greater than 60 seconds', 'WARNING'))
                        continue
                    if int(min_sleep) < 120:
                        print(Color.colorize('Minimum sleep time cannot be inferior to 120 seconds', 'WARNING'))
                        continue
                    break
                
                sleep_obj.min_sleep_seconds = int(min_sleep)
                sleep_obj.max_sleep_seconds = int(max_sleep)
                sleep_obj.save()
                print(Color.colorize('Successfully changed sleep time.', 'OKGREEN'))

            elif action == '7':
                invite_members()
            
            elif action == '8':
                forward_messages()    
                                           
    except Exception as e:
        print(Color.colorize(e, 'FAIL'))
