from flask import request, jsonify, Blueprint
from models.entities.ecomerce.shein.shein_controller import SheinController

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
    




@shein_bp.route('/',methods=['GET'])
def init_end_point():
    return '¡Route Works :-)!', 200