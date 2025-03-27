# #!/usr/bin/env python
# """Django's command-line utility for administrative tasks."""
# import os
# import sys


# def main():
#     """Run administrative tasks."""
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geolocator.settings")
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#     execute_from_command_line(sys.argv)


# if __name__ == "__main__":
#     main()

import os
import threading
import webbrowser
from django.core.management import execute_from_command_line

def open_browser():
    # Esperar unos segundos para asegurarse de que el servidor esté listo
    import time
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Configurar el entorno de Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geolocator.settings")
    
    # Iniciar el navegador en un hilo separado
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Ejecutar el servidor Django
    execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000"])