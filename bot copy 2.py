from os import getenv
import requests 
from telegram import Update
from telegram.ext import Updater, ContextTypes, MessageHandler, Filters
import json
from openai import OpenAI
from dotenv import load_dotenv



load_dotenv()
mi_bot_token = getenv(key='BOT_TOKEN')
mi_api_key = getenv(key='API_KEY_OPENAI')
cliente = OpenAI(api_key=mi_api_key)


with open(file="functions.json") as file:
    fichero_json = json.load(file)


def send_message(chat_id : int, text : str):
    data = {'chat_id': chat_id , 'text': text}
    url = f"https://api.telegram.org/bot{mi_bot_token}/sendMessage"
    response = requests.post(url=url, data=data)
    if response.ok:
       print("Mensaje enviado correctamente")
    else:
       print("Ha habido un error al enviar")

async def analyze_message(update: Update, context: ContextTypes) -> None:
    texto_recibido = update.effective_message.text
    texto_error = "Se ha producido un error"
    chat_id = update.effective_chat.id
    success = choose_function(texto=texto_recibido)
    if not success: 
       send_message(chat_id = chat_id, text = texto_error)



def send_email(email_user : str, message : str) -> None:
    print(f'{message} mandando correctamente a {email_user}')


def choose_function(texto : str, chat_id : int):
    response = cliente.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{'role' : 'user', 
                   'content' : f'En base a este mensaje : {texto} , elige la función que corresponda'}],
        functions=fichero_json,
        function_call='auto'
    )

    opcion = response.choices[0].message.function_call
    if opcion:
        funcion_elegida = opcion.name
        parametros_funcion = json.loads(opcion.arguments)
        match(funcion_elegida):
            case "send_email":
                email = send_email(email_user=parametros_funcion["email_user"] ,
                        message=parametros_funcion["message"])
                return email
    else:
        return False
    

def run() -> None:
    updater = Updater(bot=mi_bot_token)
    dispatcher = updater.dispatcher
    start_handler = MessageHandler(filters=Filters.text, callback=analyze_message)
    dispatcher.add_handler(handler = start_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
   run() 