
from datetime import datetime, timezone
from dateutil import parser
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib

load_dotenv()

# Funciones del programa

def formato_fecha(fecha_str):
    segundos = (datetime.now(timezone.utc) - parser.parse(fecha_str)).total_seconds()
    if segundos < 60 : return "Hace unos segundos"
    if segundos < 3600 : return f"Hace {int(segundos // 60)} minuto{'s' if segundos >= 120 else ''}"
    if segundos < 86400 : return f"Hace {int(segundos // 3600)} hora{'s' if segundos >= 7200 else ''}"
    return f"Hace {int(segundos // 86400)} día{'s' if segundos >= 172800 else ''}"

def extraer_imagen(entry):
    if "content" in entry:
        contenido_html = entry.content[0].value
    else:
        contenido_html = entry.summary
    
    soup = BeautifulSoup(contenido_html, "html.parser")
    img_tag = soup.find("img")
    if img_tag and "src" in img_tag.attrs:
        return img_tag["src"]

    enlaces = soup.find_all("a", href=True)
    for enlace in enlaces:
        if enlace["href"].endswith((".jpg", ".jpeg", ".png", ".gif")):
            return enlace["href"]
    return None

def obtener_contenido(url):
    try:
        # Realizar la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()  # Verificar errores HTTP

        # Analizar el contenido HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Extraer párrafos del contenido principal
        contenido = [p.get_text(strip = True) for p in soup.find_all("p")]
        parrafos = [p for p in contenido if p.endswith(".")]

        return parrafos
    
    except Exception as e:
        print(f"Error al procesar la página: {e}")

def enviar_correo(email_destinatario, tema, contenido):
    email_remitente = "bredalisgautreaux@gmail.com"
    clave_email = os.getenv("CLAVE_EMAIL")
    email_destinatario = email_destinatario

    for i in email_destinatario:
        # Configuración
        email = EmailMessage()
        email["FROM"] = email_remitente
        email["TO"] = i
        email["SUBJECT"] = tema
        email.set_content(contenido)

        contexto = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context = contexto) as smtp:
            # Logearse
            smtp.login(email_remitente, clave_email)

            # Enviar email
            smtp.sendmail(email_remitente, i, email.as_string())