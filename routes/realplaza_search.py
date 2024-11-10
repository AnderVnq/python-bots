from flask import Blueprint, request, jsonify
from services.scraping_realplaza import RealPlazaManager



realplaza_bp = Blueprint('realplaza_bp', __name__)

def realplaza_search():
    search_text = request.args.get('st')#texto de busqueda
    product_name= request.args.get('np')#nombre del producto
    sku = request.args.get('sku')#sku


    # driver = iniciar_webdriverv1()
    # resultado = extract_info_realplaza(driver, search_text,product_name)

    driver=RealPlazaManager()



    if not search_text or not product_name:
        return jsonify({"error": "Faltan parámetros"}), 400
    resultado = driver.extract_info_realplaza(search_text,product_name)
    driver.finalizar_webdriver()
    if resultado["success"]== False:
        return jsonify(resultado), 400
    if resultado:
        return jsonify(resultado), 200
    else:
        return jsonify({"message": "No se encontraron coincidencias."}), 404