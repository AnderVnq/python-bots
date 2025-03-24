from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict
import asyncio
import time
import os
import requests
import re
import json
from models.entities.ecomerce.shein.shein_processor import SheinProcessor
import traceback
import aiofiles
import requests
import aiohttp
import asyncio
import pdfkit
import imghdr
import socket
import shutil
import html
import os
import re
from pathlib import Path
from pdf2image import convert_from_path
from urllib.parse import urljoin
from models.entities.logs.bug_logger import BugLogger
from shared.user_agents import user_agents,blocked_endpoints
import random
from solver_captcha_individual_detect import *
import tempfile



class SheinController():
    def __init__(self, language='en_US'):
        self.language = language
        self.driver = self.init_driver()
        self.url_base = "https://us.shein.com/"
        self.url_base_usa="https://us.shein.com/"
        self.soup = None
        self.shn_proc = SheinProcessor()
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
        self.emails=["luispubg9905@hotmail.com","anderson_escorpio_122@hotmail.com","ndrsnvenegas♠gmail.com"]
        self.password="Heaveny2"
        self.email_index = 0  # Índice para controlar el cambio de email
        self.email = self.emails[self.email_index] 
        self.icon_detector=None
 
    def init_driver(self):
            """ Inicializa el WebDriver con las opciones deseadas """
            # headers = {
            #     'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            #     'Accept': "*/*",
            #     'Accept-Language': self.language,
            #     'Accept-Encoding': "gzip,deflate,br",
            #     'Connection': "keep-alive"
            # }
            user_agent=random.choice(user_agents)
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
            #prefs = {"profile.managed_default_content_settings.images": 2}
            #opts.add_experimental_option("prefs", prefs)
            opts.add_argument("--ignore-certificate-errors")
            opts.add_argument(f'User-agent={user_agent}')
            driver= webdriver.Chrome(options=opts,)
            return driver


    def login_data(self,refresh=True,change_email=False)->bool:


        if change_email:
            # Mover al siguiente email en el ciclo
            self.email_index = (self.email_index + 1) % len(self.emails)
            self.email = self.emails[self.email_index]
        
        current_email = self.email
        if refresh:
            self.driver.get(self.url_base_usa+"user/auth/login")
        try:
             
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="page__login-newUI-continue"]'))
            )

            container_input_email= self.driver.find_element(By.XPATH,"//div[@class='email-recommend-input']")
            input_email=container_input_email.find_element(By.XPATH,".//div//input")
            input_email.click()


            for letra in current_email:
                input_email.send_keys(letra)
                time.sleep(random.uniform(0.2,0.4))

            WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.XPATH,"//div[@class='actions']//div[@class='login-point_button']/button"))
            )

            container_click_button=self.driver.find_element(By.XPATH,"//div[@class='actions']//div[@class='login-point_button']/button")
            container_click_button.click()
            
            #contraseña 

            WebDriverWait(self.driver, 7).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="main-content"]'))
            )


            #//div[@class="main-content"]//div[@class="page__login_input-filed page__login-newUI-input"]//div[@class="sui-input"]//input
            container_modal=self.driver.find_element(By.XPATH,'//div[@class="main-content"]')

            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="main-content"]//div[@class="sui-input"]//input[@type="password" and @aria-label="Contraseña:"]'))
            )
            input_password=container_modal.find_element(By.XPATH,'.//div[@class="sui-input"]//input[@type="password" and @aria-label="Contraseña:"]')
            input_password.click()
            #actions_password=ActionChains(self.driver)

            for letra in self.password:
                #actions_password.send_keys(letra)
                input_password.send_keys(letra)
                time.sleep(random.uniform(0.3,0.5))

            WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.XPATH,".//div[@class='actions']//div[@class='login-point_button']/button"))
            )

            continue_click=container_modal.find_element(By.XPATH,'.//div[@class="actions"]//div[@class="login-point_button"]/button')
            current_url=self.driver.current_url
            continue_click.click()

            #input("en el click de identificate")

            try:
                WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located((By.XPATH,'//div[@class="sui-dialog__body"]//div[@class="skip"]'))
                )
                click_skip=self.driver.find_element(By.XPATH,'//div[@class="sui-dialog__body"]//div[@class="skip"]/span')
                click_skip.click()
            except Exception as e:
                print(e)
                return False

            if self.driver.current_url==current_url:
                return False
            
            return True
        except Exception as e:
            print(e)
            return False



    def get_product_list(self,platform : str = 'Shein'):

        response =  self.shn_proc.get_product_list_proc(platform,self.on_device_process)
        if response:
            self.set_sku_data_list(response)

            if self.login_data():
                self.update_data_sku_price()
            else:
                print("Error al iniciar sesión")
                return

    def is_found_data(self):
        return self.is_found
        
    def update_data_sku_price(self):
        sku_list= self.get_sku_data_list()
        if not sku_list:
            return
        self.lenght_sku_list = len(sku_list)
        try:
            
            # if not self.login_data():
            #     print("Error al iniciar sesión")
            #     return

            for index,data in enumerate(sku_list):

                if data.get("product_id", None).strip() and bool(int(data.get("is_parent", False))) and not bool(int(data.get("get_variation", 0))):
                    url=self.url_base+f"product-p-{data['product_id']}.html?languaje=es"
                    self.url_complete=self.url_base_usa+f"product-p-{data['product_id']}.html"
                    self.driver.get(url)
                    self.extract_info(index)
                    self.url_complete=None
                
                elif data.get("product_id","").strip() and bool(int(data.get("is_parent",0))) and bool(int(data.get("get_variation",0))):
                    url=self.url_base+f"product-p-{data['product_id']}.html?languaje=es"
                    self.driver.get(url)
                    self.extract_variantes(index)
                    self.url_complete=None
                else:
                    pass
            self.sku_data=None
        except Exception as e:
            print(f"Error al actualizar los datos: {str(e)}")
            traceback.print_exc()
        


    def set_sku_data_list(self,data):
        self.sku_data = data

    def get_sku_data_list(self):
        return  self.sku_data
    def affected_data(self):
        return self.affected_rows
    
    def updated_rows(self, affected : int):
        
        if self.affected_rows is None:
            self.affected_rows = 0 
        self.affected_rows += affected
    




    def obtains_img_captcha(self,refresh_img:bool=True):

        try:

            if refresh_img:
                click_refresh=WebDriverWait(self.driver,5).until(
                    EC.element_to_be_clickable((By.XPATH,"//div[@class='captcha_btn_click_wrapper']//div[@class='captcha_click_refresh']"))
                )
                
                click_refresh.click()
            
            container_img=WebDriverWait(self.driver,5).until(
                EC.presence_of_element_located((
                    By.XPATH,"//div[@class='captcha_click_wrapper']"
                ))
            )

            img_captcha=container_img.find_element(By.XPATH,".//div[@class='pic_wrapper']")
            time.sleep(1)
            style_attribute=img_captcha.get_attribute("style")
            img_captcha_url=style_attribute.replace("background-image: url('","").replace("')","")
            match = re.search(r'url\("?(.*?)"?\)', style_attribute)
            if match:
                image_url = match.group(1)
                print("URL de la imagen:", image_url)
                response=requests.get(image_url)
                if response.status_code==200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                        temp_file.write(response.content)
                        return temp_file.name
        except Exception as e:
            return



    def mover_mouse_naturalmente(self, elemento, destino_x, destino_y, pasos=30, delay=0.02):
        """
        Mueve el mouse en una ruta curva hasta el destino y luego hace clic.
        
        :param driver: Instancia de Selenium WebDriver.
        :param elemento: Elemento sobre el cual se moverá el mouse.
        :param destino_x: Coordenada X final relativa al elemento.
        :param destino_y: Coordenada Y final relativa al elemento.
        :param pasos: Número de movimientos intermedios.
        :param delay: Tiempo entre cada paso.
        """
        
        self.driver.execute_script("""
            var elem = arguments[0];
            var rect = elem.getBoundingClientRect();
            var destino_x = arguments[1] + rect.left + window.scrollX;
            var destino_y = arguments[2] + rect.top + window.scrollY;
            
            // Obtener la posición inicial del cursor
            var cursor_x = rect.left + rect.width / 2;
            var cursor_y = rect.top + rect.height / 2;
            
            var pasos = arguments[3];
            var delay = arguments[4];

            function easeOutQuad(t) {
                return t * (2 - t);
            }

            function moverMouse(index) {
                if (index > pasos) {
                    setTimeout(() => {
                        var clickEvent = new MouseEvent('click', {bubbles: true, clientX: destino_x, clientY: destino_y});
                        elem.dispatchEvent(clickEvent);
                        
                        // Dibujar un círculo en la posición de clic
                        var circle = document.createElement('div');
                        circle.style.width = '10px';
                        circle.style.height = '10px';
                        circle.style.background = 'red';
                        circle.style.borderRadius = '50%';
                        circle.style.position = 'absolute';
                        circle.style.top = destino_y - 5 + 'px';
                        circle.style.left = destino_x - 5 + 'px';
                        circle.style.zIndex = '9999';
                        document.body.appendChild(circle);
                        setTimeout(() => { circle.remove(); }, 1000);

                    }, delay * 1000);
                    return;
                }

                var t = easeOutQuad(index / pasos);
                var nuevo_x = cursor_x + (destino_x - cursor_x) * t + (Math.random() - 0.5) * 5;
                var nuevo_y = cursor_y + (destino_y - cursor_y) * t + (Math.random() - 0.5) * 5;

                var moveEvent = new MouseEvent('mousemove', {bubbles: true, clientX: nuevo_x, clientY: nuevo_y});
                elem.dispatchEvent(moveEvent);

                setTimeout(() => moverMouse(index + 1), delay * 1000);
            }

            moverMouse(0);
        """, elemento, destino_x, destino_y, pasos, delay)



   
    def solver_click_captcha(self, temp_img_path: str):
        MAX_INTENTOS = 4  # Número máximo de intentos

        # if not hasattr(self, 'icon_detector') or self.icon_detector.image_path != temp_img_path:
        #self.icon_detector = IconDetector(temp_img_path, filtro_tipo="grey")
        for intento in range(1, MAX_INTENTOS + 1):
            print(f"Intento {intento} de {MAX_INTENTOS}")

            if temp_img_path:
                self.icon_detector = IconDetector(temp_img_path,filtro_tipo="grey")
                self.icon_detector.recortar_secciones()
                self.icon_detector.detectar_keypoints()
                self.icon_detector.encontrar_coincidencias()
                self.icon_detector.mostrar_coincidencias_por_icono()
                puntos = self.icon_detector.mostrar_resultado_final()

                if puntos and len(puntos) > 3:
                    puntos = puntos[:3]
                elif puntos and len(puntos) <= 3:
                    print(f"Solo se encontraron {len(puntos)} puntos, se procederá con ellos.")
                if puntos:
                    for punto in puntos:
                        try:
                            # Clic en los puntos detectados
                            click_captcha = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[@class='captcha_click_wrapper']//div[@class='pic_wrapper']"))
                            )
                            self.mover_mouse_naturalmente(click_captcha, punto[0], punto[1])
                            time.sleep(1)
                            print(f"Punto clickeado en posición: {punto}")
                        except Exception as e:
                            continue
                

                confirmar_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='captcha_btn_click_wrapper']//div[@class='captcha_click_confirm']"))
                )

                confirmar_btn.click()

                if "captcha" not in self.driver.current_url:
                    print("Captcha resuelto con éxito.")
                    return True  # Salir de la función si se resolvió el CAPTCHA

                print("Captcha aún presente, refrescando y reintentando...")
                temp_img_path = self.obtains_img_captcha(refresh_img=False)

        print(f"No se pudo resolver el CAPTCHA después de {MAX_INTENTOS} intentos.")
        return False

                



    def extract_info(self,index:int):    
        self.driver.implicitly_wait(5)
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: "captcha" not in d.current_url
            )
            print("Acceso al producto exitoso:", self.driver.current_url)
        except:
            print("Captcha no resuelto automáticamente, por favor resuélvelo manualmente.")
            #self.driver.get("https://us.shein.com/login")
            # if not "captcha_type=905" in self.driver.current_url:
            #     url=self.driver.current_url
            #     new_url = url.replace("captcha_type", "captcha_type=905")
            #     self.driver.get(new_url)
            # path_img=self.obtains_img_captcha()
            # result_solve_captcha= self.solver_click_captcha(path_img)
            # if not result_solve_captcha:
            #     print("Error al resolver el CAPTCHA.")
            #     return
            response_logout=self.logout_data()
            if response_logout:
                print("Acceso al producto exitoso:", self.driver.current_url)
            else:
                print("Error al cerrar sesión.")
                self.product_data_not_found_api_ctrl(index)
                return

            


        # Si se logra salir del CAPTCHA, continuar con el scraping
        #self.driver.get(self.url_base+f"product-p-{data['product_id']}.html?languaje=es")   
        # if "captcha" not in self.driver.current_url:
        #     print("Página del producto lista para el scraping.")
        # else:
        #     print("Permaneciendo en la página del CAPTCHA.")
        #     return
        try:
            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            response_json=self.extract_data_soup()
            if response_json:
                print("Información extraída con éxito")
                self.update_price_data(response_json,index)
            else:
                print("Error al extraer la información en extract_info")
            self.soup=None
        except Exception as e:
            print(e)
            print("Error al cargar la página")
            self.product_data_not_found_api_ctrl(index)

    def close_driver(self):
        self.driver.quit()


    def product_data_not_found_api_ctrl(self, index):
        data = self.sku_data[index]
        curret_time = self.current_time()
        for kynf, valnf in enumerate(data["child"]):
            data["child"][kynf]["is_capture"] = 0
            data["child"][kynf]["fail_times"] = int(valnf.get("fail_times", 0)) + 1
            data["child"][kynf]["last_updated"] = curret_time
            data["child"][kynf]["searched_times"] = int(valnf.get("searched_times", 0)) + 1
            data["child"][kynf]["searched_fail"] = int(valnf.get("searched_fail", 0)) + 1
            data["child"][kynf]["quantity"] = 0
            data["child"][kynf]["stock"] = 0
        self.validate_data(index) 


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
            return None
        except Exception as e:
            print(f"Error al extraer la información del producto en data_soup")
            return None


    def current_time(self):
        current_time = datetime.now()
        formatted_current_time = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
        return formatted_current_time    

    def update_price_data(self,data:list[dict],index:int):
        try:

            db_data=self.sku_data[index]
            current_time = self.current_time()
            parent={}
            price=None
            sku=data["currentGoodsId"]
            product_id = data["currentGoodsId"].strip().upper()
            goods_sn = data["currentGoodsSn"].strip().upper()
            try:
                variantes = (
                    data.get('productIntroData', {})
                    .get('attrSizeList', {})
                    .get('sale_attr_list', {})
                    .get(sku, {})
                    .get('sku_list', [])
                )
            except (KeyError, TypeError):
                variantes = []  # Si hay un error, se asigna una lista vacía


            print("En structure data")
            for key,value in enumerate(db_data["child"]):
                
                compare_sku= value.get("sku").strip().upper() if value else None
                
                if(compare_sku==product_id) or (compare_sku==goods_sn):
                    
                    price_src=data.get("productIntroData",{}).get('getPrice',{}).get('salePrice',{}).get('amount') or data.get('getPrice',{}).get('salePrice',{}).get('usdAmount')
                    price = price_src if price_src else None

                    db_data["child"][key]["original_price"]=price
                    try:
                        quantity = data.get('productIntroData', {}).get('detail', {}).get('stock')
                        if quantity is not None and str(quantity).isdigit():
                            quantity = int(quantity)
                        else:
                            quantity = None
                        in_stock = 1 if quantity is not None and quantity >= int(value["min_quantity"]) else 0
                    except Exception as e:
                        print(f"Error al procesar los datos: {e}")
                        quantity = None
                        in_stock = 0
                    db_data["child"][key]["stock"] = in_stock
                    db_data["child"][key]["quantity"] = quantity

                    if not bool(int(value.get("product_name_saved", 0))) and bool(int(value.get("verify_name", 0))):
                        product_name_src= data.get('productIntroData',{}).get('detail',{}).get('goods_name')
                        if product_name_src:
                            product_name_title=product_name_src.title()
                            db_data["child"][key]["product_name"]=product_name_title

                    if not bool(int(value.get("description_saved", 0))) and bool(int(value.get("verify_description", 0))):
                        list_atributes=data.get("productIntroData", {}).get("detail", {}).get("productDetails",None)
                        product_description_src=self.set_product_description_ctrl(list_atributes)
                        db_data["child"][key]["product_description"]=product_description_src  
                    
                    if not bool(int(value.get("color_saved", 0))) and bool(int(value.get("verify_color", 0))):
                        
                        color=self.get_color_crtl(data)
                        db_data["child"][key]["color"]=color


                    if not bool(int(value.get("is_exist_file", 0))) and bool(int(value.get("verify_images", 0))):
                        db_data["child"][key]["own_image"] = 1
                        qty_img = self.image_product_limit()
                        initial_img_val = self.initial_detail_images_list()
                        for prop in initial_img_val:
                           if prop in db_data["child"][key]:
                               db_data["child"][key][prop] = None
                        

                        main_image_url=data.get('productIntroData',{}).get('detail',{}).get('original_img')
                        print("Main image url",main_image_url)
                        if main_image_url:
                            if not main_image_url.startswith("http://") and not main_image_url.startswith("https://"):
                                main_image_url = "http:" + main_image_url
                        db_data["child"][key]["main_image_url"]=main_image_url
                        list_images=data["productIntroData"]["goods_imgs"]["detail_image"]
                        hires_images = self.get_product_images_api_ctrl(qty_img,list_images)
                        db_data["child"][key]["hires_images"] = hires_images
                        resp_main_img = asyncio.run(self.download_image(db_data["sku"],db_data["child"][key].get('main_image_url'),"main"))     

                        db_data["child"][key]["main_image_url"] = resp_main_img['url']  if resp_main_img["status"] else None

                        resp_multi_img =  asyncio.run(self.download_multiple_images(db_data["sku"],db_data["child"][key].get('hires_images')))

                        if resp_multi_img:
                            for ky, url_val in enumerate(resp_multi_img):
                                    key_res = url_val["name"]
                                    if key_res in db_data["child"][key]:
                                        db_data["child"][key][key_res] = url_val.get("url",None)
                        if variantes is not None:    #Captura la tabla tallas
                           result_size = self.size_structure_data_ctrlv2(data)
                           if result_size is not None:
                                result_path =  asyncio.run(self.html_structure(result_size,value["sku"].lower()))
                                if result_path["success"]:
                                    db_data["child"][key]["image_size_link"] = result_path["output_path"]
                                    for ind, img_prop in enumerate(initial_img_val):
                                        if not db_data["child"][key].get(f"image_{ind}"):
                                            db_data["child"][key][f"image_{ind}"] = result_path["output_path"].strip()
                                            break

                                    if os.path.exists(result_path["temp_output"]):
                                        os.unlink(result_path["temp_output"])
                        del db_data["child"][key]["hires_images"]
                        #print("data\n",db_data["child"][key])

                    db_data["child"][key]["last_updated"] = current_time
                    db_data["child"][key]["searched_times"] = int(value["searched_times"]) + 1

                    if price is not None:
                        db_data["child"][key]["is_capture"] = 1
                    else:

                        db_data["child"][key]["searched_fail"] = int(db_data["child"][key]["searched_fail"]) + 1
                        db_data["child"][key]["is_capture"] = 0

                        if int(db_data["child"][key]["searched_fail"]) >= 2:
                            db_data["child"][key]["stock"] = 0
                           
                    parent=db_data["child"][key]
                    break
            print("Paso el primer break")
            if variantes is not None:
                for key,value in enumerate(db_data['child']):
                    for variante in variantes:
                        if value["sku_code"] == variante["sku_code"]:
                            if not bool(int(value["size_saved"])) and bool(int(value["verify_size"])):
                                print("entro a size")
                                size_src=variante["sku_sale_attr"][0]["attr_value_name_en"]
                                print("talla",size_src)
                                db_data["child"][key]["size"]=size_src.strip().upper()

                            price_src_temp=price
                            price_child=price_src_temp if price_src_temp else None
                            db_data["child"][key]["original_price"]=price_child
                            qty = variante["stock"] if "stock" in variante and str(variante["stock"]).strip().isdigit() else 0

                            is_stock = 1 if qty >= int(value["min_quantity"]) else 0
                            db_data["child"][key]["stock"] = is_stock
                            db_data["child"][key]["quantity"] = qty

                            if not bool(int(value["brand_saved"])) and bool(int(value["verify_brand"])):
                                brand_src = parent["brand"]
                                if brand_src is not None:
                                    db_data["child"][key]["brand"] = brand_src.strip().upper()

                            if not bool(int(value["product_name_saved"])) and bool(int(value["verify_name"])):
                                product_name_src = parent["product_name"].strip()
                                db_data["child"][key]["product_name"] = product_name_src

                            if not bool(int(value["description_saved"])) and bool(int(value["verify_description"])):
                                db_data["child"][key]["product_description"] = parent["product_description"]

                            if not bool(int(value["color_saved"])) and bool(int(value["verify_color"])):
                                db_data["child"][key]["color"] = parent["color"]

                            if not bool(int(value["is_exist_file"])) and bool(int(value["verify_images"])):

                                #images_list_ch = sku.get("currentSkcImgInfo", {})#reemplazar por data , osea related color y busca como hacer append a las variaciones por color y talla 
                                images_list_ch =data["productIntroData"]["goods_imgs"]["detail_image"]
                                # if (
                                # "skuImages" in images_list_ch and images_list_ch["skuImages"]
                                # and variante["sku_code"] in images_list_ch["skuImages"]
                                # and images_list_ch["skuImages"][variante["sku_code"]]
                                # ):
                                if images_list_ch and variante["sku_code"]:
                                    db_data["child"][key]["own_image"] = 1
                                    qty_img_c = self.image_product_limit()
                                    main_image_url_c = images_list_ch[0]["origin_image"].strip()
                                    if main_image_url_c:
                                        if not main_image_url_c.startswith("http://") and not main_image_url_c.startswith("https://"):
                                            main_image_url_c = "http:" + main_image_url_c
                                    print("en images lits child",main_image_url_c)
                                    db_data["child"][key]["main_image_url"] = main_image_url_c

                                    images_child =images_list_ch #[main_image_url_c]

                                    hires_images_c = self.get_product_images_api_ctrl(qty_img_c,images_child)
                                    db_data["child"][key]["hires_images"] = hires_images_c

                                    main_img_url_c = asyncio.run(self.download_image(value["sku"],db_data["child"][key].get('main_image_url'),"main"))                            
                                    db_data["child"][key]["main_image_url"] = main_img_url_c['url']  if main_img_url_c["status"] else None
                                    print("despues de main image url")
                                    resp_multi_img_c =  asyncio.run(self.download_multiple_images(value["sku"],db_data["child"][key].get('hires_images')))
                                    
                                    print("despues de multple images dowload")
                                    if resp_multi_img_c:
                                        for kyc, url_val_c in enumerate(resp_multi_img_c):
                                                key_value = url_val_c["name"]
                                                if key_value in db_data["child"][key]:#validar el primer key
                                                    db_data["child"][key][key_value] = url_val_c.get("url",None)

                                    if parent and "image_size_link" in parent and parent["image_size_link"]:
                                        name_child = value["sku"].lower().strip()
                                        ext_ch = Path(parent["image_size_link"]).suffix
                                        print("EXT_CH",ext_ch)
                                        file_name_src = os.path.basename(parent["image_size_link"])
                                        
                                        resp_img_size =  asyncio.run(self.copy_file(parent["sku"], name_child, file_name_src ,ext_ch))
                                       
                                        img_prop_li_ch = self.initial_detail_images_list()
                                        if resp_img_size["success"]:  #img_prop_li_ch["success"] :
                                            for ind, img_prop in enumerate(img_prop_li_ch):
                                                key_src_img = f"image_{ind}"
                                                if not db_data["child"][key].get(key_src_img):
                                                    db_data["child"][key][key_src_img] = resp_img_size["output_path"]
                                                    break
                                    
                                    del db_data["child"][key]["hires_images"]
                                else:
                                    db_data["child"][key]["own_image"] = 0
                                    initial_img_val = self.initial_detail_images_list()
                                    if initial_img_val:  
                                        for prop in initial_img_val:
                                            if prop in parent:
                                                db_data["child"][key][prop] = parent[prop]

                            print("No entro en is exists file")
                            db_data["child"][key]["last_updated"] = current_time
                            db_data["child"][key]["searched_times"] = int(value["searched_times"]) + 1

                            if price_child is not None:
                                db_data["child"][key]["is_capture"] = 1
                            else:
                                db_data["child"][key]["searched_fail"] = int(value["searched_fail"]) + 1
                                db_data["child"][key]["is_capture"] = 0
                                db_data["child"][key]["stock"] = 0
            print("antes de validate data")
            self.validate_data(index)
        except Exception as e:
            print(f"Error al estructurar los datos: {str(e)}")
            traceback.print_exc()


    async def copy_file(self,sku:str, new_name : str,old_name :str,extension:str):
        result = {
            "success": False,
            "output_path": None,
            "temp_output": None,
            "error": None
        }
        try:
            src_path = f"{self.images_path}/{sku.lower()}/{old_name}"
            dest_dir  = f"{self.images_path}/{new_name}"
            # Verificar si el directorio de destino existe y, si no, crearlo
            if not os.path.exists(dest_dir):
                print("Creando el directorio de destino")
                os.makedirs(dest_dir)
                
            print("Después de verificar el directorio de destino")

            # Aquí quitamos el '/' extra al inicio del nombre del archivo
            dest_image_path = os.path.join(dest_dir, f"{new_name}_size{extension}")
            # Intentar copiar el archivo
            shutil.copy(src_path, dest_image_path)

            output_path = f"{self.domain_path}{new_name}/"
            image_url_domain = urljoin(output_path, f"{new_name}_size{extension}")
            result["success"] = True
            result["output_path"] = image_url_domain
            print("RESULT",result)
            return result
        
        except Exception as e:
            print(f"Error al copiar el archivo: {str(e)}")
            log_list = self.logger.bug_logs_data(e)
            resp = self.shn_proc.bug_register_proc(log_list)
            return result



    def validate_data(self,index:int):
        data = self.sku_data[index]
        self.lenght_sku_list = len(self.sku_data)        
        for indx, val_dic in enumerate(data["child"]):
             data["child"][indx]["weight_saved"] = self.is_valid_proper(val_dic,"weight_in_kg")
             data["child"][indx]["is_exist_file"] = self.is_valid_images(val_dic)
             data["child"][indx]["product_name_saved"] = self.is_valid_proper(val_dic,"product_name")
             data["child"][indx]["description_saved"] = self.is_valid_proper(val_dic,"product_description")
             data["child"][indx]["brand_saved"] = self.is_valid_proper(val_dic,"brand")
             data["child"][indx]["dimension_saved"] = self.is_valid_dimension(val_dic)
             data["child"][indx]["size_saved"] = self.is_valid_proper(val_dic,"size")
             data["child"][indx]["color_saved"] = self.is_valid_proper(val_dic,"color")   
             data["child"][indx]["is_active"] = 0   
             data["child"][indx]["extraction"] = 0
             data["child"][indx]["processing"] = 0
             data["child"][indx]["process_app"] = None
             data["child"][indx]["from_app"] = self.on_device_process
             self.sku_detail.append(data["child"][indx])
             self.updated_rows(1)
        self.sku_data[index] = None
        self.batching_data(index) 



    def is_valid_proper(self,data:dict,prop:str):

        if prop in data:
            return 1 if data.get(prop) is not None else 0
        return 0


    def batching_data(self, index : int):
        if (index + 1) % self.batch_size == 0 or index + 1 == self.lenght_sku_list:
            self.shn_proc.update_shein_sku_list_proc(self.sku_detail,self.batch_size)
            self.sku_detail = []


    def is_valid_images(self,data):
        if (
            data.get("image_thumbnail") 
            or data.get("main_image_url") 
            or data.get("image_0") 
            or data.get("image_1") 
            or data.get("image_2") 
            or data.get("image_3") 
            or data.get("image_4") 
            or data.get("image_5") 
            or data.get("image_size_link")
        ):
            return 1
        return 0
    
    def is_valid_dimension(self,data):
        if (
            data.get("height") 
            or data.get("width") 
            or data.get("length") 
        ):
            return 1
        return 0

    def image_product_limit(self):
        qty = 3
        return qty
    
    async def download_multiple_images(self, sku, image_links):
        max_images = min(5, len(image_links))  # Limitar a 5 imágenes o menos si hay menos URLs
        image_links = image_links[:max_images]

        # Crear tareas para descargar las imágenes en paralelo
        tasks = [
            self.download_image(sku, image.get("url"), f"{i}")
            for i, image in enumerate(image_links)
        ]

        # Ejecutar todas las descargas en paralelo
        results = await asyncio.gather(*tasks)

        # Crear un nuevo array de objetos para almacenar las URLs descargadas en orden
        downloaded_images = []
        for i, result in enumerate(results):
            image_data = {
                "name": f"image_{i}",
                "url": result["url"] if result["status"] else None  # Asigna la URL o None si falló
            }
            downloaded_images.append(image_data)  # Añadir el objeto al array en orden

        return downloaded_images


    def get_product_images_api_ctrl(self, img_qty : int, product_images : list = [], base_url : str  = None):
        hi_resolution_imgs = []
        
        for ky, value_img in enumerate(product_images):
            if img_qty > ky:
                hi_resolution_imgs.append({'url': value_img["origin_image"].strip()})#["clave de la img origin_image"]
        
        product_images = []
        return hi_resolution_imgs


    async def download_image(self,sku, image_link : str = None, file_name : str = None):
        try:
            image_url = self.sanitize_image_url(image_link)

            if not image_url.startswith("http://") and not image_url.startswith("https://"):
                image_url = "http:" + image_url  # Añadir http:// si no tiene esquema

            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=None) as response:
                    if response.status == 200:

                        image_data = await response.read()
                        extension = f".{imghdr.what(None, h=image_data)}" if imghdr.what(None, h=image_data) else None

                        image_name = f"{self.images_path}/{sku.lower()}/{sku.lower()}_{file_name}{extension}"
                        # Crear el directorio si no existe
                        os.makedirs(os.path.dirname(image_name), exist_ok=True) 

                        # Guardar la imagen localmente de manera asíncrona
                        async with aiofiles.open(image_name, 'wb') as f:
                            await f.write(image_data)  # Escribir la imagen en el archivo

                        # Generar la URL local (suponiendo que estás sirviendo los archivos desde un servidor)
                        local_url = f"{self.domain_path}{sku.lower()}/{sku.lower()}_{file_name}{extension}"
                        return {"url": local_url, "status": True,"message":"success"}
                    else:
                        return {"url": image_url, "status": "error", "message": f"Error al descargar thumbnail: {response.status}"}
            return {"url": "asdas", "status": True,"message":"success"}
        except asyncio.TimeoutError as e:
            print(f"Error en dowload imgs 1 {str(e)}")
            print(str(e))
            print("despues del str e ")
            traceback.print_exc()
            log_list = self.logger.bug_logs_data(e)
            resp = self.shn_proc.bug_register_proc(log_list)
            return {"url": image_url, "status": False, "message": "Timeout al descargar thumbnail"}
        except Exception as e:
            print(f"Error en dowload imgs 2")
            print(str(e))
            print("despues del str e ")
            traceback.print_exc()
            log_list = self.logger.bug_logs_data(e)
            resp = self.shn_proc.bug_register_proc(log_list)
            return {"url": image_url, "status": False, "message": f"Error inesperado al descargar thumbnail: {e}"}
    

    def sanitize_image_url(self, url):
        find_text = ["_wk_", "_wk_shein"]
        replace_text = ["_", ""]

        url_ext_changed = url.replace('webp', 'jpg')

        cleared_url = url_ext_changed
        for find, replace in zip(find_text, replace_text):
            cleared_url = cleared_url.replace(find, replace)

        return cleared_url


    def replace_size(self,value):
            replace = {
                '1XL': 'XL',
                '0XL': 'L'
            }
            if value: 

                value = value.strip().upper()

                contiene_reemplazos = any(clave in value for clave in replace.keys())
                
                if contiene_reemplazos:
                
                    for old, new in replace.items():
                        value = value.replace(old, new)
                    return value

            return value


    def initial_detail_images_list(self):
        image_props = [
            "main_image_url",
            "image_thumbnail",
            "image_size_link",
            "image_0",
            "image_1",
            "image_2",
            "image_3",
            "image_4",
            "image_5"
        ]

        return image_props
    

    def set_product_description_ctrl(self,atributes):
        # se hace con el html de la pagina 
        try:

            ul='<ul>'
            agrupar_data=defaultdict(list)

            for  atr in atributes:
                key= atr["attr_name"]
                value=atr["attr_value"]
                agrupar_data[key].append(value)

            
            for ky,values in agrupar_data.items():
                ul+=f'<li>{ky}: {", ".join(values)}</li>'

            ul+'</ul>'
            
            return ul
        except Exception as e:
            print(f"Error en product description (ul): {str(e)}")
            return None


    def get_color_crtl(self,data:dict):

        color = None
        try:
            color_src= data['productIntroData']['detail']["mainSaleAttribute"][0]["attr_value"]
            color = color_src.title()
            return color
        except Exception as e:
            try:
                main_container = self.soup.select_one('.goods-color__title.j-expose__product-intro__color-title')

                # Buscar dentro del contenedor principal el elemento 'sub-title'
                if main_container:
                    sub_title = main_container.select_one('.sub-title')
                    if sub_title:
                        color_text = sub_title.get_text(strip=True).replace(':', '').strip()
                        return color_text
            except Exception as e:
                print(f"Error al obtener el color: {str(e)}")
                return None

    def size_structure_data_ctrl(self, data):
        data_size = []
        structured_data = {}

        for attr in data[0]["attr_value_list"]:
            talla = attr.get("attr_value_name")
            local_size = None

            # Buscar el tamaño local para el código de país 'EU'
            if "attr_value_local_size" in attr:
                for local_size_entry in attr["attr_value_local_size"]:
                    if local_size_entry.get("country_code") == "EU":
                        local_size = local_size_entry.get("attr_local_size_value")
                        break

            # Procesar attrDescPopUp si está presente y no está vacío
            if "attrDescPopUp" in attr and attr["attrDescPopUp"]:
                for desc in attr["attrDescPopUp"]:
                    multi_part_name = desc.get("multiPartName", "Medidas del producto (cm)").strip()
                    
                    # Inicializar structured_data[multi_part_name] si no existe
                    if multi_part_name not in structured_data:
                        structured_data[multi_part_name] = {
                            "title": multi_part_name,
                            "headers": ["Talla", "EU" if local_size else None],
                            "data": []
                        }
                    
                    current_data = structured_data[multi_part_name]["data"]
                    found = False
                    
                    # Buscar filas existentes que coincidan
                    for existing_row in current_data:
                        if existing_row[0] == talla and existing_row[1] == local_size:
                            for bind_attr in desc["bindAttrData"]:
                                attr_name_key = bind_attr["attrNameKey"]
                                index = structured_data[multi_part_name]["headers"].index(attr_name_key) \
                                    if attr_name_key in structured_data[multi_part_name]["headers"] else -1
                                if index != -1:
                                    existing_row[index] = self.size_handle_data_ctrl(bind_attr["attrNameValue"])
                            found = True
                            break

                    # Si no se encuentra, crear una nueva fila
                    if not found:
                        new_row = [talla, local_size]
                        for bind_attr in desc["bindAttrData"]:
                            attr_name_key = bind_attr["attrNameKey"]
                            if attr_name_key not in structured_data[multi_part_name]["headers"]:
                                structured_data[multi_part_name]["headers"].append(attr_name_key)
                            index = structured_data[multi_part_name]["headers"].index(attr_name_key)
                            if len(new_row) <= index:
                                new_row.extend([None] * (index + 1 - len(new_row)))
                            new_row[index] = self.size_handle_data_ctrl(bind_attr["attrNameValue"])
                        current_data.append(new_row)

        data_size = list(structured_data.values())
        return data_size
    
    def size_handle_data_ctrl(self, text):

        text = re.sub(r'\s*inch\s*', '', text, flags=re.IGNORECASE)

        match = re.search(r'[\/-]', text)
        if match:
            delimiter = match.group(0)
            parts = text.split(delimiter)
        else:
           
            parts = [text]
            delimiter = ''
       
        converted_parts = []
        for part in parts:
            part = part.strip()

            if str(part).isnumeric() or (str(part).replace('.', '', 1).isdigit() and str(part).count('.') < 2):
                cm_value = self.format_number_ctrl(self.inches_to_cm_ctrl(float(part)))
                converted_parts.append(str(cm_value))
            else:
                converted_parts.append(part)

       
        result = delimiter.join(converted_parts)
        return result

    def format_number_ctrl(self, text_num, allow_digit = 2):
        # Convertir el número en texto y luego a flotante
        number = float(re.sub(r'[^\d.]', '', str(text_num)))
        # Redondear a la cantidad de dígitos permitidos sin agregar corchetes
        formatted_number = round(number, allow_digit)
        return formatted_number
    
    def inches_to_cm_ctrl(self, inch):
        cm = inch * 2.54
        return cm

    def size_structure_data_ctrlv2(self, data_v):

        data_size = []
        structured_data = {}
        try:
            data=data_v.get("productIntroData", {}).get("sizeInfoDes", {}).get("sizeInfo", [])
        except Exception as e:
            return data_size
        
        for item in data:
            talla = item.get("attr_value_name")
            
            # Buscar las medidas en cm o pulgadas y convertir si es necesario
            for key, value in item.items():
                # Excluir las claves que no son medidas
                if key not in ["attr_id", "attr_name", "attr_value_id", "attr_value_name", "attr_value_name_en"]:
                    medida = value.strip()
                    
                    # Si la medida está en cm
                    if "cm" in medida:
                        # Extraer el valor en cm y agregarlo
                        value_in_cm = self.extract_value_in_cm(medida)
                        self.add_measurement(structured_data, talla, key, value_in_cm)
                    
                    # Si la medida está en pulgadas
                    elif "inch" in medida.lower():
                        # Extraer el valor en pulgadas y convertirlo a cm
                        value_in_inches = self.extract_value_in_inches(medida)
                        value_in_cm = self.inches_to_cm_ctrl(value_in_inches)
                        self.add_measurement(structured_data, talla, key, value_in_cm)

        # Convertir los datos estructurados en una lista
        data_size = list(structured_data.values())
        return data_size

    def extract_value_in_cm(self, medida):
        # Extraer el valor numérico de la medida en cm
        match = re.search(r"([\d\.]+)\s*cm", medida)
        if match:
            return float(match.group(1))
        return None

    def extract_value_in_inches(self, medida):
        # Extraer el valor numérico de la medida en pulgadas (si existe)
        match = re.search(r"([\d\.]+)\s*(inch|in)", medida, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    def add_measurement(self, structured_data, talla, key, value):
        # Si no existe el multi_part_name, lo inicializamos
        if key not in structured_data:
            structured_data[key] = {
                "title": key,
                "headers": ["Talla", "Medida en cm"],
                "data": []
            }

        current_data = structured_data[key]["data"]
        found = False

        # Verificar si la talla ya existe en los datos estructurados
        for existing_row in current_data:
            if existing_row[0] == talla:
                existing_row[1] = value  # Actualizamos el valor de la medida
                found = True
                break

        # Si no se encuentra la talla, agregar una nueva fila
        if not found:
            new_row = [talla, value]
            current_data.append(new_row)


    async def html_structure(self,data_size,sku):

        result = {
            "success": False,
            "output_path": None,
            "temp_output": None,
            "error": None
        }

        try:
                
            config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
            #config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
            options = {"quiet": ""}

            content_group = ""
            data_table = None

            for row in data_size:
                content_group += f'<div class="content_group">'
                content_group += f'<div class="table-title">{html.escape(row.get("title", ""))}</div>'
                data_table = "<table><tr>"

               
                for head in row.get("headers", []):  # Crear encabezados de la tabla
                    data_table += f"<th>{html.escape(head or '')}</th>"

                data_table += "</tr>"

                
                for data_row in row.get("data", []):    # Crear filas de datos
                    data_table += "<tr>"
                    for info in data_row:
                        td_data = self.replace_size(str(info))
                        data_table += f"<td>{html.escape(td_data or '')}</td>"
                    data_table += "</tr>"

                data_table += "</table>"
                content_group += data_table
                content_group += '</div>'
                data_table = None

                html_structure = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Table</title>
                    <style>
                        html{{
                            display: flex;
                            align-items: center;
                            flex-direction: column;
                            gap: 16px;
                            justify-content: center;
                            width: 100%;
                        }}
                        body{{
                            max-width: 1024px;
                            display: flex;
                            align-items: center;
                            flex-direction: column;
                            gap: 30px;
                            justify-content: center;
                            width: 100%;
                            
                        }}
                        .content_group{{
                        width: 100%;
                        padding: 12px;
                        }}
                
                        table {{
                            width: 100%;
                            border-collapse: separate;
                            border-spacing: 0;
                            border: 1px solid #9f9f9f; /* Añadir borde alrededor de la tabla */
                            border-radius: 10px; /* Añadir borde redondeado */
                            overflow: hidden; /* Para aplicar el borde redondeado correctamente */
                        }}

                        th{{
                            color:#222;
                            font-size: 12px;
                        }}  
                        
                        td{{
                        font-size: 12px;
                        }}
                
                        th, td {{
                            padding: 6px;
                            text-align: left;
                            border-bottom: 1px solid #9f9f9f; /* Añadir borde inferior a cada celda */
                        
                        }}
                        th:first-child, td:first-child {{
                            color: #222 !important;
                            font-weight:600;
                        }}
                
                        tr:last-child th, tr:last-child td {{
                            border-bottom: none; /* Quitar borde inferior de la última fila */
                        }}

                        th:first-child, td:first-child {{
                            border-left: 1px solid #9f9f9f; /* Añadir borde izquierdo a la primera celda */
                        }}

                        th:last-child, td:last-child {{
                            border-right: 1px solid #9f9f9f; /* Añadir borde derecho a la última celda */
                        }}

                        .table-title {{
                            font-weight:600;
                            color: #222;
                            text-align: center;
                            font-size: 14px;
                            margin-bottom: 10px;
                        }}
                    </style>
                </head>
                <body> {content_group}
                </body>
                </html>
                """

                if not os.path.exists(f"{self.images_path}/measure"):   #Valida directorio existe
                    os.makedirs(f"{self.images_path}/measure")

                pdf_path = f"{self.images_path}/measure/output.pdf"
                pdfkit.from_string(html_structure, pdf_path, configuration = config, options = options) #Genera PDF
               
                images = convert_from_path(pdf_path)  # Convertir PDF a imágenes
                output_image_path = None
                name_ext = "_size.png"
                for i, image in enumerate(images):
                    output_image_path = f"{self.images_path}/{sku}/{sku}{name_ext}"
                    image.save(output_image_path, "PNG")
             
            result["output_path"] = f"{self.domain_path}{sku}/{sku}{name_ext}"
            result["temp_output"] = f"{pdf_path}"
            result["success"] = True

            return result 

        except Exception as e:
            print("Error en html Estructura",str(e))
            traceback.print_exc()  # Imprime el seguimiento completo de la excepción
            log_list = self.logger.bug_logs_data(e)
            resp = self.shn_proc.bug_register_proc(log_list)
            return result
        


    def bug_logs_data(self, e, severity="ERROR"):
        try:
            # Intentamos convertir el código de error, si está disponible
            error_code = int(e.args[0]) if e.args and str(e.args[0]).isdigit() else 0
        except (IndexError, ValueError) as error:
            # Si no podemos acceder a e.args[0] o convertirlo a entero, asignamos 0
            error_code = 0

        log_row = {
            "event_type": e.__class__.__name__,
            "log_description": str(e),
            "ip_address": self.get_client_ip(),
            "severity": severity,
            "module": f"{e.__traceback__.tb_frame.f_code.co_filename} {e.__traceback__.tb_lineno}",
            "request_url": self.get_request_url(),
            "http_method": self.get_http_method(),
            "user_agent": self.get_user_agent(),
            "error_code": error_code,
            "stack_trace": ''.join(traceback.format_exception(type(e), e, e.__traceback__)),
            "session_id": None
        }

        log_list = [log_row]

        return json.dumps(log_list)


    def logout_data(self):
        self.driver.get(self.url_base_usa+"user/auth/logout")
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="multi-account__main"]'))
            )
            
            click_return_login=WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,'//div[@class="multi-account__main"]//div[@class="multi-account__login"]'))
            )
            click_return_login.click()
            
            return self.login_data(refresh=False,change_email=True)

        except Exception as e:
            print(e)
            return False


    def extract_variantes(self,index:int):
        
        self.driver.implicitly_wait(5)
        data=self.sku_data[index]
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: "captcha" not in d.current_url
            )
            print("Acceso al producto exitoso:", self.driver.current_url)
        except:
            print("Captcha no resuelto automáticamente, por favor resuélvelo manualmente.")
        #     self.driver.get("https://us.shein.com/login")

        # # Si se logra salir del CAPTCHA, continuar con el scraping

        # self.driver.get(self.url_base+f"product-p-{data['product_id']}.html?languaje=es") 

        print(self.driver.current_url)   
        if "captcha" not in self.driver.current_url:
            print("Página del producto lista para el scraping.")  
        else:
            response_logout=self.logout_data()
            if response_logout:
                print("Logout exitoso")
            else:
                print("Error al hacer logout")
                self.product_data_not_found_api_ctrl(index)

                return
            
        try:
            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            response_json=self.extract_data_soup()
            if response_json:
                print("Información extraída con éxito")
                self.extract_variant(index,response_json)
            else:
                print("Error al extraer la información en extract_variantes")
                self.product_data_not_found_api_ctrl(index)
            self.soup=None
        except Exception as e:
            print(e)
            print("Error al cargar la página")
            self.product_data_not_found_api_ctrl(index)


    def extract_variant(self,index:int,data_sku_soup):

        data=self.sku_data[index]
        # response_data={"is_found":False}
        # last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        parent={}
        
        try:
            current_product_id=data_sku_soup["currentGoodsId"]
            current_product_sku=data_sku_soup["currentGoodsSn"]
            current_product_color=data_sku_soup["productIntroData"]["detail"]["mainSaleAttribute"][0]["attr_value"]
            current_time=self.current_time()
            price_src=data_sku_soup.get("productIntroData",{}).get('getPrice',{}).get('salePrice',{}).get('amount') or data_sku_soup.get('getPrice',{}).get('salePrice',{}).get('usdAmount')

            price=price_src if price_src else None

            sku_list=data_sku_soup.get("productIntroData",{}).get("attrSizeList",{}).get("sale_attr_list").get(data["product_id"],{}).get("sku_list",[])
            
            

            for key,value in enumerate(data['child']):
                compare_sku=value["sku"].strip()
                if(compare_sku==current_product_sku) or (compare_sku==current_product_id):

                    try:
                        quantity = data_sku_soup.get('productIntroData', {}).get('detail', {}).get('stock')
                        if quantity is not None and str(quantity).isdigit():
                            quantity = int(quantity)
                        else:
                            quantity = None
                        in_stock = 1 if quantity and quantity > 0 else 0
                    except Exception as e:
                        print(f"Error en price y  quantity: {e}")
                        quantity = None
                        in_stock = 0

                    data["child"][key]["original_price"] = price
                    data["child"][key]["get_variation"] = 0
                    data["child"][key]["stock"] = in_stock
                    data["child"][key]["quantity"] = quantity

                    if not bool(int(value.get("product_name_saved",0))):
                        product_name_src = data_sku_soup.get("productIntroData", {}).get("detail", {}).get("goods_name", None)
                        if product_name_src is not None:
                            product_name=product_name_src.title()
                            data["child"][key]["product_name"] = product_name

                    if not bool(int(value.get("description_saved", 0))) and bool(int(value.get("verify_description", 0))):
                        list_atributes=data_sku_soup.get("productIntroData", {}).get("detail", {}).get("productDetails",None)
                        description_val = self.set_product_description_ctrl(list_atributes)
                        data["child"][key]["product_description"] = description_val


                    if not bool(int(value.get("color_saved", 0))) and bool(int(value.get("verify_color", 0))):

                        data["child"][key]["color"] = current_product_color   


                    data["child"][key]["last_updated"] = current_time
                    data["child"][key]["searched_times"] = int(value["searched_times"]) + 1

                    if price is not None:
                        data["child"][key]["is_capture"] = 1
                    else:

                        data["child"][key]["searched_fail"] = int(data["child"][key]["searched_fail"]) + 1
                        data["child"][key]["is_capture"] = 0

                        if int(data["child"][key]["searched_fail"]) >= 2:
                            data["child"][key]["stock"] = 0

                    parent=data["child"][key]
                    break
            
            if not parent:
                self.validate_data(index)

            child_size_list=[]
            child_size={}

            for sku in sku_list:
                data_size=sku["sku_sale_attr"][0]
                if data_size:
                    if sku["sku_code"]:

                        child_size["size"]=data_size.get("attr_value_name_en",None)
                        child_size["size_saved"]=(1 
                            if data_size.get("attr_value_name_en", "")
                            else 0
                        )
                        child_size["verify_size"] = (
                            0 
                            if data_size.get("attr_value_name_en", "")
                            else 1
                        )
                        child_size["original_price"] = price if price else None                      
                        child_size["product_description"] =  parent["product_description"]
                        child_size["description_saved"] = 1 if parent["product_description"] else 0
                        if current_product_sku and data_size.get("attr_value_name_en"):
                            child_size["sku"]=current_product_sku+data_size.get("attr_value_name_en")
                        else:
                            child_size["sku"]=None
                        
                        child_size["verify_description"] = 0 if parent["product_description"] else 1   
                        child_size["sku_code"] = sku["sku_code"]
                        child_size["variant_id"] = parent["variant_id"]
                        child_size["category"] = parent["category"]
                        child_size["subcategory"] = parent["subcategory"]
                        child_size["product_type"] = parent["product_type"]
                        child_size["product_name"] = parent["product_name"].strip() if parent["product_name"] else None 
                        child_size["product_name_saved"] = 1 if parent["product_name"] else 0
                        child_size["verify_name"] = 0 if parent["product_name"] else 1
                        child_size["platform"] = parent["platform"]
                        child_size["product_id"] = parent["product_id"]
                        child_size["short_desc_cf"] = parent["short_desc_cf"]
                        child_size["category_cf"] = parent["category_cf"]
                        child_size["category_label"] = parent["category_label"]
                        child_size["brand"] =  parent["brand"].strip().upper() if parent["brand"] else None
                        child_size["brand_saved"] = 1 if parent["brand"] else 0
                        child_size["verify_brand"] = 0 if parent["brand"] else 1
                        child_size["is_parent"] = 0
                        child_size["is_child"] = 1
                        child_size["is_active"] = 0
                        qty = int(sku["stock"]) if "stock" in sku and str(sku["stock"]) else 0
                        child_size["stock"] = 1 if qty >= int(parent["min_quantity"]) else 0     
                        child_size["quantity"] = qty
                        child_size["last_updated"] = current_time
                        child_size["color"] =  parent["color"]
                        child_size["color_saved"] =  1 if parent["color"] else None
                        child_size["verify_color"] =  0 if parent["color"] else 1
                        child_size["use_product_url"] = 0
                        child_size["product_url"] = None
                        child_size["is_capture"] = 1
                        child_size["searched_times"] =  1
                        child_size["searched_fail"] =  0
                        child_size["fail_times"] =  0
                        child_size["parent_sku"] =  parent["parent_sku"]
                        child_size["get_variation"] =  0
                        child_size["height"] =  None
                        child_size["width"] =  None
                        child_size["length"] =  None
                        child_size["dimension_saved"] =  0
                        child_size["verify_dimension"] =  0
                        child_size["weight_in_kg"] =  None
                        child_size["weight_saved"] =  0
                        child_size["verify_weight"] =  0
                        child_size["extraction"] =  0
                        child_size["processing"] =  0
                        child_size["process_app"] = None
                        child_size["from_app"] = None                        
                        child_size = self.create_images_prop(child_prop = child_size)
                        #section  ignore

                        child_size["is_exist_file"] = self.is_valid_images(child_size)
                        child_size["verify_images"] = 0 if bool(int(child_size["is_exist_file"])) else 1
                        child_size_list.append(child_size)
                        if child_size_list:
                            self.shn_proc.update_product_list(
                            data_list = child_size_list
                            ,from_dev = f"Device:{self.on_device_process} | IP: {self.logger.get_public_ip()}" 
                            )
                        child_size_list = []
            
            #variantes color 
            if bool(int(parent["is_parent"])) and not bool(int(parent["is_child"])):

                variantes_color=data_sku_soup.get("productIntroData",{}).get("relation_color",[])
                child_color_list=[]
                child_color={}

                if variantes_color and len(variantes_color)>0:
                    for color in variantes_color:
                        child_color = {
                            "sku" : (color.get("goods_sn", None) or "").strip() or None,
                            "sku_code" :  None,
                            "variant_id" : (color.get("goods_sn", None) or "").strip() or None,
                            "category" : parent["category"],
                            "subcategory" : parent["subcategory"],
                            "product_type" : parent["product_type"],
                            "product_name" : None,
                            "product_name_saved":0,
                            "verify_name":1,
                            "product_description":None,
                            "description_saved":0,
                            "verify_description":1,
                            "platform" : parent["platform"],
                            "product_id" :  color["goods_id"],
                            "short_desc_cf" : parent["short_desc_cf"],
                            "category_cf" : parent["category_cf"],
                            "category_label" : parent["category_label"],
                            "brand" : parent["brand"],
                            "brand_saved": 1 if parent["brand"] else 0,
                            "verify_brand":1,
                            "is_parent" : 1,
                            "is_child" : 1,
                            "is_active" : 1,
                            "extraction":1,
                            "stock" : 0,
                            "quantity" : None,
                            "original_price" : parent["original_price"],
                            "last_updated" : current_time,
                            "color" :  color["mainSaleAttribte"][0]["attr_value"],
                            "color_saved":1 if color["mainSaleAttribte"][0]["attr_value"] else 0,
                            "verify_color":1,
                            "use_product_url" : 0,
                            "product_url" : None,
                            "is_capture" : 1,
                            "searched_times" : 1,
                            "searched_fail" : 0,
                            "fail_times" : 0,
                            "height": None,
                            "width":None,
                            "length": None,
                            "dimension_saved":0,
                            "verify_dimension":1,
                            "weight_in_kg" : None,
                            "weight_saved":0,
                            "verify_weight":1,
                            "is_exist_file":0,
                            "verify_images":1,
                            "size":None,
                            "size_saved":0,
                            "verify_size":1,
                            "own_image":1,
                            "processing":0,
                            "process_app":None,
                            "from_app":None,
                            "get_variation":1,
                            "parent_sku": parent["parent_sku"]
                        }
                        child_color=self.create_images_prop(child_color)
                        child_color_list.append(child_color)
                    if child_color_list:
                        self.shn_proc.update_product_list(
                        data_list = child_color_list
                        ,from_dev = f"Device:{self.on_device_process} | IP: {self.logger.get_public_ip()}" 
                        )
            self.validate_data(index)       
        except Exception as e:
            print(f"Error al estructurar los datos: {str(e)}")
            logs_list=self.logger.bug_logs_data(e)
            self.shn_proc.bug_register_proc(logs_list)
            traceback.print_exc()
            





    def create_images_prop(self,child_prop :dict):
        images_prper_list = self.initial_detail_images_list()

        for ind, img_prop in enumerate(images_prper_list):
            child_prop[img_prop] = None
        
        return child_prop





    def set_product_detail(self,index,key,data):
        try:
            #data_db=self.sku_data[index]
            data_db=data
            #self.sku_data[index]=data_db
            res=self.shn_proc.update_data_for_variantes_proc(data_db)
            return res
        except Exception as e:
            print(f"Error al estructurar los datos: {str(e)}")
            traceback.print_exc()
            return None