import asyncio
import os

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
import requests
from bs4 import BeautifulSoup
from redis_handler import r

# Replace with your Telegram bot token
from database import User, engine

BOT_TOKEN = "7199296374:AAEuOcaqAXOcApWKURdY4KLADsmsofld1q8"
#from sqlalchemy.orm import Session
# Base URL for Instagram media
BASE_URL = "https://www.instagram.com/"

BASE_URL_YOUTUBE = "https://www.youtube.com/"


async def download_media(url):
    try:
        # Extract post ID from the URL
        post_id = url.split("/")[-2]
        type = url.split("/")[-3]

        # Make a request to the Instagram post URL
        response = requests.get(f"{BASE_URL}{type}/{post_id}")
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the media type (video, photo, or reel)
        media_type = None
        media_url = None
        # Check for video and reel
        video_source = soup.find("video source")
        if video_source:
            media_type = "video"
            media_url = video_source["content"]
        elif soup.find("meta", property="og:type", content="video.other"):
            media_type = "reel"
            # Extract reel download URL using unofficial methods (unreliable)
            media_url = get_reel_download_url(post_id)

        # Check for photo
        if not media_url:
            image_meta = soup.find("meta", property="og:image")
            if image_meta:
                media_type = "photo"
                media_url = image_meta["content"]

        # Download the media
        if media_url:
            file_name = f"{post_id}.{media_type.split('/')[-1]}"
            with open(file_name, "wb") as file:
                file.write(requests.get(media_url).content)
            return file_name
        else:
            return "Media not found or unsupported type."

    except Exception as e:
        print(f"Error downloading media: {e}")
        return "An error occurred while downloading media."


async def get_reel_download_url(post_id):
    # This method uses unofficial methods and might not work consistently
    url = f"https://www.instagram.com/reel/videos/{post_id}/"
    response = requests.get(url)
    try:
        data = response.json()
        return data["graphql"]["shortcode_media"]["video_url"]
    except Exception:
        return None


async def handle_name(chat_id, name):
    await bot.send_message(chat_id, f"{name} tilni tanlang")
    await bot.send_message(chat_id, "Tilni kiriting UZ/RU")

async def handle_ru(chat_id):
    await bot.send_message(chat_id, "Введите ссылку на пост в Instagram, который вы хотите скачать!")

async def handle_uz(chat_id):
    await bot.send_message(chat_id, "Yuklamoqchi bo'lgan instagram postingiz linkini kiriting! ")

async def handle_message(message: Message):
    #if r.get(message.from_id):
    #    r.delete(message.from_id)
    if message.text == "/start":
        if r.get(message.from_id):
            if r.get(message.from_id) == "UZ":
                await handle_uz(message.from_id)
            elif r.get(message.from_id) == "RU":
                await handle_ru(message.from_id)
        else:

            a = await message.answer("Instgramdan rasm yuklovchi botga xush kelibisiz!")
            #r.set(message.from_id, {"name": a["chat"]["name"]})
            await handle_name(message.from_id, a["chat"]["first_name"])
        #language = await message.answer("Biror tilni kiriting: O'zbek yoki Rus")

    if message.text.startswith("https"):
        # Get the first URL from the message
        url = message.text.split()[0]
        if BASE_URL in url:
            file_name = await download_media(url)
            if file_name:
                await message.answer_photo(open(file_name, "rb"))
                await asyncio.sleep(2)  # Wait before deleting temporary file
                # Delete the downloaded file
                os.remove(file_name)
            else:
                await message.answer(file_name)
        else:
            await message.answer("Please provide a valid Instagram post URL.")

    if message.text == "UZ":
        r.set(message.from_id, "UZ")
        await handle_uz(message.from_id)

    if message.text == "RU":
        r.set(message.from_id, "RU")
        await handle_ru(message.from_id)


if __name__ == "__main__":
    # Create a bot instance and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    # Register the handler for messages
    dp.register_message_handler(handle_message)

    # Start polling for updates
    executor.start_polling(dp, skip_updates=True)
