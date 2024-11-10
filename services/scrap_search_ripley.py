from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
from utils.cookies import cookies

def iniciar_webdriver(language='en_US',proxy=None):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        'Accept': "*/*",
        'Accept-Language': language,
        'Accept-Encoding': "gzip,deflate,br",
        'Connection': "keep-alive"
    }

    opts = Options()
    opts.add_argument("--start-maximized")
    #opts.add_argument("--headless")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    #opts.add_argument("--blink-settings=imagesEnabled=false") 
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument(f'User-agent={headers["User-Agent"]}')
    if proxy:
        opts.add_argument(f'--proxy-server={proxy}')

    driver = webdriver.Chrome(options=opts)
    return driver


# def iniciar_webdriver(language='en_US',proxy=None):
#     driver = Driver(uc=True)
#     url = "https://simple.ripley.com.pe/"
#     driver.uc_open_with_reconnect(url, 4)
#     driver.uc_gui_click_captcha()
#     driver.quit()
        





def add_cookies_to_driver(driver, cookies):
    # Asegúrate de que la página esté cargada antes de añadir las cookies
    driver.get("https://simple.ripley.com/")
    driver.delete_all_cookies()  # Limpiar las cookies previas

    # for cookie in cookies:
    #     driver.add_cookie(cookie)  # Añadir cada cookie

    time.sleep(1)  # Esperar un poco para que se apliquen las cookies
    driver.refresh()  


def extract_info_search(driver:webdriver.Chrome,search_text,pmp):

    add_cookies_to_driver(driver,cookies)
    # driver.get("https://simple.ripley.com.pe/")
    # driver.implicitly_wait(5)

    # try :
    #     WebDriverWait(driver,10).until(
    #         EC.presence_of_element_located((By.ID,"gLIfn4"))
    #     )
    #     container_captcha = driver.find_element(By.ID,"gLIfn4")
    #     location = container_captcha.location
    #     size = container_captcha.size

    #     checkbox_x_2 = 444.5
    #     checkbox_y_2 = 22.5
    #     time.sleep(3)
    #     # Realiza clic en el checkbox con diferentes valores de offset
    #     checkbox_x = location['x'] + int(size['width'] * 0.2) - 157  # Un valor fijo para prueba
    #     checkbox_y = (location['y'] + int(size['height'] // 2))-5

    #     driver.execute_script(f"var circle = document.createElement('div');"
    #                   f"circle.style.position = 'absolute';"
    #                   f"circle.style.width = '10px';"
    #                   f"circle.style.height = '10px';"
    #                   f"circle.style.backgroundColor = 'red';"
    #                   f"circle.style.borderRadius = '50%';"
    #                   f"circle.style.left = '{checkbox_x}px';"
    #                   f"circle.style.top = '{checkbox_y}px';"
    #                   f"document.body.appendChild(circle);")
    #         # Mover el ratón a la posición calculada y hacer clic
    #     actions = ActionChains(driver)
    #     actions.move_by_offset(checkbox_x, checkbox_y).click().perform()
        

    #     #iframe= container_captcha.find_element(By.TAG_NAME, "iframe")


    #     #ActionChains(driver).move_to_element(container_captcha).perform()
    #     #container_captcha.click()
    #     print(container_captcha.parent)
    #     print("Captcha detectado")
    # except Exception as ex:
    #     print("Error",ex)
    #     return None
    try:

        div_container = driver.find_element(By.CLASS_NAME, "Navbar_navbar--navigation--search-bar__kS6kB")
        search_input = div_container.find_element(By.CLASS_NAME, "SearchBar_searchInput__jatEt")
        search_input.send_keys(search_text)
        search_button = div_container.find_element(By.CLASS_NAME, "SearchBar_searchButton__lFj8T")
        search_button.click()
        driver.implicitly_wait(5)
    except Exception:
        return None

    #resultado = None
    total_contenedores = 0
    pagina_actual = 1

    while True:
        try:
            WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "algolia-search-no-results"))
            )
            return None
        except Exception:
            pass

        WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.CLASS_NAME,"catalog-grid"))
        )

        catalog_container= driver.find_element(By.CLASS_NAME,"catalog-container")
        contenedores = catalog_container.find_elements(By.ID,"product-border")
        total_contenedores += len(contenedores)
        print(f"Total de contenedores: {total_contenedores}")
        for index,contenedor in enumerate(contenedores):
            try:
                print("indice",index)
                enlace = contenedor.find_element(By.TAG_NAME, 'a')
                product_id = enlace.get_attribute('id')

                # Si el ID coincide con el que buscas
                print("PMP",pmp)
                print("product_id",product_id)
                if product_id == f"{pmp}":
                    response = {
                        "success": True,
                        "message": "Producto encontrado",
                        "contenedor": index + 1,
                        "pagina": pagina_actual
                    }
                print(response)
                return response
            except Exception:
                continue

        try:

            WebDriverWait(driver,10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,"loading-screen"))
            )

            if contenedores:
                ultimo_contenedor = contenedores[-1]
                driver.execute_script("arguments[0].scrollIntoView();",ultimo_contenedor)
                print(f"sroll hasta el contenedor {total_contenedores}")

            
            siguiente_boton = driver.find_element(By.XPATH, '//li[a/span[text()="»"]]')

            continue_li = driver.find_elements(By.XPATH, '//ul[@class="pagination"]//li')
            if continue_li:
                ultimo_li = continue_li[-1]
                href = ultimo_li.find_element(By.TAG_NAME, 'a').get_attribute("href")
                print(href)
                if "#" in href:
                    break

            if 'is-disabled' in siguiente_boton.get_attribute('class'):
                print("El botón de 'Siguiente' está deshabilitado. No hay más páginas.")
                break

            # WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.XPATH, '//li[a/span[text()="»"]]'))
            # )
            #siguiente_boton.click()
            driver.get(href)
            #print(url)
            #driver.implicitly_wait(5)
            #time.sleep(5)
            pagina_actual += 1
        except (NoSuchElementException,TimeoutException):
            break 
    
    print("No se encontraron coincidencias")
    return None
















# class MyTestCase(BaseCase):
#     def iniciar_webdriver(self, language='en_US', proxy=None):
#         # Iniciar WebDriver con SeleniumBase
#         self.driver = Driver(uc=True)
#         url = "https://gitlab.com/users/sign_in"
#         self.driver.uc_open_with_reconnect(url, 4)
#         self.driver.uc_gui_click_captcha()
#         self.driver.quit()