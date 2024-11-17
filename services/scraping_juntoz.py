from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException,WebDriverException, NoSuchElementException, ElementClickInterceptedException
import re
import time
from shared.driver_bots import WebDriverManager
from models.database_bots import RankingProduct


class JuntozManager(WebDriverManager):

    def __init__(self, language='en_US', proxy=None):
        super().__init__(language, proxy)
        self.driver = self.iniciar_webdriver()
    def close_modal(self):
        try:
            modal = self.driver.find_element(By.XPATH, '//w-div[@role="dialog"]')
            
            try:
                close_button = modal.find_element(By.XPATH, './/span[contains(@class, "w")]')
                close_button.click() 
                return True  
            
            except (NoSuchElementException, ElementClickInterceptedException):
                return False
        except Exception:
            return True

    def wait_for_loader_to_disappear(self, timeout=20):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "panel-loader"))
            )
            return True
        except TimeoutException:
            print("Error: El loader no desapareció a tiempo.")
            return False

    def obtener_numero_productos(self):
        # Encuentra el elemento que contiene el texto
        element = self.driver.find_element(By.CSS_SELECTOR, ".form-group.panel-catalog__heading__second label")

        full_text = element.text

        match = re.search(r'(\d+)', full_text)

        if match:
            return int(match.group(1)) 
        else:
            return None 

    def extract_info_juntoz(self ,search_text, id_producto):
        url="https://juntoz.com/"
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
            error_page=self.driver.find_element(By.ID,"main-frame-error")
            resultado["message"]="Error al abrir la página"
            resultado["success"]=False
            return resultado
        except NoSuchElementException:
            pass
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchBar"))
            )

            container_search= self.driver.find_element(By.ID,"searchCatalog")
            search_input= container_search.find_element(By.ID,"inputSearchV2")
            search_input.send_keys(search_text)

            button_search = container_search.find_element(By.XPATH,"//button[@class='btn search-btn btn-search']")

            time.sleep(3)
            res=self.close_modal()
            if res==False:
                resultado["message"]="Error al cerrar el modal"
                resultado["success"]=False
                return resultado
            
            print("Promo cerrada")
            button_search.click()
            self.driver.implicitly_wait(5)
        except Exception:
            resultado["message"]="Error al buscar el producto"
            resultado["success"]=False
            return resultado

        #resultado = None
        total_contenedores = 0
        pagina_actual = 1

        total_productos = self.obtener_numero_productos()
        if total_productos is None:
            print("No se pudo obtener el número total de productos.")
            resultado["message"]="No se pudo obtener el número total de productos."
            resultado["success"]=False
            return resultado

        while True:
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "container-fluid catalog-container"))
                )
                print("No se encontraron resultados para tu búsqueda.")
                resultado["message"]="No se encontraron resultados para tu búsqueda."
                resultado["success"]=False
                return resultado
            except (NoSuchElementException, TimeoutException):
                pass

            # Espera a que el contenedor esté presente
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "catalog-products-container"))
            )

            catalog_container = self.driver.find_element(By.CLASS_NAME, 'catalog-products-container')


            contenedores = catalog_container.find_elements(By.ID, 'product-preview-card')  # Ajusta el selector aquí
            total_contenedores += len(contenedores)
            print(f'Contenedores en esta página: {len(contenedores)}')

            for index, contenedor in enumerate(contenedores):
                # Obtener el nombre del producto

                try:
                    container_data= contenedor.find_element(By.CLASS_NAME, 'product-preview-card__wrapper__heading')
                    product_name=contenedor.find_element(By.XPATH,'//div[@class="product-preview-card__wrapper__footer__product-name"]/a').text
                    iph=container_data.find_element(By.TAG_NAME,'input').get_attribute('value')
                    print(iph)
                except Exception:
                    continue    

                if id_producto == f"{iph}":
                    resultado["success"]=True
                    resultado["message"]="Producto encontrado"
                    resultado["contenedor"]=index+1
                    resultado["pagina"]=pagina_actual
                    resultado["sku"]=iph
                    resultado["nombre_producto"]=product_name
                    nuevo_producto = RankingProduct(
                        product_name=search_text,
                        shop_name="Juntoz",
                        position=index + 1,
                        page=pagina_actual,
                        sku_cf=id_producto,
                        precio_normal=None,
                    )
                    response=nuevo_producto.crear_ranking()
                    if response is None:
                        print("Error al guardar el producto en la base de datos.")
                        response["message"]="Error al guardar el producto en la base de datos."
                        response["success"]=False
                        return response

                    print(f"Coincidencia encontrada en el contenedor {resultado['contenedor']} de la página {resultado['pagina']}: {resultado}")
                    return resultado
            try:
                
                if contenedores:
                    ultimo_contenedor = contenedores[-3]
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", ultimo_contenedor)
                    time.sleep(2)
                    print(f'Scroll hasta el contenedor {total_contenedores}')
                    self.driver.execute_script("window.scrollBy(0, +130);")

                time.sleep(1)
                WebDriverWait(self.driver, 10).until(

                    EC.visibility_of_element_located((By.CLASS_NAME, "pagination"))
                )
                
                # Encuentra el botón "Siguiente"
                next_button = self.driver.find_element(By.XPATH, "//li//a[contains(text(), 'Siguiente')]")
                
                # Clic en el botón "Siguiente" si está habilitado
                if "disabled" not in next_button.get_attribute("class"):
                    try:

                        all_containers= total_contenedores+len(contenedores)
                        print(all_containers)

                        if(all_containers>=total_productos):
                            break
                        
                        next_button.click()

                        time.sleep(1)
                        WebDriverWait(self.driver, 10).until(
                            EC.staleness_of(next_button)  # Espera a que la página cambie antes de proceder
                        )
                        current_url=self.driver.current_url
                        print("URL",current_url)
                        loader_close=self.wait_for_loader_to_disappear()
                        if loader_close==False:
                            resultado["message"]="Error al esperar el loader"
                            resultado["success"]=False
                            return resultado
                        #WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
                    except Exception:
                        resultado["message"]="Error al hacer click en el botón siguiente"
                        resultado["success"]=False
                        return resultado
                pagina_actual += 1  # Aumentar el número de página

            except NoSuchElementException:
                print("No hay más páginas.")
                break

        # Si no se encontró ninguna coincidencia, se retorna None
        print("No se encontraron coincidencias.")
        resultado["message"]="No se encontraron coincidencias."
        resultado["success"]=False
        return resultado































