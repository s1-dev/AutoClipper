from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time

DRIVER_PATH = r"C:\code\downloads\chromedriver-win64\chromedriver.exe"  
DEFAULT_WAIT_TIME = 10

def setupWebDriver():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    service = Service(DRIVER_PATH)

    return webdriver.Chrome(service=service, options=chrome_options) 

def launchYoutubeVideo(driver, videoUrl):
    driver.get(videoUrl)

    playButton = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "ytp-play-button"))
    )
    playButton.click()


    fullScreenButton = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "ytp-fullscreen-button"))
    )
    fullScreenButton.click()

    print("INITIALIZED", flush=True)

def main():
    url = r"https://www.youtube.com/watch?v=U__aholYpL4"
    driver = setupWebDriver()
    launchYoutubeVideo(driver, url)
    
    time.sleep(500000)
    print("COMPLETED", flush=True)
    driver.quit()


if __name__ == "__main__":
    main()
    