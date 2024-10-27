import time
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

class SMSSender:
    _instance = None

    def __new__(cls, base_url, password):
        if cls._instance is None:
            cls._instance = super(SMSSender, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, base_url, password):
        if self.initialized:
            return

        self.base_url = base_url
        self.password = password
        self.session_id = None
        self.setup_driver()
        self.login()
        self.initialized = True

    def setup_driver(self):
        options = Options()
        service = Service(log_path=os.devnull)
        self.driver = webdriver.Firefox(options=options, service=service)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
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

            start_time = time.time()
            while time.time() - start_time < 10:
                cookies = self.driver.get_cookies()
                for cookie in cookies:
                    if cookie['name'] == 'JSESSIONID':
                        self.session_id = cookie['value']
                        break
                if self.session_id:
                    break
                time.sleep(0.5)

            if not self.session_id:
                raise Exception("Failed to get session ID after 10 seconds")


            self.driver.quit()

        except Exception as e:
            self.driver.quit()
            raise Exception(f"Login failed: {str(e)}")

    def send_sms(self, phone_number: str, message: str, retries: int = 3):
        try:
            data = f"""[LTE_SMS_SENDNEWMSG#0,0,0,0,0,0#0,0,0,0,0,0]0,3\nindex=1\nto={phone_number}\ntextContent={message}"""

            headers = {
                'Cookie': f'JSESSIONID={self.session_id}'
            }

            print(f"Sending SMS request:")
            print(f"URL: {self.base_url}/cgi?2")
            print(f"Headers: {headers}")
            print(f"Data: {data}")

            response = requests.post(f"{self.base_url}/cgi?2", data=data, headers=headers)

            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Response body: {response.text}")

            if response.status_code == 200:
                print(f"SMS sent successfully to {phone_number}")
                return {"status": "success", "message": "SMS sent successfully"}
            else:
                print(f"Failed to send SMS: {response.status_code}")
                return {"status": "error", "message": f"Failed to send SMS: {response.status_code}"}

        except Exception as e:
            print(f"Exception occurred while sending SMS: {str(e)}")
            return {"status": "error", "message": str(e)}

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
