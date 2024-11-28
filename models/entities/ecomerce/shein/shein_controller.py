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


class SheinController():
    def __init__(self, language='en_US'):
        self.language = language
        self.driver = self.init_driver()
        self.url_base = "https://www.shein.com/"
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
        self.domain_path = os.getenv('DOMAIN')
        self.url_complete=None
 
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




    def get_product_detail(self,platform : str = 'Shein'):

        # ip = self.get_public_ip()
        # if ip:
        #     self.on_device_process = ip
        
        response =  self.shn_proc.get_product_list_proc(platform,self.on_device_process)
        if response:
            self.set_sku_data_list(response)
        self.update_data_sku_price()


    


    def update_data_sku_price(self):
        sku_list= self.get_sku_data_list()
        if not sku_list:
            return
        self.lenght_sku_list = len(sku_list)
        try:

            for index,data in enumerate(sku_list):

                #if data.get("product_id", None).strip() and bool(int(data.get("is_parent", False))):
                url=self.url_base+f"product-p-{data['product_id']}.html?languaje=es"
                self.url_complete=self.url_base_usa+f"product-p-{data['product_id']}.html"
                self.driver.get(url)
                self.extract_info(index)
                self.url_complete=None
        except Exception as e:
            print(f"Error al actualizar los datos: {str(e)}")
            return None
        


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
    
    def extract_info(self,index:int):    
        self.driver.implicitly_wait(5)
        self.driver.get(self.url_complete) 
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
            #self.driver.get(self.url_base_usa+f"/product-p-{data['product_id']}.html")    
        else:
            print("Permaneciendo en la página del CAPTCHA.")
        try:
            modal_is_closed = self.close_modal()
            if modal_is_closed:
                print("Modal cerrado")
            else:
                print("No se encontró el modal")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID,"goods-detail-v3"))
            )
            banner_is_closed=self.close_banner()
            if banner_is_closed:
                print("Banner cerrado")
            else:
                print("No se encontró el banner")
            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            response_json=self.extract_data_soup()
            if response_json:
                print("Información extraída con éxito")
                self.structure_data(response_json,index)
            else:
                print("Error al extraer la información")
        except Exception as e:
            print(e)
            print("Error al cargar la página")
            self.product_data_not_found_api_ctrl(index)
    def close_modal(self):
        try:
            WebDriverWait(self.driver, 3).until(
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
            print(f"Error al extraer la información del producto")
            return None

    def close_banner(self):
        try:
            close_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH,'//div[@class="quickg-outside"]'))
            )
            close_button.click()
            return True
        except Exception as e:
            print("No se encontró el banner de registro rápido")
            return False


    def current_time(self):
        current_time = datetime.now()
        formatted_current_time = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
        return formatted_current_time    

    def structure_data(self,data:list[dict],index:int):
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

            # try:
            #     variantes_color = (
            #         data.get('productIntroData', {})
            #         .get('relation_color', [])
            #     )
            # except (KeyError, TypeError):
            #     variantes_color = []  # Si hay un error, se asigna una lista vacía

            # Validar la unión de las listas
            #variantes_unidas = (variantes if variantes else []) + (variantes_color if variantes_color else [])

            for key,value in enumerate(db_data["child"]):
                
                compare_sku=value.get("sku").strip().upper()
                
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

                        product_description_src=self.set_product_description_ctrl()
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
                        print("data\n",db_data["child"][key])

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
            if variantes is not None:
                for key,value in enumerate(db_data['child']):
                    for variante in variantes:
                        if value["sku_code"] == variante["sku_code"]:
                            if not bool(int(value["size_saved"])) and bool(int(value["verify_size"])):
                                size_src=variante["sku_sale_attr"][0]["attr_value_name_en"]
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

                                    db_data["child"][key]["main_image_url"] = main_image_url_c

                                    images_child =images_list_ch #[main_image_url_c]

                                    hires_images_c = self.get_product_images_api_ctrl(qty_img_c,images_child)
                                    db_data["child"][key]["hires_images"] = hires_images_c

                                    main_img_url_c = asyncio.run(self.download_image(value["sku"],db_data["child"][key].get('main_image_url'),"main"))                            
                                    db_data["child"][key]["main_image_url"] = main_img_url_c['url']  if main_img_url_c["status"] else None

                                    resp_multi_img_c =  asyncio.run(self.download_multiple_images(value["sku"],db_data["child"][key].get('hires_images')))
                                    
                                    if resp_multi_img_c:
                                        for kyc, url_val_c in enumerate(resp_multi_img_c):
                                                key_value = url_val_c["name"]
                                                if key_value in db_data["child"][key]:#validar el primer key
                                                    db_data["child"][key][key_value] = url_val_c.get("url",None)

                                    if parent and "image_size_link" in parent and parent["image_size_link"]:
                                        name_child = value["sku"].lower().strip()
                                        ext_ch = Path(parent["image_size_link"]).suffix
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
                            db_data["child"][key]["last_updated"] = current_time
                            db_data["child"][key]["searched_times"] = int(value["searched_times"]) + 1

                            if price_child is not None:
                                db_data["child"][key]["is_capture"] = 1
                            else:
                                db_data["child"][key]["searched_fail"] = int(value["searched_fail"]) + 1
                                db_data["child"][key]["is_capture"] = 0
                                db_data["child"][key]["stock"] = 0
            self.validate_data(index)
        except Exception as e:
            print(f"Error al estructurar los datos: {str(e)}")
            return None


    async def copy_file(self,sku:str, new_name : str,old_name :str,extension:str):
        result = {
            "success": False,
            "output_path": None,
            "temp_output": None,
            "error": None
        }
        try:
            src_path = f"{self.images_path}/{sku.lower()}/{old_name}{extension}"
            dest_dir  = f"{self.images_path}/{new_name}"
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            dest_image_path = os.path.join(dest_dir, f"/{new_name}_size{extension}")

            shutil.copy(src_path, dest_image_path)

            output_path = f"{self.domain_path}{new_name}/"
            image_url_domain = urljoin(output_path, f"{new_name}_size{extension}")
            result["success"] = True
            result["output_path"] = image_url_domain

            return result
        
        except Exception as e:
            print(f"Error al copiar el archivo: {str(e)}")
            log_list = self.logger.bug_logs_data(e)
            resp = self.shn_proc.bug_register_proc(log_list)
            return result



    def validate_data(self,index:int):
        data = self.sku_data[index]
        self.lenght_sku_list = len(data["child"])        
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
            self.sku_detail.append(data["child"][indx]) 
            self.updated_rows(1)
            self.batching_data(indx) 



    def is_valid_proper(self,data:dict,prop:str):

        if prop in data:
            return 1 if data.get(prop) is not None else 0
        return 0



    def batching_data(self, index : int):
        if (index + 1) % self.batch_size == 0 or index + 1 == self.lenght_sku_list:
            result = self.shn_proc.update_shein_sku_list_proc(self.sku_detail,self.batch_size)
            self.affected_rows = result
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
            log_list = self.logger.bug_logs_data(e)
            resp = self.shn_proc.bug_register_proc(log_list)
            return {"url": image_url, "status": False, "message": "Timeout al descargar thumbnail"}
        except Exception as e:
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
    

    def set_product_description_ctrl(self):


        # se hace con el html de la pagina 
        try:
            description_table = self.soup.select_one('.product-intro__description-table')
            if description_table:
                ul = '<ul>'
                items = description_table.select('.product-intro__description-table-item')
                for item in items:
                    key = item.select_one('.key').get_text(strip=True)
                    val = item.select_one('.val').get_text(strip=True)
                    ul += f'<li>{key} {val}</li>'
                ul += '</ul>'
            return ul
        except Exception as e:
            print(f"Error al actualizar los datos: {str(e)}")
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
           
            if part.isnumeric() or (part.replace('.', '', 1).isdigit() and part.count('.') < 2):
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
                
            #config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
            config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
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
               
                #images = convert_from_path(pdf_path)  # Convertir PDF a imágenes
                output_image_path = None
                name_ext = "_size.png"
                # for i, image in enumerate(images):
                #     output_image_path = f"{self.images_path}/{sku}/{sku}{name_ext}"
                #     image.save(output_image_path, "PNG")
             
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
        log_row = {
            "event_type": e.__class__.__name__,
            "log_description": str(e),
            "ip_address": self.get_client_ip(),
            "severity": severity,
            "module": f"{e.__traceback__.tb_frame.f_code.co_filename} {e.__traceback__.tb_lineno}",
            "request_url": self.get_request_url(),
            "http_method": self.get_http_method(),
            "user_agent": self.get_user_agent(),
            "error_code": int(e.args[0]) if e.args and e.args[0].isdigit() else 0,
            "stack_trace": ''.join(traceback.format_exception(type(e), e, e.__traceback__)),
            "session_id": None
        }

        log_list = [log_row]

        return json.dumps(log_list)