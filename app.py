from logging.handlers import RotatingFileHandler
import os
import logging 
from flask import Flask,send_from_directory,jsonify
from flask_cors import CORS
from routes.ripley_search import ripley_bp
from routes.juntoz_search import juntoz_bp
from routes.plaza_vea_search import plaza_vea_bp
from routes.oechsle_search import oechsle_bp
from routes.promart_search import promart_bp
from routes.sensores import sensores_bp
from _config.db_config import engine
from models.database_bots import Base, RankingProduct
import sqlite3
app = Flask(__name__)
CORS(app)
Base.metadata.create_all(engine)


conn = sqlite3.connect('sensores.db', check_same_thread=False)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dato1 INTEGER,
                    dato2 INTEGER,
                    fecha TEXT
                )''')
conn.commit()

app.config['db_connection'] = conn

#app.register_blueprint(ripley_bp)
app.register_blueprint(juntoz_bp)
app.register_blueprint(plaza_vea_bp)
app.register_blueprint(oechsle_bp)
app.register_blueprint(promart_bp)
app.register_blueprint(sensores_bp)







# Registrando las rutas
#register_blueprints(app)
# Configurar logging para producción
if not app.debug:  # Solo habilitar logs avanzados si no está en modo debug
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # Crear un manejador de logs para escribir en un archivo con rotación
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)  # Nivel de log para producción

    # Agregar el manejador de logs a la aplicación
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)  # Configurar el nivel de log
    app.logger.info('App startup')  # Registrar cuando la app se inicia




# @app.route('/Public/Images/<path:filename>')
# def serve_images(filename):
#     images_path = Config.IMAGES_PATH #os.path.join(app.root_path, 'Public/Images')
#     print(f"Attempting to serve from: {images_path}")  # Esto te ayudará a verificar la ruta
#     return send_from_directory(images_path, filename)

# @app.route('/Public/docs/<path:filename>')
# def serve_docs(filename):
#     docs_path = Config.DOCS_PATH #os.path.join(app.root_path, 'Public/docs')
#     print(f"Attempting to serve from: {docs_path}")  # Esto te ayudará a verificar la ruta
#     return send_from_directory(docs_path, filename)

@app.route('/')
def hello():
    return jsonify("Bienvenido a la API de Ranking Products"), 200




@app.route('/get_ranking', methods=['GET'])
def get_ranking():
    ranking = RankingProduct.get_ranking()


    return jsonify(ranking), 200






@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Error 500: {str(e)}")  # Registrar el error
    response = {
        "error": "Internal Server Error",
        "message": "Ocurrió un problema en el servidor, por favor intenta más tarde."
    }
    return jsonify(response), 500


# if __name__ == "__main__":
#     app.run(debug=True)
































































# def iniciar_webdriver(language='en_US', proxy=None):
#     headers = {
#         'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#         'Accept': "*/*",
#         'Accept-Language': language,
#         'Accept-Encoding': "gzip,deflate,br",
#         'Connection': "keep-alive"
#     }

#     # Opciones de Chrome
#     opts = Options()
#     opts.add_argument("--start-maximized")
#     #opts.add_argument("--headless")
#     opts.add_argument("--disable-notifications")
#     opts.add_argument("--disable-gpu")
#     opts.add_argument("--disable-extensions")
#     #opts.add_argument("--blink-settings=imagesEnabled=false") 
#     opts.add_argument("--ignore-certificate-errors")
#     opts.add_argument(f'User-agent={headers["User-Agent"]}')

#     # Configurar el proxy si se proporciona
#     if proxy:
#         prox = Proxy({
#             'proxyType': ProxyType.MANUAL,
#             'httpProxy': proxy,
#             'sslProxy': proxy
#         })
#         opts.proxy = prox

#     # Inicializar WebDriver con opciones
#     driver = webdriver.Chrome(options=opts)
#     return driver
# def validar_info(driver: webdriver.Chrome, search_text, texto: str, precio):
#     driver.get("https://simple.ripley.com.pe/")
#     driver.implicitly_wait(10)
#     texto = texto.lower().strip()
#     div_container = driver.find_element(By.CLASS_NAME, "Navbar_navbar--navigation--search-bar__kS6kB")
#     search_input = div_container.find_element(By.CLASS_NAME, "SearchBar_searchInput__jatEt")
#     search_input.send_keys(search_text)
#     search_button = div_container.find_element(By.CLASS_NAME, "SearchBar_searchButton__lFj8T")
#     search_button.click()
#     driver.implicitly_wait(5)

#     resultado = None
#     pagina_actual = 1

#     while True:
#         driver.implicitly_wait(3)

#         # Verifica si hay un mensaje de "no se encontraron resultados"
#         try:
#             WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "algolia-search-no-results"))
#             )
#             return None
#         except (NoSuchElementException, TimeoutException):
#             pass

#         # Espera a que el contenedor esté presente
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "catalog-grid"))
#         )

#         catalog_container = driver.find_element(By.CLASS_NAME, 'catalog-container')
#         contenedores = catalog_container.find_elements(By.ID, 'product-border')
#         print(f'Contenedores en esta página: {len(contenedores)}')

#         for index, contenedor in enumerate(contenedores):
#             try:
#                 nombre_element = contenedor.find_element(By.CLASS_NAME, 'catalog-product-details__name')
#                 nombre_producto = nombre_element.text.lower().strip()
#             except NoSuchElementException:
#                 nombre_producto = None

#             if not nombre_producto:
#                 continue

#             precios_element = None
#             try:
#                 precios_element = contenedor.find_element(By.CLASS_NAME, 'catalog-product-details__prices')
#             except NoSuchElementException:
#                 continue

#             # Inicializa precios
#             precio_normal, precio_internet, precio_oferta = None, None, None

#             # Obtiene precios
#             try:
#                 precio_normal = precios_element.find_element(By.XPATH,".//li[@title='Precio Normal']").text
#             except NoSuchElementException:
#                 pass

#             try:
#                 precio_internet = precios_element.find_element(By.XPATH,".//li[@title='Precio Internet']").text
#             except NoSuchElementException:
#                 pass

#             try:
#                 precio_oferta = precios_element.find_element(By.XPATH,".//li[@title='Precio Ripley']").text
#             except NoSuchElementException:
#                 pass

#             if texto in nombre_producto:
#                 if (precio_normal and precio in precio_normal) or \
#                    (precio_internet and precio in precio_internet) or \
#                    (precio_oferta and precio in precio_oferta):
#                     resultado = {
#                         'nombre': nombre_producto,
#                         'precio': precio_normal or precio_internet or precio_oferta,
#                         'contenedor': index + 1,
#                         'pagina': pagina_actual
#                     }
#                     return resultado

        

#         pagina_actual += 1  # Aumentar el número de página
    
#     return None



# Comparar el nombre y los tres precios
# if ratio_similitud>=70:
#     # Compara con el precio normal, internet o de oferta si existen
#     if (precio_normal and precio in precio_normal) or \
#        (precio_internet and precio in precio_internet) or \
#        (precio_oferta and precio in precio_oferta):


#driver.implicitly_wait(3)
# Espera a que el loader esté invisible antes de continuar
# try:
#     WebDriverWait(driver, 2).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "loading-screen"))  # Ajusta el selector del loader
#     )
# except (TimeoutException,NoSuchElementException):
#     print("El loader no se ocultó en el tiempo esperado.")
#     continue


# Obtiene precios
# try:
#     # WebDriverWait(precios_element, 2).until(
#     #     EC.presence_of_element_located((By.XPATH,".//li[@title='Precio Normal']"))
#     # )
#     precio_normal = precios_element.find_element(By.XPATH,".//li[@title='Precio Normal']").text
#     print(precio_normal)
# except Exception:
#     pass
# try:
#     # WebDriverWait(precios_element, 2).until(
#     #     EC.presence_of_element_located((By.XPATH,".//li[@title='Precio Internet']"))
#     # )
#     precio_internet = precios_element.find_element(By.XPATH,".//li[@title='Precio Internet']").text
#     print(precio_internet)
# except Exception:
#     pass
# try:
#     # WebDriverWait(precios_element, 2).until(
#     #     EC.presence_of_element_located((By.XPATH,".//li[@title='Precio Ripley']"))
#     # )
#     precio_oferta = precios_element.find_element(By.XPATH,".//li[@title='Precio Ripley']").text
#     print(precio_oferta)
# except Exception:
#     pass