# def validar_info_juntoz(driver: webdriver.Chrome, search_text, texto: str, precio):
#     driver.get("https://juntoz.com/")
#     driver.implicitly_wait(5)
#     texto = texto.lower().strip()
#     try:

#         div_container = driver.find_element(By.CLASS_NAME, "Navbar_navbar--navigation--search-bar__kS6kB")
#         search_input = div_container.find_element(By.CLASS_NAME, "SearchBar_searchInput__jatEt")
#         search_input.send_keys(search_text)
#         search_button = div_container.find_element(By.CLASS_NAME, "SearchBar_searchButton__lFj8T")
#         search_button.click()
#         driver.implicitly_wait(5)
#     except Exception:
#         return None

#     resultado = None
#     total_contenedores = 0
#     pagina_actual = 1

#     while True:
#         try:
#             WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "algolia-search-no-results"))
#             )
#             print("No se encontraron resultados para tu búsqueda.")
#             return None
#         except (NoSuchElementException, TimeoutException):
#             pass

#         # Espera a que el contenedor esté presente
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "catalog-grid"))
#         )

#         catalog_container = driver.find_element(By.CLASS_NAME, 'catalog-container')
#         contenedores = catalog_container.find_elements(By.ID, 'product-border')  # Ajusta el selector aquí
#         total_contenedores += len(contenedores)
#         print(f'Contenedores en esta página: {len(contenedores)}')

#         for index, contenedor in enumerate(contenedores):
#             # Obtener el nombre del producto
#             try:
#                 nombre_element = contenedor.find_element(By.CLASS_NAME, 'catalog-product-details__name')
#                 nombre_producto = nombre_element.text.lower().strip()
#                 print(f'Nombre del producto: {nombre_producto}')
#             except NoSuchElementException:
#                 print("Nombre del producto no encontrado.")
#                 nombre_producto = None

#             # Si no se encontró el nombre, pasa al siguiente contenedor
#             if not nombre_producto:
#                 continue

#             precios_element = None
#             try:
#                 WebDriverWait(driver,10).until(
#                     EC.presence_of_element_located((By.CLASS_NAME,'catalog-product-details__prices'))
#                 )
#                 precios_element = contenedor.find_element(By.CLASS_NAME,'catalog-product-details__prices')
#             except Exception:
#                 continue

#             precio_normal = obtener_precio(precios_element, 'Precio Normal')
#             precio_internet = obtener_precio(precios_element, 'Precio Internet')
#             precio_oferta = obtener_precio(precios_element, 'Precio Ripley')
#             ratio_similitud = fuzz.token_sort_ratio(nombre_producto, texto)
#             if ratio_similitud >= 70 and (
#                     (precio_normal and precio in precio_normal) or
#                     (precio_internet and precio in precio_internet) or
#                     (precio_oferta and precio in precio_oferta)):
#                     resultado = {
#                         'nombre': nombre_producto,
#                         'precio_normal': precio_normal ,
#                         'precio_internet':precio_internet ,
#                         'precio_ripley_oferta':precio_oferta,
#                         'contenedor': index + 1,  # Posición dentro de la página actual
#                         'pagina': pagina_actual  # Número de la página
#                     }
#                     print(f"Coincidencia encontrada en el contenedor {resultado['contenedor']} de la página {resultado['pagina']}: {resultado}")
#                     return resultado

#         try:
            
#             WebDriverWait(driver, 10).until(
#                 EC.invisibility_of_element_located((By.CLASS_NAME, "loading-screen"))
#             )

#             # Verifica si hay contenedores y realiza scroll al último contenedor
#             if contenedores:
#                 ultimo_contenedor = contenedores[-1]
#                 driver.execute_script("arguments[0].scrollIntoView();", ultimo_contenedor)
#                 print(f'Scroll hasta el contenedor {total_contenedores}')

#             siguiente_boton = driver.find_element(By.XPATH, '//li[a/span[text()="»"]]')

#             continue_li = driver.find_elements(By.XPATH, '//ul[@class="pagination"]//li')
#             if continue_li:
#                 ultimo_li = continue_li[-1]
#                 href = ultimo_li.find_element(By.TAG_NAME, 'a').get_attribute("href")
#                 print(href)
#                 if "#" in href:
#                     break

#             if 'is-disabled' in siguiente_boton.get_attribute('class'):
#                 print("El botón de 'Siguiente' está deshabilitado. No hay más páginas.")
#                 break

#             WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, '//li[a/span[text()="»"]]'))
#             )
#             #siguiente_boton.click()
#             driver.get(href)
#             #print(url)
#             #driver.implicitly_wait(5)
#             #time.sleep(5)
#             pagina_actual += 1  # Aumentar el número de página

#         except NoSuchElementException:
#             print("No hay más páginas.")
#             break

#     # Si no se encontró ninguna coincidencia, se retorna None
#     print("No se encontraron coincidencias.")
#     return None

