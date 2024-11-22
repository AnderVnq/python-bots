from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict
import asyncio
import time
import os
import requests
from selenium.webdriver.common.keys import Keys
import re
import json








class SheinController():
    def __init__(self, language='en_US'):
        self.language = language
        self.driver = self.init_driver()
        self.url_base = "https://www.shein.com/"
        self.soup = None
 
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
            #opts.add_argument("--headless") 
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
            # driver= webdriver.Remote(
            #     command_executor=selenium_url,
            #     options=opts
            # )

            driver= webdriver.Chrome(options=opts)
            return driver






    def extract_info(self):
         
        sku=18693230
        url=self.url_base+f"/product-p-{sku}.html"

        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: "captcha" not in d.current_url
            )
            print("Acceso al producto exitoso:", self.driver.current_url)
        except:
            print("Captcha no resuelto automáticamente, por favor resuélvelo manualmente.")

        # Si se logra salir del CAPTCHA, continuar con el scraping
        if "captcha" not in self.driver.current_url:
            print("Página del producto lista para el scraping.")
        else:
            print("Permaneciendo en la página del CAPTCHA.")
        try:
            modal_is_closed = self.close_modal()
            if modal_is_closed:
                print("Modal cerrado")
            else:
                print("No se encontró el modal")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID,"goods-detail-v3"))
            )

            banner_is_closed=self.close_banner()
            if banner_is_closed:
                print("Banner cerrado")
            else:
                print("No se encontró el banner")

            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            #generar el html
            # with open("product.html", "w", encoding="utf-8") as file:
            #     file.write(self.driver.page_source)

            response_captura=self.capture_image_size("png")
            if response_captura:
                print("Captura realizada con éxito")
            else:
                print("Error al realizar la captura")
            response_json=self.extract_data_soup()



            if response_json:
                print("Información extraída con éxito")
                self.structure_data(response_json)
            else:
                print("Error al extraer la información")

        except Exception as e:
            print(e)
            print("Error al cargar la página")
            pass
        input("Press Enter to continue...")
        self.close_driver()


    def close_modal(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="sui-dialog__body"]'))
            )
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="sui-dialog__body"]//span[@class="sui-icon-common__wrap icon-close homepage-she-close"] | //div[@class="sui-dialog__body"]//div[@class="dialog-header-v2__close-btn"]/*'))
            )
            close_button.click()
            return True
        except (TimeoutException,NoSuchElementException) as e:
            print(f"No se encontró el modal o el botón de cierre. Error: {str(e)}")
            return False



    def close_driver(self):
        self.driver.quit()




    def extract_data_soup(self):
        try:
            scripts = self.soup.find_all("script")
            pattern = r"window\.gbRawData\s*=\s*(\{.*?\"styles\":\s*\"\".*?\})"
            
            for script in scripts:
                if 'window.gbRawData' in script.text:
                    # Normalizar el texto del script eliminando saltos de línea
                    script_text = script.text.replace('\n', ' ').replace('\r', '').strip()

                    match = re.search(pattern, script_text, re.DOTALL)
                    
                    if match:
                        raw_data = match.group(1)
                        raw_data = raw_data.replace('\"', '"').replace("\\'", "'")
                        try:
                            data_dict = json.loads(raw_data)
                            return data_dict  # Procesa el diccionario según sea necesario
                        except json.JSONDecodeError as decode_err:
                            print(f"Error de decodificación de JSON: {decode_err}")
                            return None
                        
                        break
            return None
        except Exception as e:
            print(f"Error al extraer la información del producto: {str(e)}")
            return None



    def close_banner(self):
        try:
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="c-quick-register j-quick-register c-quick-register__enes"]//div[@class="quickg-outside"]'))
            )
            close_button.click()

            return True
        except Exception as e:
            print("No se encontró el banner de registro rápido")
            return False


    def structure_data(self,data):
        try:
            product_data = defaultdict(list)
            #product_data["sku"] = data["goodsId"]
            sku=data["currentGoodsId"]
            print(type(data))  
            print(type(product_data))
            #variantes=data["productIntroData"]["attrSizeList"][sku]
            variantes=data.get('productIntroData',{}).get('attrSizeList',{}).get('sale_attr_list',{}).get(sku,{}).get('sku_list')
            print(variantes)
            if variantes:
                
                for variante in variantes:
                    print(variante)



        except Exception as e:
            print(f"Error al estructurar los datos: {str(e)}")
            return None






    def capture_image_size(self, extension):
        try:

            container=self.driver.find_element(By.XPATH, '//div[@class="product-intro__size-help"]')
            elemento=container.find_element(By.XPATH,".//div[@class='product-intro__size-guide']")

            elemento.click()
            self.driver.implicitly_wait(2)
            # Espera a que el contenedor esté presente en la página
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="sui-dialog__wrapper sui-dialog__W720"]'))
            )
            
            # Localiza el elemento que contiene la imagen
            image = self.driver.find_element(By.XPATH, '//div[@class="sui-dialog__wrapper sui-dialog__W720"]//div[@class="sui-dialog__body"]')
            
            # Toma la captura de pantalla y la guarda con la extensión especificada
            image.screenshot(f"image.{extension}")
            
            return True  # Retorna True si todo salió bien
        
        except Exception as e:
            # Maneja cualquier excepción (puedes registrar el error si es necesario)
            print(f"Error al capturar la imagen: {e}")
            return False


def main():
    shein_controller = SheinController()
    shein_controller.extract_info()


if __name__ == "__main__":
    main() 