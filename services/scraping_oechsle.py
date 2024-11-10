from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException,WebDriverException
import re
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from fuzzywuzzy import fuzz
from shared.driver_bots import WebDriverManager


class OechsleManager(WebDriverManager):
    def __init__(self, language='en_US', proxy=None):
        super().__init__(language, proxy)
        self.driver = self.iniciar_webdriver()


    def normalizar_precio_texto(self,precio):
        # Eliminamos el símbolo de moneda si está presente
        precio = precio.strip().replace('S/', '').replace('$', '').replace(' ', '')

        # Usamos expresiones regulares para normalizar el precio
        # Convertimos cualquier formato con comas y puntos a un formato numérico estándar
        if re.search(r'^\d{1,3}(?:\.\d{3})*(?:,\d{2})?$', precio):  # Formato como 4.500,00
            # Reemplazamos la última coma por un punto (decimal) y eliminamos los puntos
            precio = precio.replace('.', '').replace(',', '.')
        elif re.search(r'^\d{1,3}(?:,\d{3})*(?:\.\d{2})?$', precio):  # Formato como 4,500.00
            # Reemplazamos las comas por un punto y eliminamos el punto como separador de miles
            precio = precio.replace(',', '').replace('.', '.')

        # Retornamos el precio normalizado como texto sin espacios ni símbolos
        return precio


    def obtener_precios(self):
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
            precio_lista_texto = self.driver.find_element(By.CSS_SELECTOR, 'span.text-del.ListPrice').text
            precio_lista = extraer_numero(precio_lista_texto)
        except Exception:
            #print(f"Error al obtener precio lista: {e}")
            precio_lista = None

        try:
            precio_oferta_texto = self.driver.find_element(By.CSS_SELECTOR, 'span.fw-bold.BestPrice').text
            precio_oferta = extraer_numero(precio_oferta_texto)
        except Exception as e:
            #print(f"Error al obtener precio oferta: {e}")
            precio_oferta = None

        try:
            precio_tarjeta_oh_texto = self.driver.find_element(By.CSS_SELECTOR, 'span.fw-bold.tOhPrice').text
            precio_tarjeta_oh = extraer_numero(precio_tarjeta_oh_texto)
        except Exception as e:
            #print(f"Error al obtener precio tarjeta: {e}")
            precio_tarjeta_oh = None

        # Diccionario con resultados
        return {
            "Precio_lista": precio_lista,
            "Precio_oferta": precio_oferta,
            "Precio_tarjeta": precio_tarjeta_oh
        }



    def extract_info_oechsle(self,search_text,product_name,price):
        url="https://www.oechsle.pe/"
        resultado = {
            "success": None,
            "message": "",
        }
        try:
            self.driver.get(url)
            time.sleep(2)
        except (WebDriverException,Exception) as e:
            print(f"Error al abrir la página: {e}")
            resultado["success"] = False
            resultado["message"] = "Error al cargar la página"
            return resultado



        try:

            WebDriverWait(self.driver,10).until(
                EC.presence_of_element_located((By.CLASS_NAME,"biggy-search"))
            )

            search_container= self.driver.find_element(By.CLASS_NAME,"biggy-autocomplete")
            search_bar = search_container.find_element(By.CLASS_NAME,"biggy-autocomplete__input")
            search_bar.send_keys(search_text)
            search_bar.send_keys(Keys.RETURN)
            time.sleep(1)
        except Exception:
            resultado["success"] = False
            resultado["message"] = "Error al buscar el producto"
            return resultado
        
        total_contenedores=0
        pagina_actual=1


        while True:

            try:
                WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located((By.CLASS_NAME,"biggy-search__products"))
                )
            except (TimeoutException,NoSuchElementException):
                resultado["success"] = False
                resultado["message"] = "No se encontraron resultados"
                return resultado
            
            try:
                WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located((By.CLASS_NAME,"biggy-search__products__list"))
                )
            except (TimeoutException,NoSuchElementException):
                resultado["success"] = False
                resultado["message"] = "No se encontraron resultados"
                return resultado

            catalog_container=self.driver.find_element(By.CLASS_NAME,'biggy-search__products__list')    
            contenedores = catalog_container.find_elements(By.XPATH,'//li[@class="biggy-search-analytics-product done"]')

            total_contenedores+=len(contenedores)

            for index,contenedor in enumerate(contenedores):
                try:
                    name_element=contenedor.find_element(By.XPATH,".//span[@class='text fz-15 fz-lg-17 prod-name']")
                    nombre_producto=name_element.text.lower().strip()
                    sku=contenedor.get_attribute("data-product")
                    print("Nombre Producto",nombre_producto)
                    print("SKU",sku)
                except Exception:
                    continue


                result_precios=self.obtener_precios()
                precio_lista=result_precios["Precio_lista"]
                precio_normal=result_precios["Precio_oferta"]
                precio_oferta=result_precios["Precio_tarjeta"]

                #print("")
                if precio_lista==None and precio_normal==None and precio_oferta==None:
                    resultado["success"] = False
                    resultado["message"] = "No se encontraron precios"
                    return resultado

                ratio_similitud=fuzz.token_sort_ratio(product_name.lower(),nombre_producto)

                if ratio_similitud > 80:
                    precios = {
                        "precio_lista": precio_lista,
                        "precio_normal": precio_normal,
                        "precio_oferta": precio_oferta
                    }
                    price_sanitizado=self.normalizar_precio_texto(price)
                    for key, value in precios.items():
                        if value == price_sanitizado:
                            resultado = {
                                "success": True,
                                "message": "Producto encontrado",
                                "contenedor": index + 1,
                                "pagina": pagina_actual,
                                "nombre_producto": nombre_producto,
                                key: value,
                                "sku": sku
                            }
                            return resultado
            try:

                if contenedores:
                    ultimo_contenedor = contenedores[-1]
                    self.driver.execute_script("arguments[0].scrollIntoView();",ultimo_contenedor)
                    print(f"Scroll hasta el contenedor {total_contenedores}")


                WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located((By.CLASS_NAME,"biggy-pagination"))
                )

                paginacion=self.driver.find_element(By.CLASS_NAME,"biggy-pagination")
                siguiente_btn =paginacion.find_element(By.CSS_SELECTOR, '.biggy-pagination__item.biggy-pagination__item--next')
                # Comprueba si el siguiente botón es un <span> (deshabilitado) o un <a> (habilitado)
                if 'biggy-pagination__item--disabled' in siguiente_btn.get_attribute('class'):
                    print("No hay más páginas para navegar.")
                    resultado["success"] = False
                    resultado["message"] = "No hay más páginas para navegar."
                    resultado["pagina"] = pagina_actual
                    return resultado

                # Haz clic en el botón "Siguiente"
                siguiente_btn.click()
                time.sleep(2)

                pagina_actual += 1
            except (NoSuchElementException,TimeoutException):
                resultado["success"] = False
                resultado["message"] = "No se encontraron coincidencias"
                resultado["pagina"] = f"paginas visitadas {pagina_actual}"
                return resultado













    def extract_info_by_sku(self,search_text,sku):
        url="https://www.oechsle.pe/"
        resultado = {
            "success": None,
            "message": "",
        }
        try:
            self.driver.get(url)
            time.sleep(2)
        except (WebDriverException,Exception) as e:
            print(f"Error al abrir la página: {e}")
            resultado["success"] = False
            resultado["message"] = "Error al cargar la página"
            return resultado
        try:

            WebDriverWait(self.driver,10).until(
                EC.presence_of_element_located((By.CLASS_NAME,"biggy-search"))
            )

            search_container= self.driver.find_element(By.CLASS_NAME,"biggy-autocomplete")
            search_bar = search_container.find_element(By.CLASS_NAME,"biggy-autocomplete__input")
            search_bar.send_keys(search_text)
            search_bar.send_keys(Keys.RETURN)
            time.sleep(1)
        except Exception:
            resultado["success"] = False
            resultado["message"] = "Error al buscar el producto"
            return resultado
        
        total_contenedores=0
        pagina_actual=1


        while True:

            try:
                WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located((By.CLASS_NAME,"biggy-search__products"))
                )
            except (TimeoutException,NoSuchElementException):
                resultado["success"] = False
                resultado["message"] = "No se encontraron resultados"
                return resultado
            
            try:
                WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located((By.CLASS_NAME,"biggy-search__products__list"))
                )
            except (TimeoutException,NoSuchElementException):
                resultado["success"] = False
                resultado["message"] = "No se encontraron resultados"
                return resultado

            catalog_container=self.driver.find_element(By.CLASS_NAME,'biggy-search__products__list')    
            contenedores = catalog_container.find_elements(By.XPATH,'//li[@class="biggy-search-analytics-product done"]')

            total_contenedores+=len(contenedores)

            for index,contenedor in enumerate(contenedores):
                try:
                    name_element=contenedor.find_element(By.XPATH,".//span[@class='text fz-15 fz-lg-17 prod-name']")
                    nombre_producto=name_element.text.lower().strip()
                    sku_text=contenedor.get_attribute("data-product")
                    print("Nombre Producto",nombre_producto)
                    print("SKU",sku)
                except Exception:
                    continue

                result_precios=self.obtener_precios()
                precio_lista=result_precios["Precio_lista"]
                precio_normal=result_precios["Precio_oferta"]
                precio_oferta=result_precios["Precio_tarjeta"]

                if sku==sku_text:
                    precios = {"precio_lista": precio_lista,"precio_normal": precio_normal,"precio_oferta": precio_oferta}
                    resultado = {
                        "success": True,
                        "message": "Producto encontrado",
                        "contenedor": index + 1,
                        "pagina": pagina_actual,
                        "nombre_producto": nombre_producto,
                        "sku": sku
                    }
                    for key, value in precios.items():
                        if value is not None:
                            resultado[key] = value
                            break
                    return resultado
            try:

                if contenedores:
                    ultimo_contenedor = contenedores[-1]
                    self.driver.execute_script("arguments[0].scrollIntoView();",ultimo_contenedor)
                    print(f"Scroll hasta el contenedor {total_contenedores}")


                WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located((By.CLASS_NAME,"biggy-pagination"))
                )

                paginacion=self.driver.find_element(By.CLASS_NAME,"biggy-pagination")
                siguiente_btn =paginacion.find_element(By.CSS_SELECTOR, '.biggy-pagination__item.biggy-pagination__item--next')
                # Comprueba si el siguiente botón es un <span> (deshabilitado) o un <a> (habilitado)
                if 'biggy-pagination__item--disabled' in siguiente_btn.get_attribute('class'):
                    print("No hay más páginas para navegar.")
                    resultado["success"] = False
                    resultado["message"] = "No hay más páginas para navegar."
                    resultado["pagina"] = pagina_actual
                    return resultado

                # Haz clic en el botón "Siguiente"
                siguiente_btn.click()
                time.sleep(2)

                pagina_actual += 1
            except (NoSuchElementException,TimeoutException):
                resultado["success"] = False
                resultado["message"] = "No se encontraron coincidencias"
                resultado["pagina"] = f"paginas visitadas {pagina_actual}"
                return resultado













