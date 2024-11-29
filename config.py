import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    # Configuración de Firebase
    # FIREBASE_CREDENTIALS = os.path.join(os.path.dirname(__file__), os.getenv('FIREBASE_CREDENTIALS'))
    # FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
    
    # Configuraciones de rutas
    IMAGES_PATH = os.getenv('IMAGES_PATH')
    DOCS_PATH = os.getenv('DOCS_PATH')
    DOMAIN = os.getenv('DOMAIN_LOCAL')
    PUBLIC_PATH = os.getenv('PUBLIC_PATH')
    MAIN_PATH = os.getenv('MAIN_PATH')
    #FIREBASE_PATH = os.getenv('FIREBASE_PATH')


    # SSH_HOST=os.getenv('SSH_HOST')
    # SSH_PORT=int(os.getenv('SSH_PORT',22))
    # SSH_USER=os.getenv('SSH_USER')
    # SSH_PASSWORD=os.getenv('SSH_PASSWORD')


    # DB_HOST=os.getenv('DB_HOST')
    # DB_PORT=int(os.getenv('DB_PORT',3306))
    # DB_NAME=os.getenv('DB_NAME')
    # DB_USER=os.getenv('DB_USER')
    # DB_PASSWORD=os.getenv('DB_PASSWORD')
    # DB_CHARSET=os.getenv('DB_CHARSET')


    @classmethod
    def get_base_paths(cls):
        return {
            "images_path": cls.IMAGES_PATH,
            "docs_path": cls.DOCS_PATH,
            "domain": cls.DOMAIN,
            "public_path": cls.PUBLIC_PATH,
            "main_path": cls.MAIN_PATH,
            #"firebase_path": cls.FIREBASE_PATH
        }