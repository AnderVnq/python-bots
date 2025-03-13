# from models.database_model import DatabaseModel
from _config.db_config import DBConfigMySQL
from logs.bug_logger import  BugLogger
import time
import json


class SheinProcessor:
    def __init__(self):

        self.db = DBConfigMySQL()
        self.logger=BugLogger()
        self.pool=None



    def db_connection(self,from_dev : str | None = '*'):
        self.pool = self.db.connect()
        return self.pool 
    
    def disconnect_db(self):
        if self.pool:
            self.pool = None



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

    



    def update_product_list(self,data_list :list[dict[str, any]],from_dev : str | None = '*',retries: int = 3,retry_delay: int = 2):
        sp_name = f"SPCU_ProductList_Shein"
        connection = None
        response = {"message":None,"status":False,"actualizado":0}
        for attempt in range(retries): 
            try:

                connection = self.db_connection(from_dev = from_dev)
                if not connection:
                    return []
                data_order = json.dumps(data_list, indent=0, sort_keys=False, ensure_ascii=False)
                with connection.cursor() as cursor:
                    cursor.execute("SET @result = '';")
                    cursor.execute(f"CALL {sp_name}(%s,@result);", (data_order,))
                    connection.commit()
                    # for result in cursor.stored_results():
                    #     rows = result.fetchall()
                    #     for row in rows:
                    #         response["actualizado"] =  row[0]
                    cursor.execute("SELECT @result;")
                    response["actualizado"] = cursor.fetchone()[0]
                
                response["status"] = True
                return response

            except Exception as e:
                print("ERROR",e)
                if "Deadlock found when trying to get lock" in str(e):
                    if attempt < retries - 1:  # Si no es el último intento
                        print(f"Deadlock detected, retrying... Attempt {attempt + 1}")
                        time.sleep(retry_delay)
                        continue  # Reintentar
                    else:
                        print("Max retries reached for deadlock.")
                        log_list = self.logger.bug_logs_data(e)
                        self.bug_register_proc(log_list)
                        response["message"] =  str(e)
                        return response
                else:
                    log_list = self.logger.bug_logs_data(e)
                    self.bug_register_proc(log_list)
                    response["message"] =  str(e)
                    return response            
            finally:
                if connection:
                    connection.close()
                self.disconnect_db()

