from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_talisman import Talisman
import os
from dotenv import load_dotenv
from markupsafe import escape

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Configuración de seguridad HTTPS
talisman = Talisman(
	app,
	content_security_policy=None,
	force_https=True
)

# Configuración para proxy inverso de Render
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Configuraciones de la aplicación
app.config['MAX_CONTENT_LENGTH'] = 10 * (1024**2)  # 10 MiB
ALLOWED_MIME_TYPES = {'text/plain', 'text/csv', 'text/markdown'}

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
	if 'filedata' in session:
		session.clear()

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

			if file_type not in ALLOWED_MIME_TYPES:
				flash('Tipo de archivo no permitido')
				return redirect(request.url)

			extension = file.filename.split('.')[-1]

			data = file.read()
			size_bytes = len(data)

			# Lista de codificaciones a probar
			encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252']
			content = None

			# Intentar diferentes codificaciones
			for encoding in encodings:
				try:
					content = data.decode(encoding)
					break
				except UnicodeDecodeError:
					continue

			if not content:
				flash('El archivo usa una codificación no soportada')
				return redirect(request.url)

			# Procesar el contenido
			lines = len(content.splitlines())
			words = len(content.split())
			characters = len(content)

			session['filedata'] = {
				'filename' : filename,
				'file_type' : file_type,
				'extension' : extension,
				'size' : convert_size(size_bytes),
				'lines' : lines,
				'words' : words,
				'characters' : characters,
				'content' : escape(content)
			}

			return render_template(
				'result.html',
				filename=filename,
				file_type=file_type,
				size=convert_size(size_bytes),
				lines=lines,
				words=words,
				characters=characters
			)

	return render_template('upload.html')

@app.route('/details', methods=['GET'])
def details_page():
	return render_template(
		'details.html',
		filename=session['filedata']['filename'],
		file_type=session['filedata']['file_type'],
		extension=session['filedata']['extension'],
		size=session['filedata']['size'],
		lines=session['filedata']['lines'],
		words=session['filedata']['words'],
		characters=session['filedata']['characters'],
		content=session['filedata']['content']
	)

if __name__ == '__main__':
    if os.environ.get('HOSTING'):
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)
    else:
        app.run(host='0.0.0.0', port=8080, debug=True)
