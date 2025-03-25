import csv
import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Tu clave de API de IPInfo
API_KEY = '3b5c89838fc09c'

# Función para validar si una cadena es una dirección IP válida
def is_valid_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or not 0 <= int(part) <= 255:
            return False
    return True

# Vista principal para cargar el archivo CSV
@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        # Obtener el archivo cargado
        uploaded_file = request.FILES.get('csv_file')
        if not uploaded_file:
            return JsonResponse({'error': 'No se ha subido ningún archivo.'}, status=400)

        try:
            # Leer el archivo CSV cargado
            decoded_file = uploaded_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            header = next(reader)  # Saltar la cabecera

            # Extraer las IPs válidas (sin duplicados)
            ips = set()
            for row in reader:
                if len(row) > 1:  # Asegurarse de que la fila tenga al menos 2 columnas
                    ip = row[1].strip()
                    if ip and '@' not in ip and is_valid_ip(ip):  # Ignorar correos electrónicos e IPs inválidas
                        ips.add(ip)

            # Consultar la API de IPInfo para obtener datos geográficos
            results = []
            for ip in ips:
                try:
                    print(f"Consultando API para la IP {ip}...")
                    url = f'https://ipinfo.io/{ip}?token={API_KEY}'
                    response = requests.get(url)
                    data = response.json()

                    city = data.get('city', '')
                    region = data.get('region', '')
                    zip_code = data.get('postal', '')
                    loc = data.get('loc', ',').split(',')
                    lat = loc[0] if len(loc) > 0 else ''
                    long = loc[1] if len(loc) > 1 else ''

                    results.append([ip, city, region, zip_code, lat, long])
                    print(f"Datos obtenidos para la IP {ip}: {city}, {region}, {zip_code}, {lat}, {long}")
                except Exception as e:
                    print(f"Error al procesar la IP {ip}: {e}")
                    results.append([ip, '', '', '', '', ''])

            # Crear un archivo CSV con los resultados
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="processed_results.csv"'
            writer = csv.writer(response)

            # Escribir la cabecera
            writer.writerow(['Número de IP', 'Ciudad', 'Estado', 'Código Postal', 'Latitud', 'Longitud'])
            writer.writerows(results)

            print("Proceso completado. El archivo 'processed_results.csv' ha sido creado.")
            return response
        except Exception as e:
            print(f"Error general: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

    # Si no es una solicitud POST, renderiza la página principal
    return render(request, 'upload.html')