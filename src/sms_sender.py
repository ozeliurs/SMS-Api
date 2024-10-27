import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

class SMSSender:
    _instance = None

    def __new__(cls, base_url, password) -> 'SMSSender':
        if cls._instance is None:
            cls._instance = super(SMSSender, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, base_url, password) -> None:
        if self.initialized:
            return

        self.base_url = base_url
        self.password = password
        self.setup_driver()
        self.login()
        self.navigate_to_sms_page()
        self.initialized = True

    def setup_driver(self) -> None:
        options = Options()
        service = Service(log_path=os.devnull)
        self.driver = webdriver.Firefox(options=options, service=service)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self) -> None:
        try:
            self.driver.get(self.base_url)

            input_password = self.wait.until(
                EC.presence_of_element_located((By.ID, "pc-login-password"))
            )
            input_password.send_keys(self.password)

            button_login = self.driver.find_element(By.ID, "pc-login-btn")
            button_login.click()

            try:
                button_confirm = self.wait.until(
                    EC.presence_of_element_located((By.ID, "confirm-yes"))
                )
                button_confirm.click()
            except:
                pass

        except Exception as e:
            self.driver.quit()
            raise Exception(f"Login failed: {str(e)}")

    def navigate_to_sms_page(self) -> None:
        try:
            # Wait for advanced button and click
            advanced_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "advanced"))
            )
            advanced_button.click()

            # Wait for SMS inbox link and click
            sms_inbox = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[url='lteSmsInbox.htm']"))
            )
            sms_inbox.click()

            # Wait for new message link and click
            new_msg = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[url='lteSmsNewMsg.htm']"))
            )
            new_msg.click()

        except Exception as e:
            raise Exception(f"Navigation failed: {str(e)}")

    def send_sms(self, phone_number: str, message: str, retries: int = 3) -> dict:
        try:
            # self.navigate_to_sms_page()

            input_to = self.wait.until(
                EC.presence_of_element_located((By.ID, "toNumber"))
            )
            input_to.clear()
            input_to.send_keys(phone_number)

            input_content = self.driver.find_element(By.ID, "inputContent")
            input_content.clear()
            input_content.send_keys(message)

            button_send = self.driver.find_element(By.ID, "send")
            button_send.click()

            return {"status": "success", "message": "SMS sent successfully"}
        except Exception as e:
            # If there's an error, restart browser and try again
            try:
                if retries > 0:
                    self.driver.quit()
                    self.setup_driver()
                    self.login()
                    return self.send_sms(phone_number, message, retries - 1)
                else:
                    return {"status": "error", "message": "Max retries exceeded"}
            except Exception as retry_error:
                return {"status": "error", "message": str(retry_error)}

    def __del__(self) -> None:
        if hasattr(self, 'driver'):
            self.driver.quit()
