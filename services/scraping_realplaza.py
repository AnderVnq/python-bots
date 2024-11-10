from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import NoSuchElementException,WebDriverException
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from fuzzywuzzy import fuzz
from shared.driver_bots import WebDriverManager




class RealPlazaManager(WebDriverManager): 
    def __init__(self, language='en_US', proxy=None):
        super().__init__(language, proxy)
        self.BRAND="COMPRAFACIL USA"
        self.driver= self.iniciar_webdriver()
        

    def extract_info_realplaza(self,search_text,product_name):
        url="https://www.realplaza.com.pe/"
        #BRAND="COMPRAFACIL USA"
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
                EC.presence_of_element_located((By.CLASS_NAME,"vtex-input-prefix__group flex flex-row items-stretch overflow-hidden br2 bw1 b--solid b--muted-4 hover-b--muted-3 h-large "))
            )
            search_box = self.driver.find_element(By.ID,"downshift-2-input")
            search_box.send_keys(search_text)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)
        except (NoSuchElementException,Exception) as e:
            resultado["success"] = False
            resultado["message"] = "Error al buscar el producto"
            return resultado
        

        total_contenedores = 0
        pagina_actual = 1


        while True:
            try:
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID,"gallery-layout-container")))
            except (TimeoutException,NoSuchElementException):
                resultado["success"] = False
                resultado["message"] = "No se encontraron resultados"
                return resultado
            

            catalog_container=self.driver.find_element(By.ID,"gallery-layout-container")
            contenedores=catalog_container.find_elements(By.XPATH,'//div[@class="vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4 realplaza-components-0-x-switch__layout__grid"]')

            total_contenedores+=len(contenedores)

            for index,contenedor in enumerate(contenedores):

                try:
                    name_element= contenedor.find_element(By.XPATH,'//div[@class="vtex-product-summary-2-x-nameContainer flex items-start justify-center pv6"]//span')
                    nombre_producto = name_element.text.lower().strip()

                    brand_element= contenedor.find_element(By.XPATH,'//div[@class="realplaza-product-custom-0-x-ProductSellerNameComponent"]//p')

                    brand_sanitize= brand_element.text.replace("Por ", "")
                    brand_product = brand_sanitize.upper().strip()
                except Exception:
                    continue

                

                ratio_similitud=fuzz.token_sort_ratio(product_name.lower(),nombre_producto)

                if ratio_similitud>80 and brand_product==self.BRAND:
                    resultado={
                        "success":True,
                        "message":"Producto encontrado",
                        "contenedor":index+1,
                        "pagina":pagina_actual,
                    }
                    return resultado
            try:
                if contenedores:
                    ultimo_contenedor = contenedores[-1]
                    self.driver.execute_script("arguments[0].scrollIntoView();",ultimo_contenedor)
                    print(f"Scroll hasta el contenedor {total_contenedores}")



                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME,"vtex-flex-layout-0-x-flexRow")))

                paginacion = self.driver.find_element(By.CLASS_NAME,"vtex-flex-layout-0-x-flexRow")
                siguiente_btn = paginacion.find_element(By.CLASS_NAME, "realplaza-rpweb-10-x-paginationButton")
            
                # Verificar si el botón tiene la clase "realplaza-rpweb-10-x-enabled"
                if "realplaza-rpweb-10-x-enabled" in siguiente_btn.get_attribute("class"):
                    # Si está habilitado, hacer clic para ir a la siguiente página
                    siguiente_btn.click()
                    pagina_actual+=1
                else:
                    resultado["success"] = False
                    resultado["message"] = "No se encontraron coincidencias"
                    resultado["pagina"] = f"paginas visitadas {pagina_actual}"



            except (NoSuchElementException,TimeoutException):
                resultado["success"] = False
                resultado["message"] = "No se encontraron coincidencias"
                resultado["pagina"] = f"paginas visitadas {pagina_actual}"
                return resultado