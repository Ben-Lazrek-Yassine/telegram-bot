import csv
import os

from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty



def find_session_files(directory):
    session_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.session'):
                session_files.append(os.path.join(root, file))
                
    print(f'Found {len(session_files)} session files.', session_files)
    return session_files

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
