from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flask_talisman import Talisman
import os
from dotenv import load_dotenv
from markupsafe import escape
from flask_session import Session
import redis

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Configuración de sesiones con Redis o sistema de archivos
app.config['SESSION_TYPE'] = 'redis' if os.environ.get('REDIS_URL') else 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'uploadfiles_'

if os.environ.get('REDIS_URL'):
    # Configuración para producción con Redis
    app.config['SESSION_REDIS'] = redis.from_url(os.environ['REDIS_URL'])
else:
    # Configuración local (usará sistema de archivos)
    app.config['SESSION_FILE_DIR'] = './flask_session'

Session(app)

# Configuración de seguridad HTTPS
talisman = Talisman(
    app,
    content_security_policy=None,
    force_https=True
)

# Configuraciones de la aplicación
app.config['MAX_CONTENT_LENGTH'] = 10 * (1024**2)  # 10 MiB

def convert_size(size):
    if size == 0:
        return "0B"
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    for unit in units:
        if size < 1024:
            break
        size /= 1024
    return f"{size:.2f} {unit}"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se encontró el archivo')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No se seleccionó ningún archivo')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_type = file.mimetype
            extension = file.filename.split('.')[-1]

            data = file.read()
            size_bytes = len(data)

            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252']
            content = None

            for encoding in encodings:
                try:
                    content = data.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if not content:
                flash('El archivo usa una codificación no soportada')
                return redirect(request.url)

            lines = len(content.splitlines())
            words = len(content.split())
            characters = len(content)

            # Guardar datos en sesión (Redis o sistema de archivos)
            session['filedata'] = {
                'filename': filename,
                'file_type': file_type,
                'extension': extension,
                'size': convert_size(size_bytes),
                'lines': lines,
                'words': words,
                'characters': characters
            }
            session['file_content'] = escape(content)

            return render_template(
                'result.html',
                filename=filename,
                file_type=file_type,
                size=convert_size(size_bytes),
                lines=lines,
                words=words,
                characters=characters
            )

    # Limpiar sesión solo si viene de una redirección desde details
    if request.args.get('clear_session'):
        session.clear()
        
    return render_template('upload.html')

@app.route('/details', methods=['GET'])
def details_page():
    # Obtener y eliminar datos de la sesión
    filedata = session.pop('filedata', {})
    content = session.pop('file_content', None)

    if not filedata or not content:
        flash('La sesión ha expirado o no hay datos')
        return redirect(url_for('upload_file', clear_session=True))

    return render_template(
        'details.html',
        filename=filedata['filename'],
        file_type=filedata['file_type'],
        extension=filedata['extension'],
        size=filedata['size'],
        lines=filedata['lines'],
        words=filedata['words'],
        characters=filedata['characters'],
        content=content
    )

if __name__ == '__main__':
    if os.environ.get('HOSTING'):
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)
    else:
        app.run(host='0.0.0.0', port=8080, debug=True)