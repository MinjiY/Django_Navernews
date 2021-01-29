import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
import time

def extract_date(mystr):
    mystr = mystr.replace('<span class="bar"></span>','')
    return mystr


def parsing(sid1, sid2):
    url = 'https://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&sid1='+str(sid1)+'&sid2='+str(sid2)
    req_header={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
    }
    res = requests.get(url, headers=req_header)
    if res.ok:
        # Response 객체에서 텍스트 추출
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        #print(soup)

        #title = soup.select('div#main_content div.list_body.newsflash_body ul.type06_headline li dt:nth-child(2) a[href]')
        title = soup.select('div#main_content div.list_body.newsflash_body ul.type06_headline li')
        link = soup.select('div#main_content div.list_body.newsflash_body ul.type06_headline li dt:nth-child(2) a[href]')
        desc = soup.select('div#main_content div.list_body.newsflash_body ul.type06_headline li dl dd span.lede')
        writer = soup.select('div#main_content div.list_body.newsflash_body ul.type06_headline li dl dd span.writing')
    
        titles = []
        links = []
        dates = []
        descs=[]
        writers=[]
        for data in zip(title,link, desc, writer):
            titles.append(data[0].find_all('dt', class_= not "photo")[0].text.strip())
            links.append(data[1]['href'])
            descs.append(data[2].text)
            writers.append(data[3].text)
            
            res2 = requests.get(data[1]['href'],headers=req_header )
            if res2.ok:
                published_date = BeautifulSoup(res2.text, 'html.parser').select('div#main_content div.article_header div.article_info div.sponsor span.t11')
                if len(published_date)>0:
                    dates.append(published_date[0].text)    
        content = zip(titles,links,dates,descs,writers)            
    return content


def selenium_parsing(sports):
    URL = "https://sports.news.naver.com/"+sports+"/news/index.nhn?isphoto=N"
    
    chrome_options=webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('lang=ko_KR')
    path = "C:\\cloud\\selenium\\webdriver\\chromedriver.exe"
    driver = webdriver.Chrome(path, chrome_options= chrome_options)

    driver.get(URL)
    time.sleep(3)

    title = driver.find_elements_by_css_selector('#_newsList > ul > li > div > a > span')
    link = driver.find_elements_by_css_selector('#_newsList > ul > li > div > a')
    date = driver.find_elements_by_css_selector('#_newsList > ul > li > div > div > span.time')
    preview = driver.find_elements_by_css_selector('#_newsList > ul > li > div > p')
    writer = driver.find_elements_by_css_selector('#_newsList > ul > li > div > div > span.press')
    
    titles = []
    links = []
    dates =[]
    previews = []
    writers = []
    for element in zip(title,link,date,preview,writer):
        titles.append(element[0].get_attribute('innerHTML'))
        links.append(element[1].get_attribute('href'))
        dates.append(extract_date(element[2].get_attribute('innerHTML')))
        previews.append(element[3].get_attribute('innerHTML'))
        writers.append(element[4].get_attribute('innerHTML'))
    contents = zip(titles,links,dates,previews,writers)
    return contents