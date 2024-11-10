from flask import Blueprint, request, jsonify
from services.scraping_promart import PromartManager




promart_bp = Blueprint('promart_bp', __name__)



@promart_bp.route('/search/promart', methods=['GET'])
def promart_search():
    sku = request.args.get('sku')
    search_text = request.args.get('st')  # Texto de búsqueda
    price = request.args.get('pr')
    product_name = request.args.get('np')  # Nombre del producto
    
    driver = PromartManager()

    # Si se proporciona el SKU, hacemos la búsqueda directamente por SKU
    if sku:
        resultado = driver.extract_info_by_sku(sku,search_text)
        driver.finalizar_webdriver()
        if resultado["success"] == False:
            return jsonify(resultado), 400
        return jsonify(resultado), 200
    
    if not search_text:
        return jsonify({"error": "Faltan parámetro search text"}), 400
    if not price:
        return jsonify({"error": "Faltan parámetro precio"}), 400
    if not product_name:
        return jsonify({"error": "Faltan parámetro product name"}), 400

    # Realizar el scraping con los parámetros de búsqueda
    resultado = driver.extract_info_promart(search_text, product_name, price)
    driver.finalizar_webdriver()
    
    if resultado["success"] == False:
        return jsonify(resultado), 400

    return jsonify(resultado), 200