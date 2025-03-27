import os
import sys
from django.core.management import execute_from_command_line

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geolocator.settings")
    
    # Detectar si estamos en un entorno de producción
    if 'RENDER' in os.environ:  # Render define esta variable de entorno
        # Usar el puerto dinámico proporcionado por Render
        port = os.getenv('PORT', '8000')
        execute_from_command_line(["manage.py", "runserver", f"0.0.0.0:{port}"])
    else:
        # Desarrollo local: iniciar el servidor y abrir el navegador
        import threading
        import webbrowser
        import time

        def open_browser():
            time.sleep(2)  # Esperar unos segundos para asegurarse de que el servidor esté listo
            webbrowser.open("http://127.0.0.1:8000")

        # Iniciar el navegador en un hilo separado
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Ejecutar el servidor Django en localhost
        execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000"])

if __name__ == "__main__":
    main()