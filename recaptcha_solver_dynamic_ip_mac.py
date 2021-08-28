# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 10:01:10 2020

@author: OHyic
"""

# system libraries
import os
import random
import socket
import subprocess
import sys
import time
import urllib

# recaptcha libraries
import netifaces
import pydub
import speech_recognition as sr
# selenium libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# Networking Libraries
from spoofmac.util import random_mac_address

# custom patch libraries
from recaptcha_v2_solver.patch import webdriver_folder_name


def delay(waiting_time=5):
    driver.implicitly_wait(waiting_time)


def change_ip(interface_name, ip_address, mask, gateway):
    ip_address = '.'.join(ip_address.split('.')[:-1]) + '.' + str(
        random.randrange(8, 255 - int(mask.split('.')[-1]) - 1))
    result_1 = subprocess.call(
        f'netsh interface ipv4 set address name="{interface_name}" static {ip_address} {mask} {gateway}', shell=True)
    result_2 = subprocess.call(f'netsh interface ipv4 set dns name="{interface_name}" static 8.8.8.8', shell=True)
    if result_1 == 1 or result_2 == 1:
        print("[WARN] Unable to change IP. Run the program with admin rights.")
        sys.exit()
    print(f"[INFO] New IP Address is: {ip_address}")
    return True


def get_default_network_details():
    def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address

    ip_address = get_ip_address()
    for i in netifaces.interfaces():
        try:
            if str(netifaces.ifaddresses(i)[netifaces.AF_INET][0]['addr']) == str(ip_address):
                print("[INFO] *Default Network Details*")
                print("[INFO] IP Address: ", ip_address)
                print("[INFO] Mask: ", netifaces.ifaddresses(i)[netifaces.AF_INET][0]['netmask'])
                print("[INFO] Gateway: ", netifaces.gateways()['default'][netifaces.AF_INET][0])
                return ip_address, \
                       netifaces.ifaddresses(i)[netifaces.AF_INET][0]['netmask'], \
                       netifaces.gateways()['default'][netifaces.AF_INET][0]
        except Exception:
            pass


# SETTINGS
# Please check your network details
interface_name = 'Wi-Fi'
ip_address, mask, gateway = get_default_network_details()
count_loops = 0
count_failures = 0

# endless loop
while True:
    try:
        print("[INFO] *Changing MAC & IP*")
        print("[INFO] New Mac is:", random_mac_address(interface_name))
        change_ip(interface_name, ip_address, mask, gateway)
        print("[INFO] Start Browser")
        path_to_chromedriver = os.path.normpath(os.path.join(os.getcwd(), webdriver_folder_name, 'chromedriver'))
        driver = webdriver.Chrome(path_to_chromedriver)
        delay()
        for i in range(10):
            count_loops += 1
            # go to website
            driver.get("https://www.google.com/recaptcha/api2/demo")
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            # switch to recaptcha frame
            frames = driver.find_elements_by_tag_name("iframe")
            driver.switch_to.frame(frames[0])

            # click on checkbox to activate recaptcha
            driver.find_element_by_class_name("recaptcha-checkbox-border").click()

            # switch to recaptcha audio control frame
            driver.switch_to.default_content()
            frames = driver.find_element_by_xpath("/html/body/div[2]/div[4]").find_elements_by_tag_name("iframe")
            driver.switch_to.frame(frames[0])

            # click on audio challenge
            driver.find_element_by_id("recaptcha-audio-button").click()

            # switch to recaptcha audio challenge frame
            driver.switch_to.default_content()
            frames = driver.find_elements_by_tag_name("iframe")
            driver.switch_to.frame(frames[-1])
            # get the mp3 audio file
            src = driver.find_element_by_id("audio-source").get_attribute("src")
            print(f"[INFO] Audio src: {src}")

            path_to_mp3 = os.path.normpath(os.path.join(os.getcwd(), "sample.mp3"))
            path_to_wav = os.path.normpath(os.path.join(os.getcwd(), "sample.wav"))

            # download the mp3 audio file from the source
            urllib.request.urlretrieve(src, path_to_mp3)

            # load downloaded mp3 audio file as .wav
            sound = pydub.AudioSegment.from_mp3(path_to_mp3)
            sound.export(path_to_wav, format="wav")
            sample_audio = sr.AudioFile(path_to_wav)

            # translate audio to text with google voice recognition
            r = sr.Recognizer()
            with sample_audio as source:
                audio = r.record(source)
            key = r.recognize_google(audio)
            print(f"[INFO] Recaptcha Passcode: {key}")

            # key in results and submit
            for letter in key.lower().split():
                driver.find_element_by_id("audio-response").send_keys(letter)
            driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)
            print("[INFO] Validation Successful")
            driver.switch_to.default_content()
            driver.find_element_by_id("recaptcha-demo-submit").click()
            print(f"[INFO] Loop Completed: {i + 1}. Total Loops: {count_loops}, Total Failures: {count_failures}")
            print("[INFO] Waiting for 10 seconds.. before trying again")
            time.sleep(10)
        driver.quit()
    except Exception:
        count_failures += 1
        print(f"[WARN] Something went wrong. Total Loops: {count_loops}, Total Failures: {count_failures}")
        print("[INFO] Reopening Driver")
        driver.quit()
