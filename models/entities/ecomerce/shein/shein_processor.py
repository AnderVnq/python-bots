# from models.database_model import DatabaseModel
from _config.db_config import DBConfigMySQL

class SheinProcessor:
    def __init__(self):

        self.db = DBConfigMySQL()

    def get_product_list_proc(self, platform : str, vps : str):
        data_sku = self.db.get_shein_product_list_dbcf(platform,vps)
        return data_sku 
    
    def update_shein_sku_list_proc(self,data, batch = 100):           
        response = self.db.massive_update_model('scraping', data, 'uuid',  batch)
        return response
    
    def bug_register_proc(self,log_list):
        response =  self.db.bug_register(log_list)
        return response
    

    def get_data_for_variantes_proc(self, platform : str, vps : str):
        data_sku = self.db.get_shein_stract_variations(platform,vps)
        return data_sku



    def update_data_for_variantes_proc(self,data):           
        response = self.db.update_shein_sku_variantes_list_dbcf(data)
        return response


