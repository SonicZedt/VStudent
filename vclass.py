from log import debug
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class VStudent:
    @property
    def active_browser(self):
        return self.browser

    def __init__(self,
                 config,
                 driver_path:str='driver/geckodriver.exe',
                 driver_log_path:str='driver/geckodriver.log',
                 verbose:int=1,
                 confirm:bool=True):
        self.verbose = verbose
        self.config = config
        debug.log(f"VStudent: {config['login']['username']}\n")

        # VStudent confirmation
        if confirm:
            self._vstudent_confirmation()

        debug.separate(self.verbose)
        debug.log("Opening browser", self.verbose)
        # TODO: multi browser support
        self.browser = webdriver.Firefox(service=Service(
            executable_path=driver_path,
            log_path=driver_log_path))

    def _vstudent_confirmation(self):
        while True:
            confirm = input("Continue as specified VStudent? [Y/n]: ").lower()
            if confirm in ('y', 'yes'):
                break
            elif confirm in ('n', 'no'):
                exit()
            else:
                print("Invalid input!")

    def login(self, nologin:bool=False, exit_on_fail:bool=True) -> bool:
        """ Login to v-class using given credential in config_path """
        # go to v-class login page
        debug.log(f"Loging in as [{self.config['login']['username']}]", self.verbose)
        self.browser.get('https://v-class.gunadarma.ac.id/login/index.php')
        WebDriverWait(self.browser, 5).until(EC.presence_of_all_elements_located((By.ID, 'password')))

        # fill username and password form
        form_username = self.browser.find_element(By.ID, 'username')
        form_username.send_keys(self.config['login']['username'])
        form_password = self.browser.find_element(By.ID, 'password')
        form_password.send_keys(self.config['login']['password'])

        # press log in button
        if nologin:
            return
        button_login = self.browser.find_element(By.ID, 'loginbtn')
        button_login.click()

        # login confirmation
        try:
            assert self.browser.current_url == 'https://v-class.gunadarma.ac.id/my/'
            self.success = True
            debug.log("Login successful\n", self.verbose)
        except:
            debug.log("Login failed", self.verbose)
            self.success = False
            if exit_on_fail:
                exit()

        return self.success

class Course:
    def __init__(self, browser:WebDriver, page_url:str, verbose:int=1):
        self.browser = browser
        self.page_url = page_url
        self.verbose = verbose

        # go to course page
        self.browser.get(page_url)
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_all_elements_located((By.ID, 'page-header')))

        # course page confirmation
        try:
            assert self.browser.current_url == page_url
            debug.log("Course page reached", self.verbose, newline=True)
        except:
            debug.log("Failed to reach course page", self.verbose, newline=True)
            exit()

    def describe(self) -> dict:
        """ Course description """
        desc = {
            'id' : '',
            'title' : '',
            'url' : ''
        }

        desc['id'] = self.page_url.split('id=', 1)[1]
        desc['title'] = self.browser.find_element(By.CSS_SELECTOR, 'h1').text
        desc['url'] = self.page_url

        return desc

class Assignment:
    def __init__(self, browser:WebDriver, page_url:str, verbose:int=1):
        self.browser = browser
        self.page_url = page_url
        self.verbose = verbose

        # go to assignment page
        self.browser.get(page_url)
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_all_elements_located((By.ID, 'page-header')))

        # assignment page confirmation
        try:
            assert self.browser.current_url == page_url
            debug.log("Assignment page reached", self.verbose, newline=True)
            debug.log(f"Course title:\n{self.browser.find_element(By.CSS_SELECTOR, 'h1').text}")
        except:
            debug.log("Failed to reach assignment page", self.verbose, newline=True)
            exit()

    def describe(self) -> dict:
        """ Assignment description """
        desc = {
            'id' : '',
            'title' : '',
            'url' : ''
        }

        desc['id'] = self.page_url.split('id=', 1)[1]
        desc['title'] = self.browser.find_element(By.CSS_SELECTOR, 'h1').text
        desc['url'] = self.page_url

    def attempt(self):
        # TODO start answering attempt
        return