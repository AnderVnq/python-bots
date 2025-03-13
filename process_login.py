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





class SheinController():
    def __init__(self, language='en_US'):
        self.language = language
        self.driver = self.init_driver()
        self.url_base = "https://us.shein.com/"
        self.url_base_usa="https://us.shein.com/"
        self.soup = None
        # self.shn_proc = SheinProcessor()
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







    def login_data(self):

        self.driver.get(self.url_base_usa+"user/auth/login")
        try:
             
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="page__login-newUI-continue"]'))
            )

            container_input_email= self.driver.find_element(By.XPATH,"//div[@class='email-recommend-input']")
            input_email=container_input_email.find_element(By.XPATH,".//div//input")
            input_email.click()
            actions=ActionChains(self.driver)

            for letra in self.email:
                actions.send_keys(letra)
                time.sleep(random.uniform(0.1,0.5))


            actions.perform()

            WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.XPATH,"//div[@class='actions']//div[@class='login-point_button']/button"))
            )

            container_click_button=self.driver.find_element(By.XPATH,"//div[@class='actions']//div[@class='login-point_button']/button")
            container_click_button.click()

            input("esperar para  depurar")


            #contraseña 

            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="main-content"]'))
            )


            #//div[@class="main-content"]//div[@class="page__login_input-filed page__login-newUI-input"]//div[@class="sui-input"]//input
            container_modal=self.driver.find_element(By.XPATH,'//div[@class="main-content"]')

            input_password=container_modal.find_element(By.XPATH,'.//div[@class="page__login_input-filed page__login-newUI-input"]//div[@class="sui-input"]//input')
            input_password.click()
            actions_password=ActionChains(self.driver)


            for letra in self.password:
                actions_password.send_keys(letra)
                time.sleep(random.uniform(0.1,0.5))


            actions_password.perform()



            WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.XPATH,".//div[@class='actions']//div[@class='login-point_button']/button"))
            )

            continue_click=container_modal.find_element(By.XPATH,'.//div[@class="actions"]//div[@class="login-point_button"]/button')
            current_url=self.driver.current_url
            continue_click.click()

            input("en el click de identificate")

            if self.driver.current_url==current_url:
                self.driver.close()
                self.driver.quit()
                return False
        
            self.driver.close()
            self.driver.quit()
            return True
        except Exception as e:
            print(e)
            return False





if __name__=="__main__":
    shein_c=SheinController()
    response_login=shein_c.login_data()
    print(f"el response final del login es: {response_login}")