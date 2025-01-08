
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import feedparser
from Funciones import formato_fecha, extraer_imagen, obtener_contenido, enviar_correo

def app_kpopnews():
    # Cargar variables de entorno
    load_dotenv()

    app = Flask(__name__)

    # Conexión a la base de datos MongoDB
    cliente = MongoClient(os.getenv("CLAVE_MONGO"), server_api = ServerApi("1"))
    app.db = cliente["KpopNews"]
    coleccion = app.db["Usuarios"]

    # URL del feed RSS de noticias de K-pop
    RSS_FEED_URL = "https://www.soompi.com/es/category/musica/feed"

    # Parsear el feed RSS
    feed = feedparser.parse(RSS_FEED_URL)

    articulos = [
        {
            "título": entry.title,
            "link": entry.link,
            "resumén": entry.summary,
            "img": extraer_imagen(entry),
            "publicado": formato_fecha(entry.published)
        }
        for entry in feed.entries
    ]

    # Información del email
    tema = "KpopNews - Carla 😊💜"
    contenido = open("Contenido_Email.txt", "r", encoding = "utf-8").read()

    @app.route("/")
    def home():
        return render_template("index.html", articulos = articulos)

    @app.route("/mostrar-newsletter")
    def mostrar_newsletter():
        correos_usuarios = [documento.get("Correo") for documento in coleccion.find()]
        enviar_correo(correos_usuarios, tema, contenido)
        return redirect(url_for("home"))

    @app.route("/búsqueda", methods = ["POST"])
    def busqueda():
        dato_busqueda = request.form.get("busqueda")
        articulos_filtrados = [
            articulo for articulo in articulos if dato_busqueda in articulo["título"]
        ]

        return render_template("Busqueda.html", articulos = articulos_filtrados, 
            dato_busqueda = dato_busqueda)

    @app.route("/noticias")
    def noticias():
        return render_template("Noticias.html", articulos = articulos)

    @app.route("/<titulo>")
    def plantilla(titulo):
        articulo = next((art for art in articulos if art["título"] == titulo), None)

        if articulo is not None:
            contenido = obtener_contenido(articulo["link"])
            return render_template("Plantilla.html", articulos = articulos, info_noticia = articulo, 
                contenido = contenido)
        else:
            return redirect(url_for("home"))

    @app.route("/chat-ia")
    def chat_ia():
        return render_template("Chat_IA.html")

    @app.route("/sobre-nosotros")
    def sobre_nosotros():
        return render_template("Sobre_Nosotros.html")

    @app.route("/inicio-sesión", methods = ["GET", "POST"])
    def inicio_sesion():
        nombre = request.form.get("nombre-usuario") 
        correo = request.form.get("correo")
        clave = request.form.get("clave")

        if not coleccion.find_one({"Correo": correo}) and nombre != None and correo != None and clave != None:
            coleccion.insert_many([{"Nombre": nombre, "Correo": correo, "Contraseña": clave}])
            correos_usuarios = [documento.get("Correo") for documento in coleccion.find()]
            enviar_correo(correos_usuarios, tema, "¡Ya puedes recibir Newsletters! 💜 \nSolo debes presionar el botón Newsletter 😊")
            return redirect(url_for("home"))
        return render_template("Inicio_Sesion.html")

    @app.errorhandler(404)
    def error_404(e):
        return render_template("404.html"), 404

    return app

if __name__ == "__main__":
    app = app_kpopnews()
    app.run()