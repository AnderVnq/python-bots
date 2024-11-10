from flask import Blueprint, request, jsonify
from services.scraping_juntoz import JuntozManager

juntoz_bp = Blueprint('juntoz_bp', __name__)


@juntoz_bp.route('/search/juntoz', methods=['GET'])
def search_juntoz():
    search_text = request.args.get('st')
    codigo = request.args.get('codigo')

    if not search_text or not codigo:
        return jsonify({"error": "Faltan parámetros"}), 400

    # driver = iniciar_webdriverv1()
    # resultado = extract_info_juntoz(driver, search_text, codigo)
    driver = JuntozManager()
    resultado= driver.extract_info_juntoz(search_text,codigo)
    driver.finalizar_webdriver()
    if resultado["success"]==False:
        return jsonify(resultado), 400
    if resultado["success"]==True:
        return jsonify(resultado), 200
