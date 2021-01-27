from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import HttpResponse
from news.models import Letter 
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from django.utils import timezone

from selenium import webdriver
import time

# Create your views here.

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
                # 게시일 + 최종 수정일
                # 최종 수정일 버림
                if len(published_date)>0:
                    dates.append(published_date[0].text)    
        content = zip(titles,links,dates,descs,writers)            
    return content


def selenium_parsing():
    URL = 'https://sports.news.naver.com/'
    chrome_options=webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('lang=ko_KR')
    path = "C:\\cloud\\selenium\\webdriver\\chromedriver.exe"
    driver = webdriver.Chrome(path, chrome_options= chrome_options)

    driver.get("https://sports.news.naver.com/kbaseball/news/index.nhn?isphoto=N")
    time.sleep(3)

    title = driver.find_elements_by_css_selector('#_newsList > ul > li > div > a > span')
    link = driver.find_elements_by_css_selector('#_newsList > ul > li:nth-child(1) > div > a')
    date = driver.find_elements_by_css_selector('#_newsList > ul > li > div > div > span.time')
    preview = driver.find_elements_by_css_selector('#_newsList > ul > li > div > p')
    writer = driver.find_elements_by_css_selector('#_newsList > ul > li > div > div > span.press')
    
    # category topic title letter_link published_date preview writer

    titles = []
    links = []
    dates =[]
    previews = []
    writers = []
    for element in zip(title,link,date,preview,writer):
        #print(element[0].get_attribute('innerHTML'))
        titles.append(element[0].get_attribute('innerHTML'))
        #print(element[1].get_attribute('href'))
        links.append(element[1].get_attribute('href'))
        #print(element[2].get_attribute('innerHTML'))
        dates.append(element[2].get_attribute('innerHTML'))
        #print(element[3].get_attribute('innerHTML'))
        previews.append(element[3].get_attribute('innerHTML'))
        #print(element[4].get_attribute('innerHTML'))
        writers.append(element[4].get_attribute('innerHTML'))
    contents = zip(titles,links,dates,previews,writers)
    return contents



def news_list(request):
    # DB에서 한 토픽당 글 레터 두개씩 가져와서 뿌림

    return render(request, 'news/news_list.html')

#category topic title letter_link published_date preview writer
# db에서 뉴스들 가져오기
def news_detail(request, sid1, sid2):
    mylist=[sid1,sid2]
    
    if request.method == 'POST':
        contents = parsing(sid1, sid2)
        mylist = [sid1, sid2]
        #form = LetterForm()
       
        for data in contents:
            print(data[2])
            form = Letter(
                category=str(sid1) ,
                topic=str(sid2),
                title= data[0],
                letter_link=data[1],
                published_date=data[2],
                preview= data[3],
                writer=data[4]
                )
            form.save()
    else:
        print('GET')
        
    # 버튼 누르면 현재뉴스목록 DB에 저장
    # => topic이 fk,
    # => title로 중복체크
    # print(request.POST['sid1'])
    News = Letter.objects.filter(topic= str(sid2),created_date__lte = timezone.now()).order_by('created_date')
    
    # pagination
    paginator = Paginator(News,3)
    page_no = request.GET.get('page')
    try:
        News_p = paginator.page(page_no)
    except PageNotAnInteger:
        News_p = paginator.page(1)
    except EmptyPage:
        News_p = paginator.page(paginator.num_pages)

    return render(request, 'news/news_detail.html' ,{'message': News_p, 'key':mylist})



def news_sports(request, sports):
    print(sports)
    contents = selenium_parsing()


    return render(request, 'news/news_sports.html',{'message':contents})