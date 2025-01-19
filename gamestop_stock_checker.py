import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables from a .env file
load_dotenv()

def check_stock(url):
    options = Options()
    options.headless = True  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(url)
    
    try:
        # Explicit wait for the stock status button to be present
        stock_status_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'pdp-delivery-option-button--ship'))
        )
        
        button_classes = stock_status_element.get_attribute('class').split()
        if 'unavailable' in button_classes:
            return "Item is unavailable"
        else:
            return "Item is available"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        driver.quit()

def send_email(subject, body, to_email):
    from_email = os.getenv("FROM_EMAIL")
    from_password = os.getenv("FROM_PASSWORD")

    if not from_email or not from_password:
        raise ValueError("Environment variables FROM_EMAIL and FROM_PASSWORD must be set")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

# List of URLs to check
urls = [
    'https://www.gamestop.com/video-games/retro-gaming/products/pokemon-leafgreen-version---game-boy-advance/122849.html',
    'https://www.gamestop.com/video-games/xbox-series-x%7Cs/products/ea-sports-fc-25---xbox-series-x/415834.html'
    # Add more URLs here
]

# Check stock for each URL and collect the results
available_results = []
for url in urls:
    result = check_stock(url)
    if "Item is available" in result:
        available_results.append(f"URL: {url} - {result}")

# Send the results via email if at least one item is available
if available_results:
    email_body = "\n".join(available_results)
    send_email("Stock Check Results", email_body, os.getenv("TO_EMAIL"))