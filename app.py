import os
import re
import time
from flask import (
    Flask, render_template, send_from_directory,
    request, redirect, url_for, flash
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "skz-galeria-secreta"  # necesario para mostrar mensajes (flash)

# Aseguramos que la carpeta de uploads exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_filename(filename):
    """Limpia el nombre del archivo pero conserva espacios, #, emojis, etc.
    Solo quita caracteres que rompen el sistema de archivos o rutas."""
    filename = os.path.basename(filename)  # quita cualquier ruta tipo ../
    filename = re.sub(r'[\\/:*?"<>|\x00-\x1f]', '', filename).strip()
    if not filename:
        filename = f"foto_{int(time.time())}.jpg"
    return filename


def unique_path(filename):
    """Evita sobrescribir un archivo si ya existe uno con el mismo nombre."""
    name, ext = os.path.splitext(filename)
    candidate = filename
    i = 1
    while os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], candidate)):
        candidate = f"{name}_{i}{ext}"
        i += 1
    return candidate


@app.route("/")
def index():
    carpeta = app.config["UPLOAD_FOLDER"]
    imagenes = [f for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))]
    # las mas nuevas primero
    imagenes.sort(key=lambda f: os.path.getmtime(os.path.join(carpeta, f)), reverse=True)
    return render_template("gallery.html", imagenes=imagenes)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            flash("No seleccionaste ninguna imagen.")
            return redirect(url_for("upload"))

        if not allowed_file(file.filename):
            flash("Formato no permitido. Usa jpg, jpeg, png, gif o webp.")
            return redirect(url_for("upload"))

        filename = safe_filename(file.filename)
        filename = unique_path(filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        flash("¡Imagen subida con éxito!")
        return redirect(url_for("index"))

    return render_template("uploads.html")


if __name__ == "__main__":
    app.run(debug=True, port=5050)
