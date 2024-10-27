import os
import time
import queue
import threading

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SMSSender:
    _instance = None

    def __new__(cls, base_url, password) -> 'SMSSender':
        if cls._instance is None:
            cls._instance = super(SMSSender, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, base_url, password, retries=5) -> None:
        if self.initialized:
            return

        self.base_url = base_url
        self.password = password

        self.sms_queue = queue.Queue()
        self.is_sending = False
        self.send_lock = threading.Lock()

        while retries > 0:
            try:
                self.setup_driver()
                self.login()
                self.navigate_to_sms_page()
                self.initialized = True
                break
            except Exception as e:
                retries -= 1
                if hasattr(self, 'driver'):
                    self.driver.quit()
                if retries == 0:
                    raise Exception(f"Failed to initialize after 3 retries: {str(e)}")

    def setup_driver(self) -> None:
        options = Options()
        service = Service(log_output=os.devnull)
        self.driver = webdriver.Chrome(options=options, service=service)
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
            print("Starting navigation to SMS page")

            # Wait for interface name to be populated
            print("Waiting for #interfaceNamenterfaceName to be populated...")
            self.wait.until(
                lambda driver: driver.find_element(By.ID, "interfaceName").get_attribute("value") != ""
            )

            # Find and click advanced button
            advanced_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "advanced"))
            )

            print("Found advanced button, clicking...")
            advanced_button.click()

            # Wait for SMS inbox link and click
            print("Waiting for SMS inbox link...")
            sms_inbox = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[url='lteSmsInbox.htm']"))
            )
            print("Found SMS inbox link, clicking...")
            time.sleep(.5)
            sms_inbox.click()

            # Wait for new message link and click
            print("Waiting for new message link...")
            new_msg = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[url='lteSmsNewMsg.htm']"))
            )
            print("Found new message link, clicking...")
            time.sleep(.5)
            new_msg.click()

            print("Successfully navigated to SMS page")

        except Exception as e:
            print(f"Navigation error: {str(e)}")
            raise Exception(f"Navigation failed: {str(e)}")

    def send_sms(self, phone_number: str, message: str, retries: int = 3) -> dict:
        try:
            self.wait.until(
                EC.invisibility_of_element_located((By.ID, "mask"))
            )

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
            print(f"Error sending SMS: {str(e)}, retries left: {retries}, restarting browser...")
            # If there's an error, restart browser and try again
            try:
                if retries > 0:
                    self.driver.quit()
                    self.setup_driver()
                    self.login()
                    self.navigate_to_sms_page()
                    return self.send_sms(phone_number, message, retries - 1)
                else:
                    return {"status": "error", "message": "Max retries exceeded"}
            except Exception as retry_error:
                return {"status": "error", "message": str(retry_error)}

    def queued_send_sms(self, phone_number: str, message: str) -> dict:
        """
        Queues an SMS for sending and waits until it's sent.
        Returns only after the SMS has been processed.
        """
        try:
            # Create a result container
            result_container = {"status": None, "message": None}

            with self.send_lock:
                if not self.is_sending:
                    self.is_sending = True
                    try:
                        # Send directly if no queue
                        result = self.send_sms(phone_number, message)
                        result_container["status"] = result["status"]
                        result_container["message"] = result["message"]
                    finally:
                        self.is_sending = False
                else:
                    # Queue the message if another one is being sent
                    self.sms_queue.put((phone_number, message, result_container))

                    # Wait for the message to be processed
                    while result_container["status"] is None:
                        time.sleep(0.5)
                        # Process queue if we're not sending
                        if not self.is_sending:
                            self._process_queue()

            return result_container

        except Exception as e:
            return {"status": "error", "message": f"Queue error: {str(e)}"}

    def _process_queue(self):
        """
        Processes any pending SMS in the queue
        """
        try:
            while not self.sms_queue.empty():
                with self.send_lock:
                    if not self.is_sending:
                        self.is_sending = True
                        try:
                            # Get next SMS from queue
                            phone_number, message, result_container = self.sms_queue.get_nowait()

                            # Send the SMS
                            result = self.send_sms(phone_number, message)

                            # Update result container
                            result_container["status"] = result["status"]
                            result_container["message"] = result["message"]

                            # Mark task as done
                            self.sms_queue.task_done()
                        finally:
                            self.is_sending = False
                    else:
                        break
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error processing queue: {str(e)}")

    def __del__(self) -> None:
        if hasattr(self, 'driver'):
            self.driver.quit()
