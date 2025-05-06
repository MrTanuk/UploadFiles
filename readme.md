# UploadFiles

Un repositorio *forkeado* de [@MrTanuk](https://github.com/MrTanuk).<br>
Desplegando en Render: https://uploadfiles-immau14.onrender.com.

## Cambios

* Se mejoraron los estilos CSS y animaciones.
* Se añadió un nuevo botón para la página de detalles en la pantalla de resultado.
* Se creó una nueva pantalla de detalles con las siguientes funcionalidades:
  - Capacidad de mostrar el contenido del archivo de texto.
  - Capacidad de mostrar la ubicación del host y cliente.
  - Capacidad de mostrar la fecha y hora del host y cliente.
  - Botón para analizar otro archivo.
* Se agregó un favicon.

## Cambios Técnicos

* Se modularizaron los archivos CSS.
* Ahora se trabaja con gunicorn.
* Se quitó el filtrado por tipo para subir cualquier archivo (aunque el HTML limita parcialmente la selección).
* Se está trabajando con sesiones y cookies:
  - Variable de entorno `SECRET_KEY` para la seguridad de las cookies.
  - Si el archivo es muy largo, te dará los primeros 3900 caracteres de él, ya que si la cookie pesa mucho, no se guardará.
  - Se borra al estar en la página de inicio.

## Fotos de la Interfaz

|Upload|Results|Details|
|:-:|:-:|:-:|
|![image](https://github.com/user-attachments/assets/68f8f5f2-0e9a-4b48-a0b6-3ad3b729a73f)|![image](https://github.com/user-attachments/assets/b55ed239-6f64-4079-bedf-17684664f2ab)|![image](https://github.com/user-attachments/assets/d6197139-8b84-427a-abd0-316876882a17)|




