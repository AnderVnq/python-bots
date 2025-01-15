from flask import request, jsonify, Blueprint
from models.entities.ecomerce.shein.shein_controller import SheinController
from services.shein_bot_compras import SheinBotCompras
shein_bp = Blueprint('shein_bp', __name__)



@shein_bp.route('/update/list', methods=['GET'])
def update_list():
    shein_c=SheinController()
    #extracting variant
    shein_c.get_data_for_variant()
    response_data_variante=shein_c.is_found_data()
    #scraping prices
    shein_c.get_product_detail()
    count=shein_c.affected_data()
    shein_c.driver.quit()
    record = "Registro"
    ecomerce = "Shein"
    if count > 0:
        return jsonify({"message":f"{count} {record}{'s' if count > 1 else ''}" f" actualizado{'s' if count > 1 else ''}"
                        , "status":True,"ecormece":ecomerce,"variantes_extraidas":response_data_variante}), 200
    else:
        return jsonify({"message": "No se procesó ningún SKU", "status": False,"ecormece":ecomerce,"variantes_extraidas":response_data_variante}), 400
    



@shein_bp.route('/compras', methods=['GET'])
def get_compras():
    shein_c=SheinBotCompras()
    shein_c.get_data_process()
    shein_c.driver.quit()
    count=shein_c.affected_data()

    if count > 0:
        return jsonify({"message": f"{count} compras extraídas", "status": True}), 200
    
    return jsonify({"message": "No se procesó ninguna compra", "status": False}), 400


@shein_bp.route('/',methods=['GET'])
def init_end_point():
    return '¡Route Works :-)!', 200