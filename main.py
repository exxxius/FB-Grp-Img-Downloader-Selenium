# import os
# import time
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
#
#
# # Function to clean image name
# def clean_image_name(image_name):
#     return image_name.split('?')[0]
#
#
# # Create the images directory if it does not exist
# if not os.path.exists("images"):
#     os.makedirs("images")
#
# # Launch the web browser
# driver = webdriver.Chrome()
# driver.get("https://www.facebook.com/")
#
# # Log in to your Facebook account
# email = driver.find_element(By.NAME, "email")
# email.send_keys("YOUR FACEBOOK USERNAME") //FB username/email
# password = driver.find_element(By.NAME, "pass")
# password.send_keys("YOUR FACEBOOK PASSWORD") //FB password
# password.send_keys(Keys.RETURN)
#
# # Read the links from a text file
# with open("links.txt", "r") as f:
#     links = f.readlines()
#
# # Visit each photo page and download the photo
# for link in links:
#     # Navigate to the photo page
#     driver.get(link.strip())
#
#     # Wait for the page to load
#     try:
#         wait = WebDriverWait(driver, 5)  # Increase the timeout from 10 to 20 seconds
#         #wait.until(EC.title_contains("Photos"))
#     except TimeoutException:
#         print(f"Timed out waiting for page to load: {link.strip()}")
#         continue  # Skip the current link and continue with the next one
#
#     # # Save the photo
#     # try:
#     #     # Changed the XPath to a more general one
#     #     photo = wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@src, 'scontent')]")))
#     #     image_url = photo.get_attribute('src')
#     #
#     #     # Download and save the image
#     #     response = requests.get(image_url)
#     #     image_name = clean_image_name(image_url.split('/')[-1])
#     #     with open(f"images/{image_name}", 'wb') as img_file:
#     #         img_file.write(response.content)
#     #
#     #     # Wait for the download to complete
#     #     time.sleep(1)
#     # except NoSuchElementException:
#     #     print(f"Unable to find element on page: {link.strip()}")
#     # except TimeoutException:
#     #     print(f"Timed out waiting for image element on page: {link.strip()}")
#     # Save the photo
#     try:
#         # photo = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="mount_0_0_Rt"]/div/div[1]/div/div[5]/div/div/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div[1]/div/div[2]/div/div/div/img')))
#         photo = wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@src, 'scontent')]")))
#
#         image_url = photo.get_attribute('src')
#         print(f"Image URL: {image_url}")  # Print the image URL
#
#         # Download and save the image
#         response = requests.get(image_url)
#         print(f"Request status code: {response.status_code}")  # Print the request status code
#         if response.status_code == 200:
#             image_name = clean_image_name(image_url.split('/')[-1])
#             with open(f"images/{image_name}", 'wb') as img_file:
#                 img_file.write(response.content)
#             print(f"Image saved: images/{image_name}")  # Print the saved image path
#         else:
#             print(f"Failed to download image: {image_url}")
#
#         # Wait for the download to complete
#         time.sleep(1)
#     except NoSuchElementException:
#         print(f"Unable to find element on page: {link.strip()}")
#     except TimeoutException:
#         print(f"Timed out waiting for image element on page: {link.strip()}")
#
# # Close the web browser
# driver.quit()


import time
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading
from queue import Queue

# Log in to Facebook using FB username and password and get the cookies.
def login():
    driver = webdriver.Chrome()
    driver.get("https://www.facebook.com/")
    email = driver.find_element(By.NAME, "email")
    email.send_keys("YOUR FACEBOOK USERNAME") # FB username/email
    password = driver.find_element(By.NAME, "pass")
    password.send_keys("YOUR FACEBOOK PASSWORD")  # FB password
    password.send_keys(Keys.RETURN)
    time.sleep(5)
    cookies = driver.get_cookies()
    driver.quit()
    return cookies


# Apply the cookies to the driver
def apply_cookies(driver, cookies):
    for cookie in cookies:
        driver.add_cookie(cookie)


# Create a driver instance and apply the cookies to it.
def create_driver_instance(cookies):
    driver = webdriver.Chrome()
    driver.get("https://www.facebook.com/")
    apply_cookies(driver, cookies)
    driver.refresh()
    return driver


# Download the images from the links, using the cookies and the driver.
def download_images(cookies, driver, queue):
    while not queue.empty():
        link = queue.get()
        driver.get(link.strip())

        try:
            wait = WebDriverWait(driver, 10)
            photo = wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@src, 'scontent')]")))
            image_url = photo.get_attribute('src')

            response = requests.get(image_url)
            image_name = image_url.split('/')[-1].split('?')[0]
            with open(f"images/{image_name}", 'wb') as img_file:
                img_file.write(response.content)

            time.sleep(1)
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error: {e}")

    driver.quit()


# Create a queue of links
def create_queue():
    queue = Queue()
    with open("links.txt", "r") as f:
        for link in f.readlines():
            queue.put(link.strip())
    return queue


num_instances = 6 # Number of instances to run in parallel
cookies = login()
queue = create_queue()
drivers = [create_driver_instance(cookies) for _ in range(num_instances)]

# Create and start threads
threads = []
for i in range(num_instances):
    t = threading.Thread(target=download_images, args=(cookies, drivers[i], queue))
    t.start()
    threads.append(t)

# Wait for all threads to finish
for t in threads:
    t.join()
