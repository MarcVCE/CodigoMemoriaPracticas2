from os import getenv 
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
mi_api_token = getenv(key='API_TOKEN')
mi_api_key = getenv(key='API_KEY_OPENAI')
cliente = OpenAI(api_key=mi_api_key)


with open(file="functions.json") as file:
    fichero_json = json.load(file)


async def analyze_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto_recibido = update.effective_message.text
    choose_function(texto=texto_recibido)


def send_email(email_user : str, message : str) -> None:
    print(f'{message} mandando correctamente a {email_user}')


def choose_function(texto: str):
    response = cliente.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{'role' : 'user', 
                   'content' : f'En base a este mensaje : {texto} , elige la función que corresponda'}],
        functions=fichero_json,
        function_call='auto'
    )

    opcion = response.choices[0].message.function_call
    funcion_elegida = opcion.name
    parametros_funcion = json.loads(opcion.arguments)
    match(funcion_elegida):
        case "send_email":
            send_email(email_user=parametros_funcion["email_user"] ,
                       message=parametros_funcion["message"])

def run() -> None:
    application = Application.builder().token(token=mi_api_token).build()
    start_handler = MessageHandler(filters=filters.TEXT, callback=analyze_message)
    application.add_handler(handler = start_handler)
    application.run_polling()


if __name__ == '__main__':
   run() 