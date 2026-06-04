import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
PHOTOS_DIR = Path(__file__).parent / "received_photos"
PHOTOS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "foodfestival.com.ua product photo bot\n\n"
        "Send me photos and I will save them for review.\n"
        "Send multiple photos one by one or as an album."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    photo = message.photo[-1]  # highest resolution

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:20]
    caption = message.caption or ""
    safe_caption = "".join(c if c.isalnum() or c in "-_" else "_" for c in caption)[:40]
    filename = f"{timestamp}{'_' + safe_caption if safe_caption else ''}.jpg"
    filepath = PHOTOS_DIR / filename

    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive(filepath)

    count = len(list(PHOTOS_DIR.glob("*.jpg")))
    await message.reply_text(
        f"Saved: {filename}\n"
        f"Total photos: {count}\n\n"
        f"Send more photos or describe the design you want applied."
    )
    logger.info(f"Saved photo: {filepath}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await update.message.reply_text("Please send images only (JPEG, PNG, etc.)")
        return

    ext = doc.file_name.rsplit(".", 1)[-1].lower() if "." in doc.file_name else "jpg"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:20]
    filename = f"{timestamp}.{ext}"
    filepath = PHOTOS_DIR / filename

    file = await context.bot.get_file(doc.file_id)
    await file.download_to_drive(filepath)

    count = len(list(PHOTOS_DIR.glob("*")))
    await update.message.reply_text(
        f"Saved (original quality): {filename}\n"
        f"Total photos: {count}"
    )
    logger.info(f"Saved document photo: {filepath}")


async def list_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = sorted(PHOTOS_DIR.glob("*"))
    if not photos:
        await update.message.reply_text("No photos yet.")
        return
    lines = [f"{i+1}. {p.name}" for i, p in enumerate(photos)]
    await update.message.reply_text(f"Photos ({len(photos)}):\n" + "\n".join(lines))


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN not set. Copy .env.example to .env and add your token.")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_photos))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    logger.info("Bot started. Waiting for photos...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
