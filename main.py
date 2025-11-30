import requests as rq
from bs4 import BeautifulSoup
import time as t
import datetime as dt
import os
import configparser
from telethon import TelegramClient, functions, types
from PIL import Image, ImageDraw, ImageFont
import configparser
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.types import InputPhoto
import textwrap
import sys

# Getting steam link
config = configparser.ConfigParser()
config.read('settings.ini')

# Getting tg info
api_id = config["TG"]["api_id"]
api_hash = config["TG"]["api_hash"]
user_id = config["TG"]["user_id"]
session_name = 'anon'  # Name for your session file
client = TelegramClient(session_name, int(api_id), api_hash)

# Deleting old logs
open('logs.txt', 'w').close()
file_path = 'logs.txt'
os.remove(file_path)
open('logs.txt', 'w').close()

# Font settings
text_color = 'black'
text_position = [70, 400]  # (x, y) coordinates

try:
    while True:



        async def get_avatar_image(user_id_or_username, output_path='avatar.jpg'):
            # Getting user entity
            entity = await client.get_entity(user_id_or_username)

            # Getting user's profile photos
            photos = await client(functions.photos.GetUserPhotosRequest(
                user_id=entity,
                offset=0,
                max_id=0,
                limit=1  # Getting only the latest profile photo
            ))

            if photos.photos:
                # Downloading the latest profile photo
                latest_photo = photos.photos[0]
                await client.download_media(latest_photo, output_path)
                print(f"Avatar image downloaded to {output_path}")
            else:
                print("No profile photos found for this user.")


        def steam_status_check():
            with open('logs.txt', 'a') as logs:
                res = rq.get(config['TG']['steam_link'])
                soup = BeautifulSoup(res.content, 'html.parser')  # Getting steam html
                isPlaying = soup.find_all('div', class_='profile_in_game_header')  # Getting profile status
                print(isPlaying)

                if str(isPlaying[0])[36:][:-6] == 'Currently In-Game':  # If in game
                    time_raw = dt.datetime.now()  # Getting data
                    time = time_raw.strftime('%H:%M:%S')

                    steam_status = str(isPlaying[0])[36:][:-6]

                    game_name_raw = soup.find_all('div', class_='profile_in_game_name')  # Getting game name
                    game_name = str(game_name_raw[0])[41:][:-9]

                    list = ['Time: ' + time, '\n', 'Status: ' + steam_status, '\n', 'Game: ' + game_name, '\n' + '\n']
                    text_to_draw = 'Playing "' + game_name + '" in steam'
                    logs.writelines(list)  # Printing final info in logs/console
                    print(list)
                    logs.close()


                elif str(isPlaying[0])[36:][:-6] == 'Currently Online':  # If online

                    time_raw = dt.datetime.now()  # Getting data
                    time = time_raw.strftime('%H:%M:%S')

                    steam_status = str(isPlaying[0])[36:][:-6]

                    list = ['Time: ' + time, '\n', 'Status: ' + steam_status, '\n' + '\n']

                    logs.writelines(list)  # Printing final info in logs/console
                    text_to_draw = 'Currently online in steam'
                    print(list)
                    logs.close()



                elif str(isPlaying[0])[36:][:-6] == 'Currently Offline':  # If offline
                    time_raw = dt.datetime.now()  # Getting data
                    time = time_raw.strftime('%H:%M:%S')

                    steam_status = str(isPlaying[0])[36:][:-6]

                    list = ['Time: ' + time, '\n', 'Status: ' + steam_status, '\n' + '\n']

                    logs.writelines(list)  # Printing final info in logs/console
                    text_to_draw = 'Currently Offline in steam'
                    print(list)
                    logs.close()

            return text_to_draw





        def create_image(text_to_draw, text_color, text_position):
            # Creating an image
            with Image.open('avatar.jpg') as avatar:
                avatar.load()
                max_size = (1000, 1000)
            draw = ImageDraw.Draw(avatar)

            # Loading a font (e.g., TrueType)
            font_size = 45
            my_font = ImageFont.truetype('Early Quake DEMO.otf', font_size)

            # Draw wrapped text
            wrapper = textwrap.TextWrapper(width=20)  # Width
            text_lines = wrapper.wrap(text=text_to_draw)

            for line in text_lines:
                draw.text(text_position, line, fill=text_color, font=my_font)
                text_position[1] += 45

            # Saving or displaying the image
            new_avatar = avatar.resize(max_size)
            new_avatar.save("avatar_with_icon.png")
            text_position[1] = 400
            print(text_position)


        async def update_profile_photo():
            photos = await client.get_profile_photos('me')
            if photos:
                await client(DeletePhotosRequest(
                    id=[InputPhoto(
                        id=photos[0].id,
                        access_hash=photos[0].access_hash,
                        file_reference=photos[0].file_reference
                    )]
                ))

            with open("avatar_with_icon.png", 'rb') as file:
                file1 = await client.upload_file(file)
                await client(UploadProfilePhotoRequest(file=file1))
            print('Correct')
            with open('logs.txt', 'a') as logs:
                logs.writelines('Avatar loaded' + '\n')
                logs.close()





        async def main():
            await get_avatar_image(user_id)
            while True:
                steam_status_check()
                text_to_draw = steam_status_check()
                await client.start()
                create_image(text_to_draw, text_color, text_position)
                await update_profile_photo()

                t.sleep(300)


        if __name__ == "__main__":
            with client:
                client.loop.run_until_complete(main())

except KeyboardInterrupt:
    print("\nKeyboardInterrupt caught! Program is exiting gracefully.")
    #Writting info about closing into a logs
    with open('logs.txt', 'a') as logs:
        logs.writelines('Program stopped')
        logs.close()

    client.start()


    def load_old_avatar():
        with open("avatar.jpg", 'rb') as file:
            print(file)
            file1 = client.upload_file(file)
            client(UploadProfilePhotoRequest(file=file1))

    load_old_avatar()
    sys.exit(0)
