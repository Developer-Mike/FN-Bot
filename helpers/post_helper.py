import os
import constants

def post_image(image, caption):
    print(f"Posting image. ({image}, {caption})")
    if constants.TWITTER_ENABLED:
        print("Posting to Twitter.")

        if constants.USE_TWITTER_API:
            _post_twitter_api(image, caption)
        else:
            _post_twitter(image, caption)

def _post_twitter_api(image, caption):
    media = constants.TWITTER_API.media_upload(image)
    constants.TWITTER_API.update_status(caption, media_ids=[media.media_id])


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def _post_twitter(image, caption):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(os.path.join(constants.BASE_PATH, "chromedriver.exe"), options=options)
    driver.get("https://twitter.com/i/flow/login")
    driver.maximize_window()

    email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input')))
    email_field.send_keys(constants.TWITTER_EMAIL)
    email_field.send_keys(Keys.ENTER)

    # Security username question
    try:
        security_username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')))
        security_username_field.send_keys(constants.TWITTER_USERNAME)
        security_username_field.send_keys(Keys.ENTER)
    except:
        pass

    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')))
    password_field.send_keys(constants.TWITTER_PASSWORD)
    password_field.send_keys(Keys.ENTER)

    # Logged in

    post_image_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[3]/div/div/div[1]/input')))
    post_image_button.send_keys(image)

    post_caption_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div/div/div/div')))
    post_caption_button.send_keys(caption.replace("\\n", Keys.ENTER))

    post_caption_button.send_keys(Keys.CONTROL, Keys.ENTER)
    driver.implicitly_wait(10)

    driver.quit()
