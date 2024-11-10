from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException,WebDriverException, NoSuchElementException, ElementClickInterceptedException
import re
import time
from shared.driver_bots import WebDriverManager
#from models.database_bots import RankingProduct
from selenium.webdriver.common.keys import Keys
from fuzzywuzzy import fuzz


class PromartManager(WebDriverManager):
    def __init__(self, language='en_US', proxy=None):
        super().__init__(language, proxy)
        self.driver=self.iniciar_webdriver()




    def extract_info_promart(self,search_text,product_name,price):
        url="https://www.promart.pe/"
        resultado={
            "success":False,
            "message":"No se encontraron coincidencias"
        }
        try:
            self.driver.get(url)
            time.sleep(2)
        except WebDriverException as e:
            print(f"Error al abrir la página: {e}")
            resultado["message"]=f"Error al abrir la página"
            resultado["success"]=False
            return resultado


        try:
            search_container=self.driver.find_element(By.CLASS_NAME,"wp-inp")
            search_input=search_container.find_element(By.TAG_NAME,"input")
            search_input.send_keys(search_text)
            search_input.send_keys(Keys.RETURN)
            time.sleep(1)
        except Exception:
            resultado["success"]=False
            resultado["message"]="Error al buscar el producto en la barra de búsqueda"
            return resultado
        

        total_contenedores = 0
        pagina_actual = 1
        try:

            while True:


                
                try:
                    WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "content-main")))

                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH,'//div[contains(@class,"productos js-productos slider-products-home gh-products-listado")]'))
                    )
                except (TimeoutException,NoSuchElementException):
                    resultado["success"]=False
                    resultado["message"]="Error al cargar la página (categoría-contendor)"
                    return resultado
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH,'//div[contains(@class,"productos js-productos slider-products-home gh-products-listado active")]'))
                    )
                except TimeoutException:
                    print(f"Error al buscar los contenedores: {e}")
                    resultado["success"]=False
                    resultado["message"]="Error al buscar los contenedores"
                    return resultado
                list_container=self.driver.find_element(By.XPATH,'//div[@class="content-main"]//div[@class="js-prod"]')
                containers=list_container.find_elements(By.XPATH,"./ul/li")
                print(f'Contenedores en esta página: {len(containers)}')
                for index,container in enumerate(containers):
                    try:
                        name_element=container.find_element(By.CLASS_NAME,"productName")
                        name_product=name_element.text.lower().strip()
                    
                    except Exception:
                        continue

                    result_precios=self.obtener_precios(container)
                    precio_lista=result_precios["Precio_lista"]
                    precio_normal=result_precios["Precio_oferta"]
                    precio_oferta=result_precios["Precio_tarjeta"]
                    ratio_similitud=fuzz.token_sort_ratio(product_name.lower(),name_product)
                    
                    if ratio_similitud>70:
                        

                        price_sanitizado=self.normalizar_precio_texto(price)
                        precios = {
                            "precio_lista": precio_lista,
                            "precio_normal": precio_normal,
                            "precio_oferta": precio_oferta
                        }
                        sku=self.extract_sku_product(container)
                        for key, value in precios.items():
                            if value == price_sanitizado:
                                resultado = {
                                    "success": True,
                                    "message": "Producto encontrado",
                                    "contenedor": index + 1,
                                    "pagina": pagina_actual,
                                    "nombre_producto": name_product,
                                    "sku":sku,
                                    key: value,
                                }
                                return resultado
                try:

                    if containers:
                        ultimo_contenedor = containers[-1]
                        self.driver.execute_script("arguments[0].scrollIntoView();", ultimo_contenedor)
                        print(f"Desplazando a contenedor {total_contenedores + len(containers)}")

                    
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "row-pagination"))
                    )

                    paginacion = self.driver.find_element(By.CLASS_NAME, "row-pagination")
                    siguiente_btn=paginacion.find_element(By.XPATH,"//div[@class='row-pagination']//div[@class='btn-arrow']/a[@id='next_link']")


                    if 'link disabled' in siguiente_btn.get_attribute("class"):
                        print("No hay más páginas")
                        resultado["success"] = False
                        resultado["message"] = "No se encontraron coincidencias"
                        return resultado
                    
                    siguiente_btn.click()
                    time.sleep(2)
                    pagina_actual += 1

                except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
                    print(f"Error al cambiar de página: {e}")
                    resultado["success"] = False
                    resultado["message"] = "Error al cambiar de página"
                    return resultado

        except Exception as e:
            print(f"Error al buscar los contenedores: {e}")
            resultado["success"]=False
            resultado["message"]="Error al buscar los contenedores"
            return resultado
        


    
    def obtener_precios(self,container):
        # Función para extraer solo el número decimal y normalizarlo
        def extraer_numero(texto):
            if texto:
                # Eliminamos el símbolo de moneda y los espacios
                texto = texto.replace('S/', '').replace(' ', '')
                # Buscamos un número con formato válido
                match = re.search(r'(\d+[\.,]?\d*(?:,\d{2})?)', texto)
                if match:
                    # Reemplazamos la coma por un punto para mantener un formato decimal adecuado
                    precio_normalizado = match.group(0).replace(',', '')
                    return normalizar_precio(precio_normalizado)
            return None

        # Función para normalizar el precio a float con dos decimales
        def normalizar_precio(precio):
            # Reemplazamos la última coma por un punto y eliminamos los puntos
            if ',' in precio and '.' in precio:
                precio = precio.replace('.', '').replace(',', '.')
            elif '.' in precio:
                precio = precio.replace(',', '').replace('.', '.')
            elif ',' in precio:
                precio = precio.replace(',', '')
            
            # Convertimos a float y formateamos a dos decimales
            return f"{float(precio):.2f}"

        # Intentamos encontrar cada precio con selectores específicos
        try:
            precio_lista_texto = container.find_element(By.XPATH,".//div[@class='bestPrice']/div[@class='vcenter listPrice js-listPrice']").text
            precio_lista = extraer_numero(precio_lista_texto)
            print(precio_lista)
        except Exception:
            #print(f"Error al obtener precio lista: {e}")
            precio_lista = None

        try:
            precio_oferta_texto = container.find_element(By.XPATH,".//div[@class='bestPrice']//div[@class='vcenter bestPrice js-bestPrice second-price']").text
            precio_oferta = extraer_numero(precio_oferta_texto)
            print(precio_oferta)
        except Exception as e:
            #print(f"Error al obtener precio oferta: {e}")
            precio_oferta = None

        try:
            precio_tarjeta_oh_texto = container.find_element(By.XPATH,".//div[@class='price-tarjetaOh js-tarjetaOH active']//span[@class='price price-toh js-pp']").text
            precio_tarjeta_oh = extraer_numero(precio_tarjeta_oh_texto)
            print(precio_tarjeta_oh)
        except Exception as e:
            #print(f"Error al obtener precio tarjeta: {e}")
            precio_tarjeta_oh = None

        # Diccionario con resultados
        return {
            "Precio_lista": precio_lista,
            "Precio_oferta": precio_oferta,
            "Precio_tarjeta": precio_tarjeta_oh
        }
    



    def normalizar_precio_texto(self, precio):
        precio = precio.strip().replace('S/', '').replace('$', '').replace(' ', '')

        if re.search(r'^\d{1,3}(?:\.\d{3})*(?:,\d{2})?$', precio):
            precio = precio.replace('.', '').replace(',', '.')
        elif re.search(r'^\d{1,3}(?:,\d{3})*(?:\.\d{2})?$', precio):  # 
            precio = precio.replace(',', '').replace('.', '.')

        if '.' not in precio:
            precio = f"{float(precio):.2f}"

        return precio
    



    def extract_sku_product(self,container):

        try:
            sku_element=container.find_element(By.XPATH,".//div[@class='item-product product-listado']/div")

            sku=sku_element.get_attribute("data-sku")
            return sku
        except Exception as e:
            return None
        





    def extract_info_by_sku(self,sku,search_text):
        url="https://www.promart.pe/"
        resultado={
            "success":False,
            "message":"No se encontraron coincidencias"
        }
        try:
            self.driver.get(url)
            time.sleep(2)
        except WebDriverException as e:
            print(f"Error al abrir la página: {e}")
            resultado["message"]=f"Error al abrir la página"
            resultado["success"]=False
            return resultado


        try:
            search_container=self.driver.find_element(By.CLASS_NAME,"wp-inp")
            search_input=search_container.find_element(By.TAG_NAME,"input")
            search_input.send_keys(search_text)
            search_input.send_keys(Keys.RETURN)
            time.sleep(1)
        except Exception:
            resultado["success"]=False
            resultado["message"]="Error al buscar el producto en la barra de búsqueda"
            return resultado
        total_contenedores = 0
        pagina_actual = 1
        try:
            while True:

                try:
                    WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "content-main")))

                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH,'//div[contains(@class,"productos js-productos slider-products-home gh-products-listado")]'))
                    )
                except (TimeoutException,NoSuchElementException):
                    resultado["success"]=False
                    resultado["message"]="Error al cargar la página (categoría-contendor)"
                    return resultado
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH,'//div[contains(@class,"productos js-productos slider-products-home gh-products-listado active")]'))
                    )
                except TimeoutException:
                    print(f"Error al buscar los contenedores: {e}")
                    resultado["success"]=False
                    resultado["message"]="Error al buscar los contenedores"
                    return resultado
                list_container=self.driver.find_element(By.XPATH,'//div[@class="content-main"]//div[@class="js-prod"]')
                containers=list_container.find_elements(By.XPATH,"./ul/li")
                print(f'Contenedores en esta página: {len(containers)}')
                for index,container in enumerate(containers):
                    try:
                        name_element=container.find_element(By.CLASS_NAME,"productName")
                        name_product=name_element.text.lower().strip()
                    
                    except Exception:
                        continue
                        
                    sku_text=self.extract_sku_product(container)
                    result_precios=self.obtener_precios(container)
                    precio_lista=result_precios["Precio_lista"]
                    precio_normal=result_precios["Precio_oferta"]
                    precio_oferta=result_precios["Precio_tarjeta"]
                    
                    precios = {
                        "precio_lista": precio_lista,
                        "precio_normal": precio_normal,
                        "precio_oferta": precio_oferta
                    }
                    if sku_text==sku:
                        resultado = {
                            "success": True,
                            "message": "Producto encontrado",
                            "contenedor": index + 1,
                            "pagina": pagina_actual,
                            "nombre_producto": name_product,
                            "sku":sku
                        }

                        # Solo agrega el primer precio que no sea None
                        for key, value in precios.items():
                            if value is not None:
                                resultado[key] = value
                                break
                        return resultado
                try:

                    if containers:
                        ultimo_contenedor = containers[-1]
                        self.driver.execute_script("arguments[0].scrollIntoView();", ultimo_contenedor)
                        print(f"Desplazando a contenedor {total_contenedores + len(containers)}")

                    
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "row-pagination"))
                    )

                    paginacion = self.driver.find_element(By.CLASS_NAME, "row-pagination")
                    siguiente_btn=paginacion.find_element(By.XPATH,"//div[@class='row-pagination']//div[@class='btn-arrow']/a[@id='next_link']")

                    if 'link disabled' in siguiente_btn.get_attribute("class"):
                        print("No hay más páginas")
                        resultado["success"] = False
                        resultado["message"] = "No se encontraron coincidencias"
                        return resultado
                    
                    siguiente_btn.click()
                    time.sleep(2)
                    pagina_actual += 1

                except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
                    print(f"Error al cambiar de página: {e}")
                    resultado["success"] = False
                    resultado["message"] = "Error al cambiar de página"
                    return resultado

        except Exception as e:
            print(f"Error al buscar los contenedores: {e}")
            resultado["success"]=False
            resultado["message"]="Error al buscar los contenedores"
            return resultado        