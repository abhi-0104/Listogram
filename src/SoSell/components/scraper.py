# %%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from SoSell import logger
import time
import os

def initialize_driver():
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument("--headless")

    service = Service('/Users/Stark0104/Desktop/Coding/chromedriver-mac-arm64/chromedriver')

    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver





def login_to_instagram(driver, url):
    driver.get(url)
    try:
        # Wait for the password field to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )

        logger.info("Password field detected.")

    except Exception as e:
        logger.info(f"Error during login: {e}")

        


def scrape_instagram_post(driver, url):
    try:
        driver.get(url)

        # Close initial pop-up 
        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and @tabindex="0"]'))
            )

            logger.info("Close button detected, attempting to click.")

            driver.execute_script("arguments[0].click();", close_button)

            logger.info("Close button clicked.")

        except Exception as e:
            logger.warning(f"No close button found or clickable: {e}")

       
        try:
            close_secondary = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@aria-label="Close"]'))
            )

            driver.execute_script("arguments[0].scrollIntoView(true);", close_secondary)

            driver.execute_script("arguments[0].click();", close_secondary)

            logger.info("Secondary close button clicked.")

        except Exception as e:
            logger.warning(f"No secondary close button found: {e}")


        logger.info("Waiting for post content to load...")


        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@dir='auto' and contains(text(), 'Follow')]"))
        )
        logger.info("Post loaded, ready to scrape.")

        post_data = {}


        logger.info("Looking for image elements...")

        try:
            image_containers = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, '_aagv')]//img[@crossorigin='anonymous']"))
            )

            post_data['image_urls'] = [img.get_attribute('src') for img in image_containers]

            logger.info(f"Image elements found: {len(post_data['image_urls'])}")

        except Exception as e:
            logger.error(f"Error finding image elements: {e}")
            post_data['image_urls'] = []



        # Look for the caption
        logger.info("Looking for caption...")
        caption_elements = driver.find_elements(By.XPATH, '//div[@class="_a9zr"]')

        if caption_elements:
            post_data['caption'] = caption_elements[0].text
            logger.info("Caption found.")
        else:
            logger.warning("Caption element not found.")
            post_data['caption'] = "No caption found."

        logger.info("Scraped data successfully.")
        return post_data

    except Exception as e:
        logger.error(f"Error scraping post: {e}")
        logger.error(f"Post URL: {url}")
        return None