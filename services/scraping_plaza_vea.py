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



class PlazaVeaManager(WebDriverManager):
    def __init__(self, language='en_US', proxy=None):
        super().__init__(language, proxy)
        self.BRAND = "COMPRAFACIL USA"
        self.driver= self.iniciar_webdriver()

    def extract_info_plaza_vea(self,search_text,product_name):
        url="https://www.plazavea.com.pe/"
        #BRAND= "COMPRAFACIL USA"
        #BRAND_TEST="COVERSSTOREPERU"
        resultado = {
            "success": None,
            "message": "",
        }
        try:
            self.driver.get(url)
            time.sleep(2)
        except (WebDriverException,Exception) as e:
            print(f"Error al abrir la página: {e}")
            resultado["success"]=False
            resultado["message"]="Error al cargar la página principal"
            return resultado

        try:

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "search")))

            search_bar = self.driver.find_element(By.ID,"search_box")
            search_bar.send_keys(search_text)
            search_bar.send_keys(Keys.RETURN)
            time.sleep(1)
            #input("Press Enter to continue...")
        except Exception:
            resultado["success"]=False
            resultado["message"]="Error al buscar el producto en la barra de búsqueda"
            return resultado

        resultado=None
        total_contenedores=0
        pagina_actual=1

        while True:

            try:
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "category-page")))
            except (TimeoutException,NoSuchElementException):
                resultado["success"]=False
                resultado["message"]="Error al cargar la página (categoría-contendor)"
                return resultado
            
            try:
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "showcase-grid")))
            except (TimeoutException,NoSuchElementException):
                resultado["success"]=False
                resultado["message"]="Error al cargar la página (contenedor)"
                return resultado
            
            catalog_container=self.driver.find_elements(By.XPATH,'//div[contains(@class,"Showcase Showcase--non-food ga-product-item")]')

            total_contenedores+=len(catalog_container)

            for index,contenedor in enumerate(catalog_container):
                try:
                    name_element=contenedor.get_attribute('data-ga-name')
                    nombre_producto=name_element.lower().strip()
                    brand_element=contenedor.get_attribute('data-ga-seller')
                    brand_product=brand_element.upper().strip()
                    sku_element=contenedor.get_attribute('data-ga-sku').strip()

                    print("Nombre Producto",nombre_producto)
                    print("Brand Producto",brand_product)

                except Exception:
                    continue

                ratio_similitud=fuzz.token_sort_ratio(product_name.lower(),nombre_producto)
                if ratio_similitud>70 and brand_product==self.BRAND:
                    resultado={
                        "success":True,
                        "message":"Producto encontrado",
                        "contenedor":index+1,
                        "pagina":pagina_actual,
                        "sku":sku_element
                    }
                    return resultado
                
            try:

                if catalog_container:
                    ultimo_contenedor= catalog_container[-1]
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", ultimo_contenedor)
                    time.sleep(2)
                    print(f'Scroll hasta el contenedor {total_contenedores}')
                    self.driver.execute_script("window.scrollBy(0, +80);")

                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "pagination")))

                try:
                    max_page_text = self.driver.find_element(By.XPATH,"//span[contains(@class, 'page-number')][last()]").text
                    next_page_number = pagina_actual + 1
                    next_page_element = self.driver.find_element(By.XPATH, f"//span[contains(@class, 'page-number') and text()='{next_page_number}']")
                    if max_page_text==str(pagina_actual):
                        resultado["success"]=False
                        resultado["message"]="Producto no encontrado"
                        resultado["pagina"]=pagina_actual
                        return resultado
                    
                    current_url_before=self.driver.current_url
                    print("URL BEFORE CLICK",current_url_before)

                    next_page_element.click()

                    loader=self.wait_for_element()
                    if loader==False:
                        resultado["success"]=False
                        resultado["message"]="Error al cargar la página(loader)"
                        resultado["pagina"]=pagina_actual
                        return resultado
                except Exception:
                    resultado["success"]=False
                    resultado["message"]="Error al cargar la página"
                    resultado["pagina"]=pagina_actual
                    return resultado


                pagina_actual+=1
                print("PAGINA ACTUAL",pagina_actual)
            except Exception:
                resultado["success"]=False
                resultado["message"]="Error al cargar la página(paginacion)"
                resultado["pagina"]=pagina_actual

    def wait_for_element(driver):
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "showcase-grid ")))
        except TimeoutException:
            return False
        return True
        




    def extract_info_by_sku(self,search_text,sku):
        url="https://www.plazavea.com.pe/"
        resultado = {
            "success": None,
            "message": "",
        }
        try:
            self.driver.get(url)
            time.sleep(2)
        except (WebDriverException,Exception) as e:
            print(f"Error al abrir la página: {e}")
            resultado["success"]=False
            resultado["message"]="Error al cargar la página principal"
            return resultado

        try:

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "search")))

            search_bar = self.driver.find_element(By.ID,"search_box")
            search_bar.send_keys(search_text)
            search_bar.send_keys(Keys.RETURN)
            time.sleep(1)
            #input("Press Enter to continue...")
        except Exception:
            resultado["success"]=False
            resultado["message"]="Error al buscar el producto en la barra de búsqueda"
            return resultado

        resultado=None
        total_contenedores=0
        pagina_actual=1

        while True:

            try:
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "category-page")))
            except (TimeoutException,NoSuchElementException):
                resultado["success"]=False
                resultado["message"]="Error al cargar la página (categoría-contendor)"
                return resultado
            
            try:
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "showcase-grid")))
            except (TimeoutException,NoSuchElementException):
                resultado["success"]=False
                resultado["message"]="Error al cargar la página (contenedor)"
                return resultado
            
            catalog_container=self.driver.find_elements(By.XPATH,'//div[contains(@class,"Showcase Showcase--non-food ga-product-item")]')

            total_contenedores+=len(catalog_container)

            for index,contenedor in enumerate(catalog_container):
                try:
                    name_element=contenedor.get_attribute('data-ga-name')
                    nombre_producto=name_element.lower().strip()
                    brand_element=contenedor.get_attribute('data-ga-seller')
                    brand_product=brand_element.upper().strip()
                    sku_element=contenedor.get_attribute('data-ga-sku').strip()

                    print("Nombre Producto",nombre_producto)
                    print("Brand Producto",brand_product)

                except Exception:
                    continue

                if sku_element==sku:
                    resultado={
                        "success":True,
                        "message":"Producto encontrado",
                        "contenedor":index+1,
                        "pagina":pagina_actual,
                        "sku":sku_element
                    }
                    return resultado
                
            try:

                if catalog_container:
                    ultimo_contenedor= catalog_container[-1]
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", ultimo_contenedor)
                    time.sleep(2)
                    print(f'Scroll hasta el contenedor {total_contenedores}')
                    self.driver.execute_script("window.scrollBy(0, +80);")

                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "pagination")))

                try:
                    max_page_text = self.driver.find_element(By.XPATH,"//span[contains(@class, 'page-number')][last()]").text
                    next_page_number = pagina_actual + 1
                    next_page_element = self.driver.find_element(By.XPATH, f"//span[contains(@class, 'page-number') and text()='{next_page_number}']")
                    if max_page_text==str(pagina_actual):
                        resultado["success"]=False
                        resultado["message"]="Producto no encontrado"
                        resultado["pagina"]=pagina_actual
                        return resultado
                    
                    current_url_before=self.driver.current_url
                    print("URL BEFORE CLICK",current_url_before)

                    next_page_element.click()

                    loader=self.wait_for_element()
                    if loader==False:
                        resultado["success"]=False
                        resultado["message"]="Error al cargar la página(loader)"
                        resultado["pagina"]=pagina_actual
                        return resultado
                except Exception:
                    resultado["success"]=False
                    resultado["message"]="Error al cargar la página"
                    resultado["pagina"]=pagina_actual
                    return resultado


                pagina_actual+=1
                print("PAGINA ACTUAL",pagina_actual)
            except Exception:
                resultado["success"]=False
                resultado["message"]="Error al cargar la página(paginacion)"
                resultado["pagina"]=pagina_actual