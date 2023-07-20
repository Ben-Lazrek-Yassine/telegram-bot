from telethon import TelegramClient, events, sync

api_id= "25828489"
api_hash = "1b4fb18052a4855e108394b821ff2c16"


client = TelegramClient('session_name', api_id, api_hash)
client.start()
channel_username = 'TESTTESTTEST'
for message in client.get_messages(channel_username, limit=10):
    print(message.message)