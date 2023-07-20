import asyncio
import csv
import os
import random

from models import Account, MessageSent, SleepTime
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.sync import TelegramClient
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from scrapers import get_all_groups
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerChannel
from scrapers import *
                

def make_sure_an_account_exists():
    accounts = Account.select()
    if len(accounts) == 0:
        print('No account was found! Please enter a new one')
        save_credentials()


def load_message_to_send():
    if not os.path.isfile('message.txt'):
        with open('message.txt', 'w'):
            pass
    with open('message.txt', 'r', encoding='utf-8') as f:
        message = f.read().strip()
    return message


async def send_messages(client, message, usernames, phone=''):
    sleep_obj = SleepTime().select().get()

    MIN_SLEEP = sleep_obj.min_sleep_seconds
    MAX_SLEEP = sleep_obj.max_sleep_seconds

    if len(message) > 0:
        for username in usernames:
            query = MessageSent.select().where(
                MessageSent.username == username,
                MessageSent.message == message,
            )
            if not query.exists():
                print('Sending Message...')
                try:
                    await client.send_message(username, message)
                    message_record = MessageSent(
                        username=username, message=message
                    )
                    message_record.save()
                    print(
                        f'Sent message "{message}" to user "{username}" using phone {phone}'
                    )
                    sleep_seconds = random.randint(MIN_SLEEP, MAX_SLEEP)
                    print(f'Waiting {sleep_seconds} seconds for safety')
                    await asyncio.sleep(sleep_seconds)
                except PeerFloodError:
                    print(
                        f'{phone} reached Telegram daily limit! Stopping now'
                    )
                    break
            else:
                print('Already sent this message. Skipping...')
    else:
        print('You did not define a message to send to users')
        print(
            'Please open file message.txt and paste the message you need to be sent'
        )


def get_usernames():
    if os.path.isfile('members.csv'):
        try:
            with open('members.csv', 'r', encoding='utf-8') as f:
                csvreader = csv.reader(f)
                usernames = []
                for line in csvreader:
                    if line[0] not in ('username', ''):
                        usernames.append(line[0])
            return usernames
        except Exception as e:
            print(e)
    else:
        print(
            'No group selected. Please select a group to select a message from first'
        )
        return []


def make_sure_client_authenticates(phone, api_id, api_hash):
    try:
        print(f'Checking if {phone} is authenticated...')
        client = TelegramClient(phone, api_id, api_hash)
        client.connect()
        if not client.is_user_authorized():
            print('Just one more step is needed...')
            print(f'Telegram will send a code to {phone}.')
            print(f'Please check if you received a code via SMS or Telegram app')
            client.send_code_request(phone)
            client.sign_in(
                phone, input(f'Enter the code that Telegram sent to {phone}: ')
            )
        print('OK')
        client.disconnect()
    except Exception as e:
        print(e)


def save_credentials():
    print(
        'HELP: Visit https://my.telegram.org/ to get the API ID and the API hash for your account'
    )
    phone = input('Enter the account phone number (with country code): ').strip()
    api_id = int(input('Enter the account API ID: ').strip())
    api_hash = input('Enter the account API hash: ').strip()
    make_sure_client_authenticates(phone, api_id, api_hash)
    account = Account(phone=phone, api_id=api_id, api_hash=api_hash)
    account.save()
    print('Account saved')


def keep_running():
    print('Execution ended. You can close this window and re-open it again...')
    while True:
        pass


def print_accounts(accounts):
    for account in accounts:
        print(f'Found {len(accounts)} telegram account(s) saved')
        make_sure_client_authenticates(account.phone, account.api_id, account.api_hash)


def ask_to_add_new_account():
    answer = None
    while answer not in ('y', 'n'):
        answer = input('Do you want to add a new account? [y/n]: ').strip().lower()
    if answer == 'y':
        print('OK, next add a new account.')
        save_credentials()


async def run(account):
    try:
        client = TelegramClient(account.phone, account.api_id, account.api_hash)
        await client.connect()
        await send_messages(
            client,
            message=load_message_to_send(),
            usernames=get_usernames(),
            phone=account.phone,
        )
    except Exception as e:
        print(e)


def return_accounts():
    accounts = Account.select()
    accs = []
    for account in accounts:
        accs.append(account)
    return accs


def list_accounts():
    accounts = Account.select()
    if len(accounts) > 0:
        for account in accounts:
            print(f'{account.id}')
            print(f'Phone: {account.phone}')
            print(f'API ID: {account.api_id}')
            print(f'API hash: {account.api_hash}')
            print('')
    else:
        print('No accounts saved.')
    return accounts


def delete_account():
    ids = []
    accounts = Account.select()
    if len(accounts) > 0:
        for account in accounts:
            print(f'[{account.id}] - {account.phone}')
            ids.append(str(account.id))

        account_to_delete_id = None
        while account_to_delete_id not in ids:
            account_to_delete_id = input('Which account do you want to delete? ')
        account = Account.select().where(Account.id == account_to_delete_id).get()
        account.delete_instance()
        os.remove(f'{account.phone}.session')
        print(f'Successfully deleted {account.phone}')
    else:
        print('No accounts saved.')


def invite_members():
    accounts = Account.select()
    if len(accounts) > 0:
        print('Available Telegram accounts:')
        for account in accounts:
            print(f'[{account.id}] - {account.phone}')

        account_to_use_id = None
        while account_to_use_id not in [str(account.id) for account in accounts]:
            account_to_use_id = input('Choose the account to use for member invitation: ')

        selected_account = Account.select().where(Account.id == account_to_use_id).get()

        choice = None
        while choice not in ['1', '2']:
            print('Which function to execute for member invitation:')
            print('[1] Add members to all groups')
            print('[2] Add members to a specific channel')
            choice = input('Enter the option number: ')

        client = TelegramClient(selected_account.phone, selected_account.api_id, selected_account.api_hash)
        client.connect()

        try:
            if choice == '1':
                add_members_to_group(client)
            elif choice == '2':
                add_members_to_channel(client)
        except Exception as e:
            print(f'Error occurred during member invitation: {e}')

        client.disconnect()
    else:
        print('No accounts saved. Please add an account first.')

def choose_group():
    from scrapers import scrape_members, scrape_all 
    accounts = Account.select()
    if len(accounts) > 0:
        ids = []
        for account in accounts:
            print(f'[{account.id}] - {account.phone}')
            ids.append(str(account.id))
        account_to_use_id = None
        while account_to_use_id not in ids:
            account_to_use_id = input('Which account do you want to use? ')
        account = Account.select().where(Account.id == account_to_use_id).get()

        print(f'Logged in with {account.phone}')
        option = None
        while option not in ('1', '2'):
            option = input('Do you want to:\n[1] Select a specific group\n[2] Scrape all groups\nEnter the option number: ')
        client = TelegramClient(account.phone, account.api_id, account.api_hash)
        client.connect()
        if option == '1':
            scrape_members(client)
        elif option == '2':
            scrape_all(client)
        client.disconnect()
    else:
        print('No account saved. Please add an account first')


