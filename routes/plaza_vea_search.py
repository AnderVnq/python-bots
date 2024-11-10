
from flask import Blueprint, request, jsonify
from services.scraping_plaza_vea import PlazaVeaManager



plaza_vea_bp = Blueprint('plaza_vea_bp', __name__)



@plaza_vea_bp.route('/search/plaza_vea', methods=['GET'])
def plaza_vea_search():
    search_text = request.args.get('st')#texto de busqueda
    product_name= request.args.get('np')#nombre del producto
    sku= request.args.get('sku')


    # driver = iniciar_webdriverv1()
    # resultado = extract_info_plaza_vea(driver, search_text,product_name)
    driver=PlazaVeaManager()

    if sku:
        resultado = driver.extract_info_by_sku(sku,search_text)
        driver.finalizar_webdriver()
        if resultado["success"]== False:
            return jsonify(resultado), 400
        return jsonify(resultado), 200

    if not search_text or not product_name:
        return jsonify({"error": "Faltan parámetros"}), 400
    resultado = driver.extract_info_plaza_vea(search_text,product_name)
    driver.finalizar_webdriver()
    if resultado["success"]== False:
        return jsonify(resultado), 400
    else:
        return jsonify(resultado), 200