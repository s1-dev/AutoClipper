from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import asyncio
import time
import json
import sys

DRIVER_PATH = r"C:\code\chromedriver-win64\chromedriver-win64\chromedriver.exe"  
DEFAULT_WAIT_TIME = 30

class DriverManager:
    def __init__(self):
        self.driver = None

    def setupDriver(self):
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        service = Service(DRIVER_PATH)

        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def quitDriver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error quitting driver: {e}")
            self.driver = None

    def replaceDriver(self):
        self.quitDriver()
        self.setupDriver()

def launchFs1Site(driver, hasAlreadyInit):
    driver.get("https://www.foxsports.com/live/fs1") # Potential issue with this get call taking too long
    driver.refresh() # Necessary due to issue with fs1 site lol

    play_button = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "overlay-play-button"))
    )
    play_button.click()

    video_element = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.presence_of_element_located((By.CLASS_NAME, "jw-video"))
    )
    actions = ActionChains(driver)
    actions.move_to_element(video_element).perform()
    
    fullscreen_button = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='fullscreenButton']"))
    )
    fullscreen_button.click()
    
    token = driver.execute_script("return window.localStorage.getItem('_WIS_pvpAuth');")
    token = json.loads(token)
    expirationTime = token['expires']
    if not hasAlreadyInit:
        print("INITIALIZED", flush=True)
    return expirationTime 

async def startFs1SiteAndListeners(driverManager, hasAlreadyInit):
    initialExpirationTime = launchFs1Site(driverManager.driver, hasAlreadyInit)

    runningTasks = []
    stdinTask = asyncio.create_task(listenForCommands(driverManager, runningTasks), name="StdinListener")
    monitorExpirationTask = asyncio.create_task(monitorForRefresh(driverManager, initialExpirationTime, runningTasks), name="ExpirationMonitor")
    runningTasks.extend([stdinTask, monitorExpirationTask])

    return runningTasks 
    
async def listenForCommands(driverManager, runningTasks):
    while True:
        userInput = await asyncio.to_thread(sys.stdin.readline)
        userInput = userInput.strip()
        if userInput == "REFRESH":
            await relaunchFs1Site(driverManager, runningTasks)
            break

async def monitorForRefresh(driverManager, expirationTime, runningTasks):
    expirationTime = expirationTime / 1000  # ms to s
    while True:
        now = time.time()
        timeToExpiration = expirationTime - now

        if 0 <= timeToExpiration <= 60:
            print(f"Time to expiry: {timeToExpiration:.2f} seconds. Relaunching site!")
            await relaunchFs1Site(driverManager, runningTasks)
            break

        await asyncio.sleep(5)

async def relaunchFs1Site(driverManager, runningTasks):
    driverManager.replaceDriver()

    await cancelRunningTasks(runningTasks)

    newTasks = await startFs1SiteAndListeners(driverManager, hasAlreadyInit=True)
    runningTasks.clear()
    runningTasks.extend(newTasks)

async def asyncMain():
    driverManager = DriverManager()
    driverManager.setupDriver()
    runningTasks = await startFs1SiteAndListeners(driverManager, hasAlreadyInit=False)

    try:
        await asyncio.sleep(7560)  # 2.1 hours
    except asyncio.CancelledError:
        pass

    print("COMPLETED", flush=True)

    await cancelRunningTasks(runningTasks)
    driverManager.quitDriver()

async def cancelRunningTasks(runningTasks):
    for task in runningTasks:
        task.cancel()

def main():
    asyncio.run(asyncMain())

if __name__ == "__main__":
    main()
    