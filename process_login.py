from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.action_chains import ActionChains
import random

from models.entities.ecomerce.shein.shein_processor import SheinProcessor 





class SheinController():
    def __init__(self, language='en_US'):
        self.language = language
        self.driver = self.init_driver()
        self.url_base = "https://us.shein.com/"
        self.url_base_usa="https://us.shein.com/"
        self.soup = None
        self.shn_proc = SheinProcessor()
        # self.logger = BugLogger()
        self.on_device_process = 'vps1'
        self.batch_size = 12
        self.sku_detail = []
        self.sku_data = []
        self.lenght_sku_list = None
        self.affected_rows = 0
        # self.images_path = os.getenv('IMAGES_PATH')
        # self.domain_path = os.getenv('DOMAIN_LOCAL')
        self.url_complete=None
        self.is_found=None
        self.email="luispubg9905@hotmail.com"
        self.password="Heaveny2"
        self.email2="anderson_escorpio_122@hotmail.com"
 
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
            opts.add_experimental_option("prefs", {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            })  

            # Intenta conectarte al servidor de Selenium
            # driver= webdriver.Remote(
            #     command_executor=selenium_url,
            #     options=opts
            # )

            driver= webdriver.Chrome(options=opts)
            return driver




    def get_product_list(self,platform : str = 'Shein'):

        response =  self.shn_proc.get_product_list_proc(platform,self.on_device_process)
        if response:
            self.set_sku_data_list(response)

            if self.login_data():
                self.update_data_sku_price()
            else:
                print("Error al iniciar sesión")
                if self.driver.service.process is not None:
                    self.driver.close()
                    self.driver.quit()
                return


    def set_sku_data_list(self,data):
        self.sku_data = data

    def get_sku_data_list(self):
        return  self.sku_data


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

                    if "captcha" in self.driver.current_url or index == 35:
                        if self.logout_data():
                            self.updated_rows(1)
                    else:
                        time.sleep(random.uniform(1,3))
                        self.updated_rows(1)
        except Exception as e:
            print(f"Error al actualizar los datos: {str(e)}")
            if self.driver.service.process is not None:  # Validate if the driver is still running
                self.driver.close()
                self.driver.quit()
            return



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
            
            return self.login_data(refresh=False)

        except Exception as e:
            print(e)
            return False


    def login_data(self,refresh=True)->bool:

        if refresh:
            self.driver.get(self.url_base_usa+"user/auth/login")
        try:
             
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="page__login-newUI-continue"]'))
            )

            container_input_email= self.driver.find_element(By.XPATH,"//div[@class='email-recommend-input']")
            input_email=container_input_email.find_element(By.XPATH,".//div//input")
            input_email.click()
            #actions=ActionChains(self.driver)

            for letra in self.email:
                input_email.send_keys(letra)
                time.sleep(random.uniform(0.2,0.4))
                #actions.pause(time.sleep(random.uniform(1,2)))


            #actions.perform()

            WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.XPATH,"//div[@class='actions']//div[@class='login-point_button']/button"))
            )

            container_click_button=self.driver.find_element(By.XPATH,"//div[@class='actions']//div[@class='login-point_button']/button")
            container_click_button.click()

            #input("esperar para  depurar")


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
            self.driver.close()
            self.driver.quit()
            return False


    def affected_data(self):
        return self.affected_rows
    
    def updated_rows(self, affected : int):
        
        if self.affected_rows is None:
            self.affected_rows = 0 
        self.affected_rows += affected



if __name__=="__main__":
    shein_c=SheinController()
    shein_c.get_product_list()
    count=shein_c.affected_data()
    if shein_c.driver.service.process is not None:  # Validate if the driver is still running
        shein_c.driver.close()
        shein_c.driver.quit()
    record = "Registro"
    ecomerce = "Shein"
    if count > 0:
        print(f"{count} {record}{'s' if count > 1 else ''}" f" actualizado{'s' if count > 1 else ''}",True,ecomerce)
    else:
        print(f"No se procesó ningún SKU status False ecomerce {ecomerce} variantes_extraidas A")