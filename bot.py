import os
import json
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from openai import OpenAI

# Carga las variables de entorno y demás
load_dotenv()
mi_bot_token = os.getenv('BOT_TOKEN')
mi_api_key = os.getenv('API_KEY_OPENAI')
cliente = OpenAI(api_key=mi_api_key)
mensaje_correcto = True

# Carga el fichero JSON
with open("functions.json", "r") as file:
    fichero_json = json.load(file)

# Funciones
async def send_message(chat_id: int, text: str) -> None:
    data = {'chat_id': chat_id, 'text': text}
    url = f"https://api.telegram.org/bot{mi_bot_token}/sendMessage"
    response = requests.post(url=url, data=data)
    if response.ok:
        print("Mensaje enviado correctamente")
    else:
        print("Ha habido un error al enviar")


async def analyze_message(update: Update, context: CallbackContext) -> None:
    texto_recibido = update.effective_message.text
    chat_id = update.effective_chat.id
    success = choose_function(texto_recibido, chat_id)
    if success == False:
        await send_message(chat_id=chat_id, text="Se ha producido un error")


def send_email(email_user: str, message: str) -> None:
    print(f'{message} mandando correctamente a {email_user}')


def choose_function(texto : str, chat_id : int) -> bool | None:
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
                send_email(email_user=parametros_funcion["email_user"] ,
                           message=parametros_funcion["message"])
    else:
        mensaje_correcto = False
        return mensaje_correcto

# Configuración del Application
if __name__ == '__main__':
    app = Application.builder().token(mi_bot_token).build()
    text_handler = MessageHandler(filters.TEXT, analyze_message)
    app.add_handler(text_handler)
    app.run_polling() # Es como el idle()
