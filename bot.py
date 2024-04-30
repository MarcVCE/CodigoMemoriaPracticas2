import os
import json
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from openai import OpenAI

# Carga las variables de entorno y demás
load_dotenv()
mi_bot_token = os.getenv('BOT_TOKEN')
mi_api_key = os.getenv('API_KEY_OPENAI')
smtp_host = os.getenv('SMTP_HOST')
smtp_port = os.getenv('SMTP_PORT')
smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')
cliente = OpenAI(api_key=mi_api_key)

# Carga el fichero JSON
with open("functions.json", "r") as file:
    fichero_json = json.load(file)


# Funciones
def send_message(chat_id: int, text: str) -> None:
    data = {'chat_id': chat_id, 'text': text}
    url = f"https://api.telegram.org/bot{mi_bot_token}/sendMessage"
    response = requests.post(url=url, data=data)
    if response.ok:
        print("Mensaje de telegram enviado correctamente")
        return True
    else:
        print("Ha habido un error al enviar")
        return False


async def analyze_message(update: Update, context: CallbackContext) -> None:
    texto_recibido = update.effective_message.text
    chat_id = update.effective_chat.id
    success = choose_function(texto=texto_recibido)
    if success:
        send_message(chat_id=chat_id, text="✅ Mensaje enviado correctamente")
    else:
        send_message(chat_id=chat_id, text="❌ Se ha producido un error")


    # cliente.chat.completions.create => "Simulas que estás en chatgpt"
    # y con el content, es el prompt/lo que le pondrías por texto 
    # que le pondrías a realizar, y claro esto lo hacemos porque la idea
    # es hacerlo desde código y no irte manualmente a chatgpt (que además
    # no cumpliría los objetivos que queremos)
    

def redactar_correo_con_ia(message_text: str) -> str:
    response = cliente.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{'role' : 'user', 
                    'content' : (f'En base a este mensaje : {message_text} , devuelve en un objeto JSON que tenga' +
                                  ' como claves asunto y correo, el contenido redactado para un correo electrónico' + 
                                  ' y el asunto para el mismo.')}]
    )

    email_redactado_str = response.choices[0].message.content
    email_redactado = json.loads(email_redactado_str)
    return email_redactado

    

def send_email(email_user: str, message_text: str) -> bool:
    email_content = redactar_correo_con_ia(message_text=message_text)
    message = MIMEMultipart()
    message["From"] = f"AIbot <{smtp_user}>"
    message["To"] = email_user
    message["Subject"] = email_content["asunto"]
    body = email_content["correo"]
    message.attach(payload=MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP(host=smtp_host, port=smtp_port)
        server.starttls()
        server.login(user=smtp_user, password=smtp_password)
        server.sendmail(from_addr=smtp_user, to_addrs=email_user, msg=message.as_string())
        print(f'{message_text} mandando correctamente a {email_user}')
        server.quit()
        return True
    except Exception as ex:
        print(f"Error al enviar el correo electrónico : {ex}")
        server.quit()
        return False


def choose_function(texto : str) -> bool | None:
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
        parametros_funcion = json.loads(s=opcion.arguments)
        match(funcion_elegida):
            case "send_email":
                success = send_email(email_user=parametros_funcion["email_user"] ,
                           message_text=parametros_funcion["message"])
    else:
        success = False
    
    return success



if __name__ == '__main__':
    print("\nIniciando bot...")
    app = Application.builder().token(token=mi_bot_token).build()
    text_handler = MessageHandler(filters=filters.TEXT, callback=analyze_message)
    app.add_handler(handler=text_handler)
    app.run_polling() 


    