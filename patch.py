# -*- coding: utf-8 -*-
"""
Created on Sun May 23 14:44:43 2021

@author: Yicong
"""
# !/usr/bin/env python3
import os
import re
import stat
import sys
import urllib.request
import zipfile
from sys import platform

webdriver_folder_name = 'webdriver'


def get_platform_filename():
    filename = ''
    is_64bits = sys.maxsize > 2 ** 32

    if platform == 'linux' or platform == 'linux2':
        # Linux
        filename += 'linux'
        filename += '64' if is_64bits else '32'
    elif platform == 'darwin':
        # OS X
        filename += 'mac64'
    elif platform == 'win32':
        # Windows
        filename += 'win32'

    filename += '.zip'

    return filename


def download_latest_chromedriver(current_chrome_version=''):
    # Find the latest chromedriver, download, unzip, set permissions to executable.

    try:
        url = 'https://chromedriver.chromium.org/downloads'
        base_driver_url = 'https://chromedriver.storage.googleapis.com'
        file_name = 'chromedriver_' + get_platform_filename()
        pattern = r'https://.*?path=(\d+\.\d+\.\d+\.\d+)'

        # Download latest chromedriver.
        stream = urllib.request.urlopen(url)
        content = stream.read().decode('utf8')

        # Parse the latest version.
        all_match = re.findall(pattern, content)

        if all_match:
            # Version of latest driver.
            if current_chrome_version != '':
                print('[+] updating chromedriver')
                all_match = list(set(re.findall(pattern, content)))
                current_chrome_version = '.'.join(current_chrome_version.split('.')[:-1])
                version_match = [i for i in all_match if re.search('^%s' % current_chrome_version, i)]
                version = version_match[0]
            else:
                print('[+] installing new chromedriver')
                version = all_match[1]
            driver_url = '/'.join((base_driver_url, version, file_name))

            # Download the file.
            print(f'[+] downloading chromedriver ver: {version}: {driver_url}')
            app_path = os.path.dirname(os.path.realpath(__file__))
            chromedriver_path = os.path.normpath(os.path.join(app_path, webdriver_folder_name, 'chromedriver.exe'))
            file_path = os.path.normpath(os.path.join(app_path, webdriver_folder_name, file_name))
            urllib.request.urlretrieve(driver_url, file_path)

            # Unzip the file into folder
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.normpath(os.path.join(app_path, webdriver_folder_name)))

            st = os.stat(chromedriver_path)
            os.chmod(chromedriver_path, st.st_mode | stat.S_IEXEC)
            print('[+] latest chromedriver downloaded.')
            # Cleanup.
            os.remove(file_path)
            return True
    except Exception:
        print('[-] unable to download latest chromedriver. the system will use the local version instead.')
        return False
