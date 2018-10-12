# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re, datetime, subprocess


def main():
    driver_path = './chromedriver' # mac
    url = 'http://m.studioclassroom.com/tv-programs.php?level=sc'
    page = urlopen(url)

    bs = BeautifulSoup(page, "html.parser")

    iframe_src = bs.findAll('iframe', attrs={'src': re.compile('^(https://tv.line.me/embed/)')})[0]['src']

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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-center-play-icon]')))
    except TimeoutException:
        print('timeout ....(stage 1)')
    # move mouse pointer and click
    action = ActionChains(driver)
    el = driver.find_element(By.CSS_SELECTOR, 'button[data-center-play-icon]')
    action.move_to_element(el)
    action.pause(1)
    action.click()
    action.pause(1)
    action.perform()

    try:
        # waitfor data-src
        video = WebDriverWait(driver, 60*5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "video[id^='rmcPlayer'][data-src^='http']")))
        m3u8_src = video.get_attribute("data-src")
        print('playlist''s list: {}'.format(m3u8_src))
    except TimeoutException:
        print('timeout ....(stage 2)')
    
    # close browser
    driver.quit()
    
    query_str = m3u8_src.split('?')[1:][0]
    new_m3u8_url = m3u8_src[:m3u8_src.replace('?'+query_str, '').rfind('/')]+"/{}?"+query_str
    playlist_list = urlopen(m3u8_src)

    print('query string: {}'.format(query_str))
    
    # choice playlist by resolution
    resolution = '256x144'
    print('choice resolution: {}'.format(resolution))

    line = [l.decode('utf-8').strip() for l in playlist_list]
    resolution_key = [l for l in line if resolution in l][0]
    index = [l for l in line].index(resolution_key) + 1
    
    # get playlist
    playlist_url = new_m3u8_url.format(line[index])

    print('playlist: {}'.format(m3u8_src))

    playlist_txt = urlopen(playlist_url)

    # get .ts file url
    m3u8_file_name = playlist_url.split('?')[0].split('/')[-1]
    ts_url = playlist_url.replace('/' + m3u8_file_name, '').replace('?' + query_str, '')
    
    # modify relative url to absolute url in playlist
    with open('temp.m3u8', 'w') as file:
        for line in playlist_txt:
            txt = line.decode('utf-8').strip()
            if not txt.startswith('#'):
                txt = ts_url + '/' + txt
            file.write(txt.replace('.ts', '.ts?' + query_str) + '\r\n')
    # download and convert to mp4 by using ffmpeg
    ffmpeg_command = 'ffmpeg -protocol_whitelist "file,http,https,tcp,tls" -y -i {} -c copy -bsf:a aac_adtstoasc {}.mp4'.format('temp.m3u8', datetime.datetime.today().strftime('%Y-%m-%d'))
    process = subprocess.Popen(ffmpeg_command, shell=True)
    process.wait()


if __name__== "__main__":
    main()
