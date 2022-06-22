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
                 verbose:int=1):
        self.verbose = verbose
        self.config = config
        debug.log(f"VStudent: {config['login']['username']}\n")

        # VStudent confirmation
        if self.config['vclass'].getboolean('login_confirmation'):
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

        # click log in button
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

class Quiz:
    def __init__(self, browser:WebDriver, page_url:str, verbose:int=1):
        self.browser = browser
        self.page_url = page_url
        self.verbose = verbose

        # go to quiz page
        self.browser.get(page_url)
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_all_elements_located((By.ID, 'page-header')))

        # quiz page confirmation
        try:
            assert self.browser.current_url == page_url
            debug.log("Quiz page reached", self.verbose, newline=True)
            debug.log(f"Course title:\n{self.browser.find_element(By.CSS_SELECTOR, 'h1').text}")
        except:
            debug.log("Failed to reach quiz page", self.verbose, newline=True)
            exit()

    def describe(self) -> dict:
        """ Quiz description """
        desc = {
            'id' : '',
            'title' : '',
            'url' : ''
        }

        desc['id'] = self.page_url.split('id=', 1)[1]
        desc['title'] = self.browser.find_element(By.CSS_SELECTOR, 'h1').text
        desc['url'] = self.page_url

    def attempt(self) -> int:
        """ Attempt quiz
        return: question count """
        button_attempt = self.browser.find_element(By.LINK_TEXT, 'Attempt quiz now')
        button_attempt.click()

        WebDriverWait(self.browser, 5).until(
            EC.presence_of_all_elements_located((By.ID, 'id_submitbutton')))
        button_confirm_attemp = self.browser.find_element(By.ID, 'id_submitbutton')
        button_confirm_attemp.click()

        WebDriverWait(self.browser, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'endtestlink')))

        #try:
        #    assert '######TEXXXTTT' in self.browser.current_url
        #    debug.log("Quiz attempted", self.verbose, newline=True)
        #except:
        #    debug.log("Failed to attempt quiz page", self.verbose, newline=True)
        #    exit()

        # should be _str_ (1 of n) where n is total question
        return int(self.browser.title.rsplit(' ', 1)[1][:-1])

    def get_current_question(self) -> str:
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'qtext')))
        question = self.browser.find_element(By.CLASS_NAME, 'qtext').text       
        
        if not question:
            debug.log("No question available", self.verbose, newline=True)
            return ''

        return question

    def answer_current_question(self, question:str, answer:str, debug_qna:bool=True) -> bool:
        if debug_qna:
            debug.log(f"Q: {question}")
            debug.log(f"A: {answer}")
        
        # Find answer in quiz page and click it
        answer_element = self.browser.find_element(By.PARTIAL_LINK_TEXT, answer)
        if not answer_element:
            debug.log("Failed to answer given question", self.verbose)
            return False
        answer_radio = self.browser.find_element(By.ID, answer_element.id)
        answer_radio.click()

        debug.log("Question answered", self.verbose)
        return True

    def next_question(self, check:bool=False) -> bool:
        """ Click next question button if exist
        return: True if button exist """

        next_button = self.browser.find_element(By.LINK_TEXT, 'Next page')
        if next_button:
            if not check:
                next_button.click()
            return True

        return False