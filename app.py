from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

# Solo puede subir 10 MiB
app.config['MAX_CONTENT_LENGTH'] = 10 * (1024**2)

def convert_size(size):
    if size == 0:
        return "0B"
    
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    unit = "B" 

    for u in units:
        if size < 1024:
            unit = u
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

             # Validación MIME type
            if not file_type or not file_type.startswith('text/'):
                flash('Tipo de contenido no válido. Solo texto.')
                return redirect(request.url)

            # Calcular tamaño del archivo
            file.seek(0, os.SEEK_END)
            size_bytes = file.tell()
            # Reiniciar posición del cursor
            file.seek(0)  
            size = convert_size(size_bytes)
            
            # Análisis para archivos de texto
            is_text = file_type.startswith('text/')
            lines = words = characters = None
            if is_text:
                try:
                    content = file.read().decode('utf-8')
                    lines = len(content.splitlines())
                    words = len(content.split())
                    characters = len(content)
                except UnicodeDecodeError:
                    is_text = False
                    flash('El archivo no es un texto válido')
            
            return render_template('result.html',
                                filename=filename,
                                file_type=file_type,
                                size=size,
                                is_text=is_text,
                                lines=lines,
                                words=words,
                                characters=characters)
    return render_template('upload.html')

if __name__ == '__main__':
    if os.environ.get('HOSTING'):
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)
    else:
        app.run(host='0.0.0.0', port=8080, debug=False)
