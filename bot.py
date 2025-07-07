 import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.reply("Por favor envía un enlace de YouTube válido.")
        return

    await message.reply("Descargando video, espera un momento...")

    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'mp4',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp4')

        video = FSInputFile(filename)
        await bot.send_video(message.chat.id, video, caption=info.get("title", "Video descargado"))

        os.remove(filename)

    except Exception as e:
        await message.reply("❌ Error al descargar el video.")
        print(e)

# --- Webhook server ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/")
app.on_startup.append(on_startup)

if __name__ == "__main__":
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
