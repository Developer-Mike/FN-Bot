import os
import constants

def post(image, caption):
    print(f"Posting. ({image}, {caption})")
    if constants.TWITTER_ENABLED:
        print("Posting to Twitter.")

        if constants.USE_TWITTER_API:
            _post_twitter_api(image, caption)
        else:
            _post_twitter(image, caption)

def _post_twitter_api(image, caption):
    if image != None:
        media = constants.TWITTER_API.media_upload(image)

    constants.TWITTER_API.update_status(caption, media_ids=[media.media_id] if image != None else [])


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

if constants.VIRTUAL_DISPLAY: from pyvirtualdisplay import Display
else: from contextlib import nullcontext

def _post_twitter(image, caption):
    with Display(visible=False, size=(800, 600)) if constants.VIRTUAL_DISPLAY else nullcontext() as _:
        options = webdriver.ChromeOptions()

        driver = webdriver.Chrome(constants.CHROMEDRIVER_PATH, options=options)
        driver.get("https://twitter.com/i/flow/login")
        driver.maximize_window()

        email_field = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]')))
        email_field.send_keys(constants.TWITTER_EMAIL)
        email_field.send_keys(Keys.ENTER)

        # Security username question
        try:
            security_username_field = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"][@autocapitalize="none"]')))
            security_username_field.send_keys(constants.TWITTER_USERNAME)
            security_username_field.send_keys(Keys.ENTER)
        except:
            pass

        password_field = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))
        password_field.send_keys(constants.TWITTER_PASSWORD)
        password_field.send_keys(Keys.ENTER)

        # Logged in

        if image != None:
            post_image_button = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
            post_image_button.send_keys(image)

        post_caption_textarea = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"][@contenteditable="true"]')))
        post_caption_textarea.send_keys(caption.replace("\\n", Keys.ENTER))
        driver.implicitly_wait(5)
        post_caption_textarea.send_keys(Keys.CONTROL, Keys.ENTER)

        driver.implicitly_wait(10)
        driver.quit()
