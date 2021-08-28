# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 10:01:10 2020

@author: OHyic
"""

# system libraries
import os
import sys
import urllib

# recaptcha libraries
import pydub
import speech_recognition as sr
# selenium libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# custom patch libraries
from patch import download_latest_chromedriver, webdriver_folder_name


def delay(waiting_time=5):
    driver.implicitly_wait(waiting_time)


if __name__ == "__main__":
    # download latest chromedriver, please ensure that your chrome is up to date
    while True:
        try:
            # create chrome driver
            path_to_chromedriver = os.path.normpath(
                os.path.join(os.getcwd(), webdriver_folder_name, 'chromedriver.exe'))
            driver = webdriver.Chrome(path_to_chromedriver)
            delay()
            # go to website
            driver.get("https://www.google.com/recaptcha/api2/demo")
            break
        except Exception:
            # patch chromedriver if not available or outdated
            try:
                driver
            except NameError:
                is_patched = download_latest_chromedriver()
            else:
                is_patched = download_latest_chromedriver(driver.capabilities['version'])
            if not is_patched:
                sys.exit(
                    "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:"
                    "https://chromedriver.chromium.org/downloads")

    # main program
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
    try:
        sound = pydub.AudioSegment.from_mp3(path_to_mp3)
        sound.export(path_to_wav, format="wav")
        sample_audio = sr.AudioFile(path_to_wav)
    except Exception:
        sys.exit("[ERR] Please run program as administrator or download ffmpeg manually, "
                 "https://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/")

    # translate audio to text with google voice recognition
    r = sr.Recognizer()
    with sample_audio as source:
        audio = r.record(source)
    key = r.recognize_google(audio)
    print(f"[INFO] Recaptcha Passcode: {key}")

    # key in results and submit
    driver.find_element_by_id("audio-response").send_keys(key.lower())
    driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)
    driver.switch_to.default_content()
    driver.find_element_by_id("recaptcha-demo-submit").click()
