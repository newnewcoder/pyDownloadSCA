# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
import re, datetime, subprocess
import time

def main():
    driver_path = './chromedriver' # get from https://chromedriver.storage.googleapis.com/index.html?path=2.42/
    url = 'http://m.studioclassroom.com/tv-programs.php?level=sc'
    page = urlopen(url)

    bs = BeautifulSoup(page, "html.parser")

    iframe_src = bs.findAll('iframe', attrs={'src': re.compile('^(https://www.linetv.tw/player/)')})[0]['src']

    # open website by selenium with chrome
    option = webdriver.ChromeOptions()
    option.add_argument("--mute-audio")
    option.add_argument('headless')
    driver = webdriver.Chrome(driver_path, chrome_options=option)
    # driver = webdriver.Chrome(driver_path)

    driver.get(iframe_src)

    print('open browser: {}'.format(iframe_src))
    # print(driver.title)
    
    try:
        print('wait for advertisement countdown')
        # wait for not allowed skip ad countdown
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="player_ima-countdown-div"]')))
        el = driver.find_element(By.CSS_SELECTOR, 'div[id="player_ima-countdown-div"]')
        if 'Advertisement' in el.text:
            mi = el.text.split(' ')[-1].split(':')[0]
            s = el.text.split(' ')[-1].split(':')[1]
            waitfor = int(mi) * 60 + int(s)
            print('wait {}s...'.format(waitfor))
            time.sleep(waitfor)
    except TimeoutException:
        print('can not find advertisement countdown element')

    try:
        print('wait for video tag')
        # wait for mp4 src
        video = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "video[id='player_html5_api']")))
        mp4_src = video.get_attribute("src")
        print('get mp4 url: {}'.format(mp4_src))
    except TimeoutException:
        print('can not find video tag')
    
    # close browser
    driver.quit()
    if mp4_src:
        urlretrieve(mp4_src, datetime.datetime.today().strftime('%Y-%m-%d') + '.mp4')
        print('download completed')
    else:
        print('download failed')

if __name__== "__main__":
    main()
