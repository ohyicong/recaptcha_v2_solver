# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 10:01:10 2020

@author: OHyic
"""

#system libraries
import subprocess
import random
import os
import random
import time
import sys
#selenium libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException   
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.chrome.options import Options


#recaptcha libraries
import speech_recognition as sr
import ffmpy
import requests
import urllib
import pydub

#Networking Libraries
from spoofmac.util import random_mac_address, MAC_ADDRESS_R, normalize_mac_address
from spoofmac.interface import (
    wireless_port_names,
    find_interfaces,
    find_interface,
    set_interface_mac,
    get_os_spoofer
)
import socket
import netifaces

def delay (low=3,high=5):
    time.sleep(random.randint(low,high))

def change_ip(interface_name,ip_address,mask,gateway):
    ip_address='.'.join(ip_address.split('.')[:-1])+'.'+ str(random.randrange(8,255-int(mask.split('.')[-1])-1))
    result_1=subprocess.call('netsh interface ipv4 set address name="%s" static %s %s %s'%(interface_name,ip_address,mask,gateway), shell=True)
    result_2=subprocess.call('netsh interface ipv4 set dns name="%s" static 8.8.8.8'%(interface_name), shell=True)
    if(result_1==1 or result_2==1):
        print("[WARN] Unable to change IP. Run the program with admin rights.")
        sys.exit()
        return False
    print("[INFO] New IP Address is: %s"%(ip_address))
    return True

def get_default_network_details():
    def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address=s.getsockname()[0]
        s.close()
        return ip_address
    ip_address = get_ip_address()
    for i in netifaces.interfaces():
        try:
            if(str(netifaces.ifaddresses(i)[netifaces.AF_INET][0]['addr'])==str(ip_address)):
                print("[INFO] *Default Network Details*")
                print("[INFO] IP Address: ", ip_address)
                print("[INFO] Mask: ", netifaces.ifaddresses(i)[netifaces.AF_INET][0]['netmask'])
                print("[INFO] Gateway: ", netifaces.gateways()['default'][netifaces.AF_INET][0])
                delay(5,5)
                return ip_address,netifaces.ifaddresses(i)[netifaces.AF_INET][0]['netmask'],netifaces.gateways()['default'][netifaces.AF_INET][0]
        except:pass

#SETTINGS
#Please check your network details 
interface_name = 'Wi-Fi'
ip_address,mask,gateway = get_default_network_details()
count_loops=0
count_failures=0

#endless loop
while(True):
    print("[INFO] *Changing MAC & IP*")
    print("[INFO] New Mac is: "+random_mac_address(interface_name))
    delay(3,5)
    change_ip(interface_name,ip_address,mask,gateway)
    delay(3,5)
    print("[INFO] Start Browser")
    driver = webdriver.Chrome(os.getcwd()+"\\webdriver\\chromedriver.exe") 
    for i in range(20):
        try:
            count_loops+=1
            #go to website
            driver.get("https://www.google.com/recaptcha/api2/demo")
            element=WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            #switch to recaptcha frame
            frames=driver.find_elements_by_tag_name("iframe")
            driver.switch_to.frame(frames[0]);
            delay()
            
            #click on checkbox to activate recaptcha
            driver.find_element_by_class_name("recaptcha-checkbox-border").click()
            
            #switch to recaptcha audio control frame
            driver.switch_to.default_content()
            frames=driver.find_element_by_xpath("/html/body/div[2]/div[4]").find_elements_by_tag_name("iframe")
            driver.switch_to.frame(frames[0])
            delay()
            
            #click on audio challenge
            driver.find_element_by_id("recaptcha-audio-button").click()
            
            #switch to recaptcha audio challenge frame
            driver.switch_to.default_content()
            frames= driver.find_elements_by_tag_name("iframe")
            driver.switch_to.frame(frames[-1])
            delay()
        except:
            count_failures+=1
            print("[WARN] Something went wrong. Total Loops: %d, Total Failures %d"%(count_loops,count_failures))
            print("[INFO] Reopening Driver")
            driver.close()
            driver.quit()
            break
        #click on the play button
        is_validation_successful = False
        while(not is_validation_successful):
            try:
                driver.find_element_by_xpath("/html/body/div/div/div[3]/div/button").click()
                
                #get the mp3 audio file
                src = driver.find_element_by_id("audio-source").get_attribute("src")
                print("[INFO] Audio src: %s"%src)
                #download the mp3 audio file from the source
                urllib.request.urlretrieve(src, os.getcwd()+"\\sample.mp3")
                sound = pydub.AudioSegment.from_mp3(os.getcwd()+"\\sample.mp3")
                sound.export(os.getcwd()+"\\sample.wav", format="wav")
                sample_audio = sr.AudioFile(os.getcwd()+"\\sample.wav")
                r= sr.Recognizer()
                
                with sample_audio as source:
                    audio = r.record(source)
                
                #translate audio to text with google voice recognition
                key=r.recognize_google(audio)
                print("[INFO] Recaptcha Passcode: %s"%key)
                
                #key in results and submit
        
                driver.find_element_by_id("audio-response").send_keys(key.lower())
                delay()
                driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)
                delay()
                #check for failure message
                print(driver.find_element_by_class_name("rc-audiochallenge-error-message").text)
            except:
                is_validation_successful=True
                print("[INFO] Validation Successful")
                break
        
        try:
            driver.switch_to.default_content()
            delay()
            driver.find_element_by_id("recaptcha-demo-submit").click()
            delay()
            print("[INFO] Loop Completed. Total Loops: %d, Total Failures %d"%(count_loops,count_failures))
        except:
            print("[INFO] Network is fine. GUI Error. Restarting. Count voided.")
            count_loops-=1
            break
        
       