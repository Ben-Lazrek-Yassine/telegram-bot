import csv
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from models import Account, MessageSent, SleepTime
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon import TelegramClient
from utils import *
from telethon.errors import PeerFloodError, FloodWaitError, UserPrivacyRestrictedError



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

        with open('members.csv', 'r', encoding='UTF-8') as f:
            reader = csv.reader(f)
            next(reader)  
            for row in reader:
                username, user_id, access_hash, name, _, _ = row
                try:
                    if access_hash:
                        if username:
                            user = client.get_input_entity(username)
                        else:
                            user = client.get_input_entity(int(user_id))
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

        result = client(
            GetDialogsRequest(
                offset_date=last_date,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=chunk_size,
                hash=0,
            )
        )
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

def add_members_to_channel(client):
    channel_entity = None
    while not channel_entity:
        channel_input = input('Enter the username or ID of the channel where you want to add members: ')
        try:
            channel_entity = client.get_entity(channel_input)
        except ValueError:
            print('Invalid channel username or ID. Please try again.')

    with open('members.csv', 'r', encoding='UTF-8') as f:
        reader = csv.reader(f)
        next(reader)  
        for row in reader:
            username, user_id, access_hash, name, group_name, group_id = row
            try:
                if access_hash:
                    if username:
                        user = client.get_input_entity(username)
                    else:
                        user = client.get_input_entity(int(user_id))
                    client(InviteToChannelRequest(channel_entity, [user]))
                    print(f"Added {name} to the channel.")
                else:
                    print(f"Skipping {name} as they do not have access_hash.")
            except Exception as e:
                print(f"Failed to add {name} to the channel: {e}")


def scrape_all(client):
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    result = client(
        GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0,
        )
    )
    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup == True:
                groups.append(chat)
        except:
            continue

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
                first_name = user.first_name if user.first_name else ''
                last_name = user.last_name if user.last_name else ''
                name = (first_name + ' ' + last_name).strip()
                writer.writerow([
                    username,
                    user.id,
                    user.access_hash,
                    name,
                    target_group.title,
                    target_group.id,
                ])
    print('Members scraped successfully.')
    

def scrape_members(client):
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    result = client(
        GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0,
        )
    )
    chats.extend(result.chats)
    
    for chat in chats:
        try:
            if chat.megagroup == True:
                groups.append(chat)
        except:
            continue

    print('Choose a group to scrape members from:')
    for i, g in enumerate(groups):
        print(f"{i}- {g.title}")

    g_index = input('Enter a number: ')
    target_group = groups[int(g_index)]
    
    # has account with id,app_id,hash_access
    print('Fetching Members...')
    all_participants = client.get_participants(target_group)

    file_mode = input('Do you want to append or overwrite the CSV file? write a/o :')
    if file_mode.lower() == 'a':
        file_mode = 'a'
    else:
        file_mode = 'w'

    print('Saving in file...')
    with open('members.csv', file_mode, encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        if file_mode == 'w':
            writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])
        for user in all_participants:
            username = user.username if user.username else ''
            first_name = user.first_name if user.first_name else ''
            last_name = user.last_name if user.last_name else ''
            name = (first_name + ' ' + last_name).strip()
            writer.writerow([
                username,
                user.id,
                user.access_hash,
                name,
                target_group.title,
                target_group.id,
            ])
    print('Members scraped successfully.')