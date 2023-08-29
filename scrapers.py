import csv
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from utils import *
from telethon import TelegramClient
from models import Account, MessageSent, SleepTime
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.errors import PhoneNumberBannedError

def add_members_to_group(client):
    groups = get_all_groups(client)

    if not groups:
        print("No groups found.")
        return

    print('Choose a group to add members to:')
    for i, group in enumerate(groups):
        print(f"{i+1}- {group.title}")

    try:
        group_index = int(input('Enter the number of the group: ')) - 1
        if group_index < 0 or group_index >= len(groups):
            print('Invalid group number.')
            return

        target_group = groups[group_index]
        members_csv_file = 'members.csv'

        with open(members_csv_file, 'r', encoding='UTF-8') as f:
            reader = csv.reader(f)
            next(reader)  
            for row in reader:
                username, user_id, access_hash, name, _, _ = row
                try:
                    if access_hash:
                        user = client.get_input_entity(username) if username else client.get_input_entity(int(user_id))
                        client(InviteToChannelRequest(target_group, [user]))
                        print(f"Added {name} to the group: {target_group.title}")
                    else:
                        print(f"Skipping {name} as they do not have access_hash.")
                except Exception as e:
                    print(f"Failed to add {name} to the group: {e}")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

def get_all_groups(client):
    chats = []
    try:
        last_date = None
        chunk_size = 200
        groups = []
        result = client(GetDialogsRequest(offset_date=last_date, offset_id=0, offset_peer=InputPeerEmpty(), limit=chunk_size, hash=0))
        chats.extend(result.chats)

        for chat in chats:
            try:
                if chat.megagroup == True:
                    groups.append(chat)
            except:
                continue

        return groups
    except Exception as e:
        print(f"Error occurred while fetching groups: {e}")
        return []

def scrape_all(client):
    groups = get_all_groups(client)

    if not groups:
        print("No groups found.")
        return

    file_mode = input('Do you want to append or overwrite the CSV file? Write a/o: ')
    if file_mode.lower() == 'a':
        file_mode = 'a'
    else:
        file_mode = 'w'

    print('Scraping members from all groups...')
    with open('members.csv', file_mode, encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        if file_mode == 'w':
            writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])
        for target_group in groups:
            print(f'Scraping members from group: {target_group.title}')
            all_participants = client.get_participants(target_group)

            for user in all_participants:
                username = user.username if user.username else ''
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])
    print('Members scraped successfully.')

def get_joined_groups(client):
    groups = get_all_groups(client)

    if not groups:
        print("No groups found.")
        return

    print('Choose a group to scrape members from:')
    for i, group in enumerate(groups):
        print(f"{i}- {group.title}")

    try:
        group_index = int(input('Enter a number: '))
        if group_index < 0 or group_index >= len(groups):
            print('Invalid group number.')
            return

        target_group = groups[group_index]
        scrape_members_from_group(client, target_group)
    except ValueError:
        print("Invalid input. Please enter a valid number.")


def scrape_members_from_group(client, target_group):
    print(f'Fetching members from group: {target_group.title}')
    all_participants = client.get_participants(target_group)
    members_csv_file = 'members.csv'

    file_mode = input('Do you want to append or overwrite the CSV file? Write a/o: ')
    if file_mode.lower() == 'a':
        file_mode = 'a'
    else:
        file_mode = 'w'

    print('Saving in file...')
    with open(members_csv_file, file_mode, encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        if file_mode == 'w':
            writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])
        for user in all_participants:
            username = user.username if user.username else ''
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            user_id = user.id
            access_hash = user.access_hash
            
            try:
                # Check if the user is banned using the 'User' object
                if user.min:
                    print(f"User {username} is banned. Skipping...")
                    continue
            except Exception as e:
                print(f"Error occurred while fetching user {username}: {e}")
                continue
            
            writer.writerow([username, user_id, access_hash, name, target_group.title, target_group.id])
    print('Members scraped successfully.')


def save_credentials():
    print('Please enter your credentials: ')
    api_id = input('API ID: ')
    api_hash = input('API HASH: ')
    phone = input('Phone number: ')

    Account.create(api_id=api_id, api_hash=api_hash, phone=phone)
    print('Credentials saved successfully.')
    

def get_joined_groups(client):
    groups = get_all_groups(client)

    if not groups:
        print("No groups found.")
        return

    print('Choose a group to scrape members from:')
    for i, group in enumerate(groups):
        print(f"{i}- {group.title}")

    try:
        group_index = int(input('Enter a number: '))
        if group_index < 0 or group_index >= len(groups):
            print('Invalid group number.')
            return

        target_group = groups[group_index]
        scrape_members_from_group(client, target_group)
    except ValueError:
        print("Invalid input. Please enter a valid number.")

def forward_to_channel(client):
    source_channel_id = input('Enter the source channel ID: ')
    message_id = input('Enter the message ID to forward: ')

    print("Choose an option:")
    print("1. Send to a specific channel (by ID)")
    print("2. Send to all channels you're in")

    option = input("Enter the option number: ")

    if option == '1':
        target_channel_id = input('Enter the target channel ID to forward the message to: ')
        forward_to_specific_channel(client, source_channel_id, message_id, target_channel_id)
    elif option == '2':
        forward_to_all_channels(client, source_channel_id, message_id)
    else:
        print('Invalid option.')

def forward_to_specific_channel(client, source_channel_id, message_id, target_channel_id):
    try:
        source_entity = client.get_entity(int(source_channel_id))
        target_entity = client.get_entity(int(target_channel_id))
        client.forward_messages(target_entity, message_ids=[int(message_id)], from_peer=source_entity)
        print(f'Message forwarded from channel ID {source_channel_id} to channel ID {target_channel_id}')
    except Exception as e:
        print(f'Failed to forward message. Error: {e}')

def forward_to_specific_channel(client, source_channel_id, message_id, target_channel_id):
    try:
        source_entity = client.get_entity(int(source_channel_id))
        target_entity = client.get_entity(int(target_channel_id))
        client.forward_messages(target_entity, messages=[int(message_id)], from_peer=source_entity)
        print(f'Message forwarded from channel ID {source_channel_id} to channel ID {target_channel_id}')
    except Exception as e:
        print(f'Failed to forward message. Error: {e}')


# channel_ids = [-1001982012072,-1001912800821] 
def forward_to_all_channels(client, source_channel_id, message_id):
    try:
        source_entity = client.get_entity(int(source_channel_id))
        for dialog in client.iter_dialogs():
            try:
                if dialog.entity.megagroup == True:
                    client.forward_messages(dialog.entity, messages=[int(message_id)], from_peer=source_entity)
                    print(f'Message forwarded from channel ID {source_channel_id} to channel ID {dialog.entity.id}')
            except Exception as e:
                print(f'Failed to forward message to channel ID {dialog.entity.id}. Error: {e}')
    except Exception as e:
        print(f'Failed to forward message. Error: {e}')
        
            
#### 

def join_groups_from_file(client):
    groups = []
    with open('groups.txt', 'r') as f:
        for line in f.readlines():
            groups.append(line.strip())

    for group in groups:
        try:
            client(JoinChannelRequest(group))
            print(f'Joined group: {group}')
        except Exception as e:
            print(f'Failed to join group: {group}. Error: {e}')
