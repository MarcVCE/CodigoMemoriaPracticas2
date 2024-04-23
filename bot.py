from os import getenv 
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
import json
from dotenv import load_dotenv


load_dotenv()
token = getenv('API_TOKEN')


with open(file="functions.json") as file:
    fichero_json = json.load(file)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto_recibido = update.effective_message.text
    await context.bot.send_message(
     chat_id=update.effective_chat.id, 
     text= f'El mensaje enviado al bot es {texto_recibido}'
    )


def send_email(email_user : str, message : str) -> None:

    pass


def run() -> None:
    application = Application.builder().token(token=token).build()
    start_handler = MessageHandler(filters=filters.TEXT, callback=start)
    application.add_handler(handler = start_handler)
    application.run_polling()


if __name__ == '__main__':
   run() 