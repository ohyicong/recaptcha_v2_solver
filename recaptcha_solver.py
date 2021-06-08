# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 10:01:10 2020

@author: OHyic
"""

# system libraries
import os
import random
import time
import urllib

# recaptcha libraries
import pydub
import speech_recognition as sr
# selenium libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# custom patch libraries
import patch


def delay():
    driver.implicitly_wait(5)


if __name__ == "__main__":
    # download latest chromedriver, please ensure that your chrome is up to date
    while True:
        try:
            # create chrome driver
            driver = webdriver.Chrome(os.path.normpath(os.getcwd() + "\\webdriver\\chromedriver.exe"))
            delay()
            # go to website
            driver.get("https://www.google.com/recaptcha/api2/demo")
            break
        except Exception:
            # patch chromedriver if not available or outdated
            try:
                driver
            except NameError:
                is_patched = patch.download_latest_chromedriver()
            else:
                is_patched = patch.download_latest_chromedriver(driver.capabilities['version'])
            if not is_patched:
                print("[-] Please update the chromedriver.exe in the webdriver folder according to your chrome version:"
                      "https://chromedriver.chromium.org/downloads")
                break

    # main program
    # switch to recaptcha frame
    frames = driver.find_elements_by_tag_name("iframe")
    driver.switch_to.frame(frames[0])
    delay()

    # click on checkbox to activate recaptcha
    driver.find_element_by_class_name("recaptcha-checkbox-border").click()

    # switch to recaptcha audio control frame
    driver.switch_to.default_content()
    frames = driver.find_element_by_xpath("/html/body/div[2]/div[4]").find_elements_by_tag_name("iframe")
    driver.switch_to.frame(frames[0])
    delay()

    # click on audio challenge
    driver.find_element_by_id("recaptcha-audio-button").click()

    # switch to recaptcha audio challenge frame
    driver.switch_to.default_content()
    frames = driver.find_elements_by_tag_name("iframe")
    driver.switch_to.frame(frames[-1])
    delay()

    # get the mp3 audio file
    src = driver.find_element_by_id("audio-source").get_attribute("src")
    print("[INFO] Audio src: %s" % src)

    # download the mp3 audio file from the source
    urllib.request.urlretrieve(src, os.path.normpath(os.getcwd() + "\\sample.mp3"))
    delay()

    # load downloaded mp3 audio file as .wav
    try:
        sound = pydub.AudioSegment.from_mp3(os.path.normpath(os.getcwd() + "\\sample.mp3"))
        sound.export(os.path.normpath(os.getcwd() + "\\sample.wav"), format="wav")
        sample_audio = sr.AudioFile(os.path.normpath(os.getcwd() + "\\sample.wav"))
    except Exception:
        print("[-] Please run program as administrator or download ffmpeg manually, "
              "http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/")

    # translate audio to text with google voice recognition
    r = sr.Recognizer()
    with sample_audio as source:
        audio = r.record(source)
    key = r.recognize_google(audio)
    print("[INFO] Recaptcha Passcode: %s" % key)

    # key in results and submit
    driver.find_element_by_id("audio-response").send_keys(key.lower())
    driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)
    driver.switch_to.default_content()
    delay()
    driver.find_element_by_id("recaptcha-demo-submit").click()
    delay()
