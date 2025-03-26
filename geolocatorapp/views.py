import csv
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

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

            # Extraer las IPs válidas (sin duplicados)
            ips = set()
            invalid_rows = []  # Para almacenar mensajes de advertencia específicos
            row_count = 0

            for row in reader:
                row_count += 1
                try:
                    # Verificar que la fila tenga al menos 2 columnas
                    if len(row) < 2:
                        invalid_rows.append(f"Fila {row_count}: Fila incompleta ignorada ({row}).")
                        continue

                    # Obtener la IP de la segunda columna
                    ip = row[1].strip()

                    # Detectar si la fila es una cabecera
                    if ip.lower() in ['ip', 'ip address', 'email']:
                        invalid_rows.append(f"Fila {row_count}: Cabecera detectada y omitida ({ip}).")
                        continue

                    # Validar la IP
                    if not ip or '@' in ip or not is_valid_ip(ip):
                        invalid_rows.append(f"Fila {row_count}: IP inválida o correo electrónico ignorado ({ip}).")
                        continue

                    # Agregar la IP válida al conjunto
                    ips.add(ip)
                except Exception as e:
                    invalid_rows.append(f"Fila {row_count}: Error al procesar fila ({row}): {str(e)}")

            print(f"IPs válidas encontradas (sin duplicados): {ips}")
            total_ips = len(ips)
            print(f"Total de IPs válidas para procesar: {total_ips}")

            # Consultar la API de IPInfo para obtener datos geográficos
            results = []
            processed_ips = 0

            for ip in ips:
                processed_ips += 1
                try:
                    print(f"Consultando API para la IP {ip}... ({processed_ips}/{total_ips})")
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

            # Incluir un resumen de advertencias en la respuesta JSON
            if invalid_rows:
                warning_summary = "Se encontraron advertencias en las siguientes filas:\n" + "\n".join(invalid_rows)
                print(warning_summary)
                return JsonResponse({
                    'message': 'Archivo procesado con éxito.',
                    'warnings': warning_summary,
                }, status=200)
            else:
                return response
        except Exception as e:
            print(f"Error general: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

    # Si no es una solicitud POST, renderiza la página principal
    return render(request, 'upload.html')