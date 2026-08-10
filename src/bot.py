import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from sheets_client import save_transaction
from ai_extractor import extract_data_from_receipt

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv()
TELEGRAM_BOT_TOKEN =  os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    image_bytes = await photo_file.download_as_bytearray()
    data = extract_data_from_receipt(image_bytes)
    logging.info(f"Dados extraídos: {data}")
    save_transaction(data)
    logging.info("Dados salvos na planilha!")
    await update.message.reply_text(f"✅ Pix de {data["amount"]} registrado! Pagador: {data["name"]}")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling()

if __name__ == "__main__":
    main()