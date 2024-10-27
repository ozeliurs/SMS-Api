from dotenv import load_dotenv
import os
import sys

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
PASSWORD = os.getenv("PASSWORD")
API_KEY = os.getenv("API_KEY")

if not BASE_URL:
    print("BASE_URL environment variable not set")
    sys.exit(1)

if not BASE_URL.startswith('http'):
    BASE_URL = 'http://' + BASE_URL

if not PASSWORD:
    print("PASSWORD environment variable not set")
    sys.exit(1)

if not API_KEY:
    print("API_KEY environment variable not set")
    sys.exit(1)
