from models.entities.logs.bug_logger import BugLogger
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time

class SheinBotCompras():

    def __init__(self, language='en_US'):
        self.language = language
        self.driver = self.init_driver()
        self.url_base = "https://www.shein.com/"
        self.url_base_usa="https://us.shein.com/"
        self.soup = None
        #self.shn_proc = SheinProcessor()
        self.logger = BugLogger()
        self.on_device_process = 'vps1'
        self.batch_size = 12
        self.sku_detail = []
        self.sku_data = []
        self.lenght_sku_list = None
        self.affected_rows = 0
        self.images_path = os.getenv('IMAGES_PATH')
        self.domain_path = os.getenv('DOMAIN_LOCAL')
        self.url_complete=None
        self.is_found=None
        self.not_processed=[]


    def init_driver(self):
        """ Inicializa el WebDriver con las opciones deseadas """
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            'Accept': "*/*",
            'Accept-Language': self.language,
            'Accept-Encoding': "gzip,deflate,br",
            'Connection': "keep-alive"
        }
        selenium_url = 'http://selenium:4444/wd/hub'
        opts = Options()
        #opts.add_argument("--headless") z
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-notifications")
        #opts.add_argument("--lang=" + self.language)
        #INIT Por Pedro 
        opts.add_experimental_option('detach',True)
        opts.add_experimental_option('excludeSwitches',['enable-automation'])
        opts.add_experimental_option('useAutomationExtension',False)
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument('--disable-infobars')
        opts.add_argument('--disable-browser-side-navigation')
        #END
        opts.add_argument("--lang=es-ES")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-software-rasterizer")  # Nueva opción para reducir tiempos de carga
        opts.add_argument("--no-sandbox")  # Mejora el rendimiento en algunos entornos
        opts.add_argument("--disable-dev-shm-usage")  # Mejora en sistemas con poca memoria compartida
        #opts.add_argument("--disk-cache-dir=/tmp/cache")  # Redireccionar caché para mejorar tiempos
        
        opts.add_argument("--ignore-certificate-errors")
        opts.add_argument(f'User-agent={headers["User-Agent"]}')
        # Intenta conectarte al servidor de Selenium
        driver= webdriver.Remote(
            command_executor=selenium_url,
            options=opts
        )
        #driver= webdriver.Chrome(options=opts)
        return driver
    
    def affected_data(self):
        return self.affected_rows
    
    def updated_rows(self, affected : int):
        
        if self.affected_rows is None:
            self.affected_rows = 0 
        self.affected_rows += affected

    def get_data_process(self,platform:str='Shein',from_app:str='vps1'):
        #response =  self.shn_proc.get_data_for_variantes_proc(platform,from_app)
        response=[{"product_id":"18693230","is_parent":True,'price':53.49,'color':'multicolor','size':'S','quantity':3}]
        if response:
            self.set_sku_data_list(response)
        self.process_skus_data()


    def set_sku_data_list(self,data):
        self.sku_data = data

    def process_skus_data(self):
        sku_list= self.get_sku_data_list()
        #self.affected_rows = 0
        if not sku_list:
            return
        self.lenght_sku_list = len(sku_list)
        try:

            for index,data in enumerate(sku_list):
                print(f"Procesando SKU {index+1} - {data['product_id']}")
                if data.get("product_id", None).strip(): #and bool(int(data.get("is_parent", False))):
                    # url=self.url_base+f"product-p-{data['product_id']}.html?languaje=es"
                    # self.url_complete=self.url_base_usa+f"product-p-{data['product_id']}.html"
                    url=self.url_base+f"product-p-{data['product_id']}.html?languaje=es"
                    self.driver.get(url)
                    self.automatizacion(index)
                    self.url_complete=None
            self.sku_data=None
        except Exception as e:
            print(f"Error al actualizar los datos: {str(e)}")
            return None

    

    def get_sku_data_list(self):
        return  self.sku_data



    def handle_captcha(self):
        """Función para manejar la detección y resolución del captcha"""
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: "captcha" not in d.current_url
            )
            print("Acceso al producto exitoso:", self.driver.current_url)

        except:
            print(self.driver.current_url)
            print("Captcha no resuelto automáticamente, por favor resuélvelo manualmente.")
            time.sleep(3)
            print("Recargando la página para intentar resolver el captcha automáticamente...",self.driver.current_url)
            # Cambiar el User-Agent
            new_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            opts = Options()
            opts.add_argument(f"user-agent={new_user_agent}")
            
            # Reiniciar el driver con el nuevo User-Agent
            self.driver.quit()  # Cerrar el driver actual
            self.driver = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                options=opts
            )  # Crear un nuevo driver con el User-Agent cambiado

            # Recargar la página
            self.driver.get(self.driver.current_url)  # Volver a cargar la misma página con el nuevo User-Agent
            print("Página recargada con nuevo User-Agent.")

            # Volver a ejecutar la verificación del captcha
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: "captcha" not in d.current_url
                )
                print("Acceso al producto exitoso después de recargar:", self.driver.current_url)

            except:
                print(self.driver.current_url)
                print("Captcha aún no resuelto, por favor resuélvelo manualmente.")





    def automatizacion(self,index):

        current_sku=self.sku_data[index]
        self.driver.implicitly_wait(5)
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: "captcha" not in d.current_url
            )
            print("Acceso al producto exitoso:", self.driver.current_url)
        except:
            print(self.driver.current_url)

            self.handle_captcha()
            print("Captcha no resuelto automáticamente, por favor resuélvelo manualmente.")

        self.cerrar_modalV2()
        self.close_modal()
        self.close_banner()


        if self.validate_agotado():
            print("Producto agotado")
            self.not_processed.append(current_sku)
            return
        
        print("Producto disponible")

        if not self.validate_size(current_sku['size']):
            print("Talla no disponible")
            self.not_processed.append(current_sku)
            return
        
        print("Talla disponible")


        if not self.añadir_carrito():
            print("Error al añadir al carrito self.añadir_carrito()")
            self.not_processed.append(current_sku)
            return
        
        print("salio de añadir al carrito")

        if not self.validar_producto_añadido():
            print("Producto no añadido al carrito validacion")
            self.not_processed.append(current_sku)
            return
        

        print("Salio de Producto añadido al carrito")

        if not self.page_compra():
            print("Error al procesar la página de compra")
            self.not_processed.append(current_sku)
            return
        
        print("Página de compra procesada")


        if not self.set_quantity(current_sku['quantity']):
            print("Error al establecer la cantidad")
            self.not_processed.append(current_sku)
            return
        
        
        print("Cantidad establecida correctamente")

        self.updated_rows(1)




        
            


        self.driver.implicitly_wait(5)


    def set_quantity(self, quantity):
        try:
            # Espera explícita para localizar el input
            input_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="bsc-cart-item-goods-qty__input-wrap"]//input[@class="bsc-cart-item-goods-qty__input"]'))
            )

            # Limpia el campo antes de escribir
            input_element.clear()

            # Escribe el nuevo valor
            input_element.send_keys(str(quantity))

            print(f"Cantidad {quantity} escrita correctamente en el input.")
            return True

        except Exception as e:
            print(f"Error al escribir en el input: {e}")
            return False


    def page_compra(self):

        url=self.driver.current_url
        try:

            ir_pagina_compra = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="header-icon not-fsp-element"]//div[@class="bsc-mini-cart__trigger j-bsc-mini-cart__trigger"]'))
            )
            ir_pagina_compra.click()
            self.driver.implicitly_wait(5)
            if self.driver.current_url == url:
                return False
            
            return True
        
        except Exception as e:
            print(f"Error al procesar la página de compra: {str(e)}")
            return False



    def añadir_carrito(self):
        print("dentro de añadir carrito")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="product-intro__add-btn btn-main"]'))
            )
            add_cart_button = self.driver.find_element(By.XPATH,'//div[@class="product-intro__add-btn btn-main"]')
            add_cart_button.click()

            time.sleep(2)
            return True
        except Exception as e:
            print(f"Error al añadir al carrito: {str(e)}")
            return False
        

    def validar_producto_añadido(self):

        print("dentro de validar producto añadido")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="bsc-mini-cart__trigger j-bsc-mini-cart__trigger"]//span[@class="bsc-cart-num"]'))
            )

            data= self.driver.find_element(By.XPATH,'//div[@class="bsc-mini-cart__trigger j-bsc-mini-cart__trigger"]//span[@class="bsc-cart-num"]').text

            if data == '1':
                print("Producto añadido al carrito")
                return True
            else:
                print("Producto no añadido al carrito")
                return False
        except Exception as e:
            print(f"Producto no añadido al carrito. Error: {str(e)}")
            return False

    def validate_agotado(self):
        try:
            content=WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, 
                    '//div[@class="goodsDetail-btn-xl__container"]//div[@class="add-cart__btn-contentwithprice type-b"]//div[@class="text add-carttext-style"]'
                    
                ))
            )
            if content.text.upper().strip() == 'AGOTADO' or content.text.upper().strip() == 'SOLD OUT':
                return True

            return False
        except Exception as e:
            print(f" producto puede añadirse al carrito")
            return False


    def cerrar_modalV2(self):
        try:

            #time.sleep(2)
            
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dialog-header-v2__close-btn svg"))
            )

            boton_cerrar = self.driver.find_element(By.CSS_SELECTOR, ".dialog-header-v2__close-btn svg")
            
            # Hacer clic en el botón de cerrar
            boton_cerrar.click()
            print("Modal cerrado con éxito.")
        except Exception as e:
            print(f"Error al intentar cerrar el modal: {e}")


    def close_modal(self):
        #time.sleep(1)
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="sui-dialog__body"]'))
            )
            close_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="sui-dialog__body"]//span[@class="sui-icon-common__wrap icon-close homepage-she-close"] | //div[@class="sui-dialog__body"]//div[@class="dialog-header-v2__close-btn"]/*'))
            )
            close_button.click()
            return True
        except (TimeoutException,NoSuchElementException) as e:
            print(f"No se encontró el modal o el botón de cierre. Error:")
            return False



    def validate_size(self,size):

        try:
            print("dentro de validar talla")
            container = self.driver.find_element(By.XPATH, '//div[@class="product-intro__size-choose"]')
            print(container.get_attribute("outerHTML"))
            sizes = container.find_elements(By.XPATH, './/span') 

            for s in sizes:
                print(f"Talla encontrada: {s.text}")

            for s in sizes:
                if s.text == size:
                    WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(s))
                    s.click()
                    return True
            return False
        except Exception as e:
            print(f"Error al validar la talla: {str(e)}")
            return False
        

    def close_banner(self):
        time.sleep(1)
        try:
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,'//div[@class="quickg-outside"]'))
            )
            close_button.click()
            print("Banner de registro rápido cerrado con éxito.")
            return True
        except Exception as e:
            print("No se encontró el banner de registro rápido")
            return False












    