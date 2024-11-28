from selenium import webdriver
from selenium.webdriver.chrome.options import Options


#import webdriver remote




class WebDriverManager:
    def __init__(self, language='en_US', proxy=None):
        self.language = language
        self.proxy = proxy
        self.driver = None
    
    def iniciar_webdriver(self):
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            'Accept': "*/*",
            'Accept-Language': self.language,
            'Accept-Encoding': "gzip,deflate,br",
            'Connection': "keep-alive"
        }
        selenium_url = 'http://selenium:4444/wd/hub'
        opts = Options()
        opts.add_argument("--start-maximized")
        # opts.add_argument("--headless")
        opts.add_argument("--disable-notifications")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-extensions")
        #opts.add_argument("--blink-settings=imagesEnabled=false")
        opts.add_argument("--ignore-certificate-errors")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        opts.add_argument(f'User-agent={headers["User-Agent"]}')
        
        if self.proxy:
            opts.add_argument(f'--proxy-server={self.proxy}')

        self.driver = webdriver.Chrome(options=opts)
        # self.driver= webdriver.Remote(
        #     command_executor=selenium_url,
        #     options=opts
        # )
        return self.driver

    def finalizar_webdriver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None