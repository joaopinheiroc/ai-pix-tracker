import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from src.sheets_client import save_transaction
from src.ai_extractor import extract_data_from_receipt

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv()
TELEGRAM_BOT_TOKEN =  os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    image_bytes = await photo_file.download_as_bytearray()
    try:
        data = extract_data_from_receipt(image_bytes)
        logging.info(f"Extracted data: {data}")
        save_transaction(data)
        logging.info("Data saved to spreadsheet!")
        await update.message.reply_text(f"✅ Pix of {data['amount']} registered! Payer: {data['name']}")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ Could not process your receipt right now. Please try again in a few moments.")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling()

if __name__ == "__main__":
    main()