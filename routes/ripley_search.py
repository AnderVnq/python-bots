#from services.scraping_juntoz import iniciar_webdriverv1
from services.scrap_search_ripley import extract_info_search,iniciar_webdriver
from flask import request, jsonify,Blueprint
# Blueprint para mi función de abajo 
ripley_bp = Blueprint('ripley_bp', __name__)

# @ripley_bp.route('/search', methods=['GET'])  # Cambiar a GET
# def search():
#     # Obtener los parámetros de consulta de la URL (query string)
#     search_text = request.args.get('st')  # st = search_text
#     texto = request.args.get('tp')  # tp = nombre_producto 
#     precio = request.args.get('pp')  # pp = precio_producto

#     # Validar que los parámetros estén presentes
#     if not search_text or not texto or not precio:
#         return jsonify({"error": "Faltan parámetros"}), 400

#     # proxy = "51.79.50.22:9300"  # IP:Puerto del proxy
#     # driver = iniciar_webdriver(language='en_US', proxy=proxy)
#     driver = iniciar_webdriverv1()
#     resultado = validar_info(driver, search_text, texto, precio)
#     driver.quit()

#     if resultado:
#         return jsonify(resultado), 200
#     else:
#         return jsonify({"message": "No se encontraron coincidencias."}), 404
    


# @ripley_bp.route('/', methods=['GET'])
# def  hello():
#     return jsonify({"message": "Hello, World!"}), 200



# @ripley_bp.route('/searchv2', methods=['GET'])
# def searchv2():
#     # Obtener los parámetros de consulta de la URL (query string)
#     search_text = request.args.get('st')  # st = search_text
#     pmp = request.args.get('pmp')

#     # Validar que los parámetros estén presentes
#     if not search_text or not pmp:
#         return jsonify({"error": "Faltan parámetros"}), 400 

#     driver = iniciar_webdriver()
#     resultado = extract_info_search(driver, search_text, pmp)
#     driver.quit()
#     if resultado:
#         return jsonify(resultado), 200
#     else:
#         return jsonify({"message": "No se encontraron coincidencias."}), 404










#creame un endoin para recivir datos y me lo muestre en la response 
#crea un endpoint para recibir datos y me lo muestre en la response
#ripley_bp.route('api/sensores/',methods=['POST'])
@ripley_bp.route('/api/sensores/', methods=['POST'])
def generate_texto():
    # Obtener los datos de la petición
    data = request.json
    # Validar que los datos estén presentes
    if not data:
        return jsonify({"error": "No se encontraron datos"}), 400
    # Obtener el valor de la llave 'texto' del diccionario data
    texto = data.get('texto')
    # Validar que el texto esté presente
    if not texto:
        return jsonify({"error": "No se encontró el texto"}), 400
    # Retornar el texto en mayúsculas
    return jsonify({"texto": texto.upper()}), 200


