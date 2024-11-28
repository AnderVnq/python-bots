from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from contextlib import contextmanager
from mysql.connector import Error
import mysql.connector
import json
# Cargar las variables de entorno
load_dotenv()

# Obtener los datos de conexión desde el .env
class DBConfigSQLAlchemy:
    def __init__(self):
        self.DB_HOST = os.getenv("DB_HOST_TEST")
        self.DB_PORT = os.getenv("DB_PORT_TEST")
        self.DB_USER = os.getenv("DB_USER_TEST")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD_TEST")
        self.DB_NAME = os.getenv("DB_NAME_TEST")

        self.DATABASE_URL = f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        # Crear el engine y la sesión
        self.engine = create_engine(self.DATABASE_URL, pool_size=10, max_overflow=20)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @contextmanager
    def get_db_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()





class DBConfigMySQL:
    def __init__(self):
        self.DB_HOST = os.getenv("DB_HOST_TEST")
        self.DB_PORT = os.getenv("DB_PORT_TEST")
        self.DB_USER = os.getenv("DB_USER_TEST")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD_TEST")
        self.DB_NAME = os.getenv("DB_NAME_TEST")
        self.connection = None
        #self.logger = BugLogger()

    def connect(self):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.DB_HOST,
                    database=self.DB_NAME,
                    user=self.DB_USER,
                    password=self.DB_PASSWORD,
                    #charset=self.db,
                    port=self.DB_PORT,
                )
                return self.connection
        except Error as e:
            self.connection = None
            #self.logger.log_error(f"Error al conectar a la base de datos: {e}")

    def disconnect(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()


    def get_shein_product_list_dbcf(self,platform:str, vps: str = 'vps1'):
            sp_name = f"SP_SkuListToUpdate_Shein"
            try:
                connection = self.connect()
                with connection.cursor() as cursor:
                    cursor.execute("SET @result = '';")
                    cursor.execute(f"CALL {sp_name}(%s,%s, @result);", (platform,vps,))
                    cursor.execute("SELECT @result;")
                    result = cursor.fetchone()[0]
                    json_data = json.loads(result) if result else []
                    return json_data

            except Exception as e:
                return []
            
            finally:
                self.disconnect()




    def massive_update_model(self, table, data, id_field='uuid', batch_size = 100):
        try:
            connection = self.connect()
            connection.autocommit = True
            cursor = connection.cursor()
            update_count = 0
            batch = []
            
            for item in data:
                set_clause = ', '.join([f"{key} = %s" for key in item.keys() if key != id_field])
                values = [item[key] for key in item.keys() if key != id_field]
                values.append(item[id_field])
                query = f"UPDATE {table} SET {set_clause} WHERE {id_field} = %s"
                batch.append((query, values))

                if len(batch) >= batch_size:
                    for q, v in batch:
                        cursor.execute(q, v)  # Ejecutar cada bloque sin commit
                    update_count += len(batch)
                    batch = []

            # Ejecutar cualquier consulta restante en el batch
            if batch:
                for q, v in batch:
                    cursor.execute(q, v)  # Ejecutar cada bloque sin commit
                update_count += len(batch)

            return update_count
        except Error as e:
            return None
        finally:
            self.disconnect()


    def bug_register(self,data_log):

        sp_name = f"SP_BugLogsCreate"
        message = {"message" : None, "code" : None, "status" : False}

        try:
            connection = self.connect()
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute(f"CALL {sp_name}(%s);", (data_log,))

            message["message"] = "Log created"
            message["status"] = True

            return message
        
        except  Exception as e:
            message["message"] =  str(e)
            return message
        
        finally:
            self.disconnect()