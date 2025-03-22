import requests
from bs4 import BeautifulSoup
import random
import time

url_api = "https://us.shein.com/api/productInfo/realTimeData/query?_ver=1.1.8&_lang=es"
base_url_html = "https://us.shein.com/product-p-{}.html"  # URL base del producto

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "es-US,es-419;q=0.9,es;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "origin": "https://us.shein.com",
    "referer": "https://us.shein.com/product-p-10821547.html",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
}

cookies = {
    "armorUuid": "202411061453485afeb5403159d7924e983a62f6e7664600d3e9e1b545375600",
    "cookieId": "C9D5EBAF_B78E_1164_6181_C7C8504A3FB6",
    "RESOURCE_ADAPT_WEBP": "1",
    "language": "uses"
}

payload = {
    "goods_id": "10821744",
    "mallCode": "1",
    "tsp": {},
    "specialSceneType": 0,
    "tags": [],
    "transportTypes": ["urgent_express"]
}

# Número base del producto (puedes cambiarlo)
base_product_id = "10167125"

def generate_random_product_id(base_id):
    """
    Modifica aleatoriamente 3 números en el ID del producto dentro del rango 1-9.
    """
    id_list = list(base_id)  # Convertir el ID en una lista de caracteres
    indices_to_change = random.sample(range(len(id_list)), 3)  # Seleccionar 3 posiciones aleatorias

    for idx in indices_to_change:
        id_list[idx] = str(random.randint(1, 9))  # Cambiar a un número aleatorio entre 1 y 9

    return "".join(id_list)  # Convertir de nuevo a cadena

# Realizar varias solicitudes con diferentes IDs aleatorios
num_requests = 5  # Número de requests a realizar

for i in range(num_requests):
    random_product_id = generate_random_product_id(base_product_id)
    url_html = base_url_html.format(random_product_id)

    print(f"\n🔍 Probando con URL: {url_html}")

    response = requests.get(url_html, headers=headers)

    if response.status_code == 200:
        # Guardar el HTML en un archivo
        file_name = f"producto_{random_product_id}.html"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(response.text)

        print(f"✅ Guardado en {file_name}")

    else:
        print(f"❌ Error {response.status_code}: No se pudo obtener la página del producto.")

    # Agregar un pequeño retraso para evitar bloqueos
    time.sleep(random.uniform(1.5, 3.5))  # Espera entre 1.5 y 3.5 segundos antes de la siguiente solicitud
