from flask import Blueprint, request, jsonify
from services.scraping_oechsle import OechsleManager


oechsle_bp = Blueprint('oechsle_bp', __name__)


@oechsle_bp.route('/search/oechsle', methods=['GET'])
def oechsle_search():
    search_text = request.args.get('st')#texto de busqueda
    product_name= request.args.get('np') #nombre del producto
    price = request.args.get('pr') #precio del producto
    sku = request.args.get('sku')
    driver= OechsleManager()
    if sku:
        resultado = driver.extract_info_by_sku(search_text,sku=sku)
        driver.finalizar_webdriver()
        if resultado["success"] == False:
            return jsonify(resultado), 400
        return jsonify(resultado), 200

    if not search_text:
        return jsonify({"error": "Faltan parámetro search text/ para busqueda"}), 400
    if not product_name:
        return jsonify({"error": "Faltan parámetro product name"}), 400
    if not price:
        return jsonify({"error": "Faltan parámetro precio"}), 400
    
    resultado=driver.extract_info_oechsle(search_text,product_name,price)
    driver.finalizar_webdriver()
    if resultado["success"]== False:
        return jsonify(resultado), 400
    return jsonify(resultado), 200