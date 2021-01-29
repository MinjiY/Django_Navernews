from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from news.models import Letter 
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from django.utils import timezone

from selenium import webdriver
import time
from news.forms import NameForm, UDForm
from django.db.models import Q
from django.views.generic.edit import FormView

# Create your views here.


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
                # 게시일 + 최종 수정일
                # 최종 수정일 버림
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
    
    # category topic title letter_link published_date preview writer

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


def news_list(request):
    # DB에서 한 토픽당 글 레터 두개씩 가져와서 뿌림
    contents = {}
    key = 0
    try:
        economy=  Letter.objects.filter(category__icontains='101' ).order_by('-created_date')
        it_sc = Letter.objects.filter(category__icontains='105' ).order_by('-created_date')
        sports= Letter.objects.filter(category__icontains='sports' ).order_by('-created_date')
        contents = {'economy': economy , 'it_sc': it_sc, 'sports':sports}
    except:
        key=1

    return render(request, 'news/news_list.html',{'message':contents, 'key':key})


def news_detail(request, sid1, sid2):
    mylist=[sid1,sid2]
    
    if request.method == 'POST':
        contents = parsing(sid1, sid2)
        mylist = [sid1, sid2]
        UDform = UDForm(request.POST)
        if UDform.is_valid():
            if UDform.cleaned_data['UD'] == 'update':
                for data in contents:
                    form = Letter(
                        category=str(sid1),
                        topic=str(sid2),
                        title= data[0],
                        letter_link=data[1],
                        published_date=data[2],
                        preview= data[3],
                        writer=data[4]
                        )
                    form.save()
            elif UDform.cleaned_data['UD'] =='delete':
                Letter.objects.filter(topic=sid2).delete()

    else:
        print('GET')
    News = Letter.objects.filter(topic= str(sid2),created_date__lte = timezone.now()).order_by('-created_date')
    
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
    if request.method == 'POST':       
        contents = selenium_parsing(sports)
        UDform = UDForm(request.POST)
        if UDform.is_valid():
            if UDform.cleaned_data['UD'] == 'update':
                for data in contents:
                    print(data[2])
                    form = Letter(
                        category = 'sports',
                        topic= sports,
                        title= data[0],
                        letter_link=data[1],
                        published_date=data[2],
                        preview= data[3],
                        writer=data[4]
                        )
                    form.save()
            elif UDform.cleaned_data['UD'] =='delete':
                Letter.objects.filter(topic=sports).delete()
    else:
        print('GET')
    News = Letter.objects.filter(topic= sports ,created_date__lte = timezone.now()).order_by('created_date')
    paginator = Paginator(News,3)
    page_no = request.GET.get('page')
    try:
        News_p = paginator.page(page_no)
    except PageNotAnInteger:
        News_p = paginator.page(1)
    except EmptyPage:
        News_p = paginator.page(paginator.num_pages)
    return render(request, 'news/news_sports.html',{'message':News_p, 'key':sports})




def news_search(request):
    context ={}
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['news_topic']
            _title = form.cleaned_data['news_title']
            news_list=[]
            if topic== 'default':
                news_list = Letter.objects.filter(title__icontains=_title)
            else:
                news_func = lambda __x__: Letter.objects.filter(Q(topic__icontains=__x__) & Q(title__icontains=_title)).distinct()
                news_list = news_func(topic)
           
            context['form'] = form
            context['search_keyword'] = _title 
            context['result_list']= news_list
            return render(request, 'news/news_search.html', {'search_list': context})

    else:
        form = NameForm()

    return render(request, 'news/news_search.html', {'search_list': context})
