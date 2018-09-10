"""
-------------------------
Program:scraper.py
Author: Group: CS9900_4AM
Python3 -V: 3.6.3
Prog -Version: 1.8
Current progress:
\\ add ip pool(not tested yet)
\\ inplementing next button clicking
\\ applying header cookies for authentication
\\ add tag of name in json
Date: 2018.09.04 22:36 PM
Desc: Plz install browser driver(chromedriver/firefoxdriver...) in MAC's usr/local/bin
      package needed:
    + selenium, unittest, time, re, threading, qu
-------------------------
"""

from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
from threading import Thread
from queue import Queue
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
import json
import requests

_BE_PROXY_QUEUE = Queue()
_file_path = 'mt_proxy.txt'
_DISPLAY_LINK = 50
name_appear = []


class Consumer_Thread(Thread):
    def run(self):
        global _BE_PROXY_QUEUE
        while not _BE_PROXY_QUEUE.empty():
            p = _BE_PROXY_QUEUE.get()
            try:
                if test_useful(p):
                    with open(_file_path, 'a') as f:
                        f.write(p + '\n')
            except Exception as e:
                print('[HERE] {}'.format(e))
                pass
            finally:
               _BE_PROXY_QUEUE.task_done()


def test_useful(proxy):
    print('[INFO] Testing proxy {} {}'.format(proxy, ' now...'))
    try:
        proxies = {'http': proxy}
        requests.get('http://ip.cip.cc', timeout=20, proxies=proxies)
        print('[Congra] Successfully get one')
        return True
    except Exception as e:
        print(e)
    return False


def get_proxies_from_KDL(max_page):
    print('[Scrapy] Start Scrapying Proxies in KDL')

    base_url = 'http://www.kuaidaili.com/free/'
    options = ['intr/', 'inha/']

    p_pool = []

    print('===============\n Scraping XICI DAILI \n===============\n')
    xici_page = 1

    while xici_page <= 3:
        #   xicidaili
        new_count = 0
        print('PAGE {}'.format(str(xici_page)))
        xici_url = 'http://www.xicidaili.com/nt/' + str(xici_page)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}
        try:
            rx = requests.get(xici_url, timeout=15, headers=headers)
            bobj_2 = BeautifulSoup(rx.content.decode('utf-8'))
            sibs = bobj_2.findAll('table', {'id': 'ip_list'})[0].tr.next_siblings
        except Exception as e:
            try:
                print('error 1: {}'.format(e))
                rx = requests.get(xici_url, timeout=15, headers=headers)
                bobj_2 = BeautifulSoup(rx.content.decode('utf-8'))
                sibs = bobj_2.findAll('table', {'id': 'ip_list'})[0].tr.next_siblings

            except Exception as e:
                print('error 2: {}'.format(e))
                break

        for sib in sibs:
            try:
                get_proxy = sib.findAll('td')[2].get_text() + ':' + sib.findAll('td')[3].get_text()
                p_pool.append(get_proxy)
                new_count += 1
            except AttributeError:
                pass
        print('get {} proxies in page {}'.format(new_count, xici_page))
        xici_page += 1
    # the n-th sub page
    opt = 0
    while opt <= 1:
        page = 1
        print('===============\n Scraping {} \n===============\n'.format(options[opt]))
        while page < max_page:
            url = base_url + options[opt] + str(page) + '/'
            driver = webdriver.PhantomJS(
                executable_path=r"/root/csdn_spider/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
            #driver = webdriver.PhantomJS(executable_path=r'D:\phantomjs-2.1.1-windows\bin\phantomjs.exe')
            driver.get(url)
            print('Sleep 0.7 sec...')
            time.sleep(0.7)
            bobj = BeautifulSoup(driver.page_source)
            driver.close()
            siblings = bobj.findAll(name='table', attrs={'class': 'table table-bordered table-striped'})[
                0].tbody.tr.next_siblings
            count = 0
            for sibling in siblings:
                try:
                    get_proxy = sibling.findAll(name='td')[0].get_text() + ':' + sibling.findAll(name='td')[
                        1].get_text()
                    p_pool.append(get_proxy)
                    count += 1
                except AttributeError:
                    pass
            print('Get {} proxy'.format(str(count)))
            page += 1
        opt += 1



    print('*****************************')
    print('Finished! Get {} useful proxies in total'.format(len(p_pool)))
    return p_pool
    # with open('proxy_kdl.txt', 'w') as f:
    #    for p in p_pool:
    #        p = p + '\n'
    #        f.write(p)
    # print 'Successfully written in \'proxy_kdl.txt\''


def get_proxies_from_file():
    with open('proxy_kdl.txt', 'r') as f:
        return f.readlines()


def test_proxies_efficience(proxy):
    proxies = {'http': proxy}
    start = time.time()
    for i in range(3):
        r = requests.get('http://www.baidu.com', proxies=proxies)
        print('{}   {}'.format(i,r.text))
    cost = time.time() - start
    print('With Proxy: cost ', cost / 3, ' seconds')

    start = time.time()
    for i in range(3):
        r = requests.get('http://ip.cip.cc')
        print('{}   {}'.format(i,r.text))
    cost = time.time() - start
    print('Without Proxy: cost {} seconds'.format(cost / 3))


def page_to_json(page_src,filename,tag):
    global name_appear
    #page=requests.get(url)
    soup = BeautifulSoup(page_src, 'html.parser')
    try:
        resume=soup.select("div#resume_body")
        #print(resume)
        name=resume[0].find_all(id="resume-contact")
        name_text = name[0].get_text()
        _tag=tag
    except:
        print("scrape error")
        _tag = "pass"

    print("status: {}".format(_tag))
    if _tag == "deal":
        #print("=>{} {}".format(len(name_appear), name_appear))
        name_list=name[0].get_text()
        skills=resume[0].find_all(class_="skill-text")
        if skills:
            skills_list=[s.get_text() for s in skills]
        else:
            skills_list=[]
        #experiences=resume[0].select("div.work-experience-section")
        experiences=resume[0].find_all(class_="work-experience-section")
        #print(experiences[0].prettify())
        experiences_list=[]
        if experiences:
            for e in experiences:
                d={}
                title=e.find(class_="work_title title")
                if title:
                    d['title']=title.get_text()
                company=e.find(class_="work_company")
                if company:
                    d['company']=company.get_text() 
                date=e.find(class_="work_dates")
                if date:
                    d['date']=date.get_text()
                desc=e.find(class_="work_description")
                if desc:
                    d['desc']=desc.get_text()
                    if d['desc'] == "":
                        info = ""
                        for i in desc.next_siblings:
                            info+=i.get_text()
                        d['desc'] = info

                experiences_list.append(d)
        education=resume[0].find_all(class_="education-section")
        education_list=[]
        if education:
            for e in education:
                d={}
                
                title=e.find(class_="edu_title")
                if title:
                    d['title']=title.get_text() 

                school=e.find(class_="edu_school")
                if school:
                    d['school']=school.get_text()
                address= e.find(class_="inline-block")
                if address:
                    d['address']=address.get_text()
                date=e.find(class_="edu_dates")
                if date:
                    d['date']=date.get_text()
                education_list.append(d)

        certification=resume[0].find_all(class_="certification-section")
        certification_list=[]
        if certification:
            for c in certification:
                d={}
                title=c.find(class_="certification_title")
                if title:
                    d["title"]=title.get_text()
                date=c.find(class_="certification_date")
                if date:
                    d["date"]=date.get_text()
                desc=c.find(class_="certification_description")
                if desc:
                    d["desc"]=desc.get_text()
                    if d["desc"] == "":
                        info = ""
                        for i in desc.next_siblings:
                            info += i.get_text()
                        d['desc'] = info

                certification_list.append(d)
        obj={}
        obj["name"]=name_list
        obj["skills"]=skills_list
        obj["experiences"]=experiences_list
        obj["education"]=education_list
        obj["certification"]=certification_list
        with open(filename, 'a') as f:
            #print(obj)
            json.dump(obj, f)
            f.write("\n,")

    
    print()

    #j=json.dumps(education_list)

    
    #j=json.dumps(obj)
    #print(j)
    
    



# main()
# ==== initialise
path = "/usr/local/bin/chromedriver"
origin_webpage = "https://au.indeed.com/"
browser = webdriver.Chrome(path)

browser.get(origin_webpage)

# ==== simulate to login the website
browser.find_element_by_link_text("Sign in").click()
browser.find_element_by_id("signin_email").clear()
browser.find_element_by_id("signin_email").send_keys("franklee940611@gmail.com")
browser.find_element_by_id("signin_password").clear()
browser.find_element_by_id("signin_password").send_keys("ipALL245m4a1lcrfr")
browser.find_element_by_id("signin_remember").click()
browser.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Keep me signed in on this device.'])[1]/following::button[1]").submit()

req = requests.Session()
headers = {
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
}
req.headers.update(headers)
cookies = browser.get_cookies()
with open("cookies.txt", "w") as fp:
    json.dump(cookies, fp)
for cookie in cookies:
    req.cookies.set(cookie['name'], cookie['value'])
req.get(origin_webpage)

#print(cookies)

time.sleep(7)

# ==== find resume and write to json db
browser.find_element_by_link_text("Find Resumes").click()
browser.find_element_by_id("query").clear()
browser.find_element_by_id("query").send_keys("Marketing")
browser.find_element_by_id("location").clear()
browser.find_element_by_id("location").send_keys("Sydney NSW")

browser.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Skills'])[1]/input[1]").click()
browser.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Companies'])[1]/input[1]").click()
browser.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Field of Study'])[1]/input[1]").click()
browser.find_element_by_id("submit").click()

# browser.find_element_by_css_selector(".confirm-nav.next").click()
# time.sleep(10)
# browser.find_element_by_css_selector(".confirm-nav.next").click()
page = 0
while True:
    
    length = _DISPLAY_LINK # rec per page
    for i in range(0,length):  
        print("page {} link {}".format(page+1, i+1))
        # links = browser.find_elements_by_tag_name("a")
        # links = browser.find_elements_by_xpath("//*[@href]")
        links = browser.find_elements_by_class_name("app_link")
        if (len(links) < length and i == len(links)):
            browser.close()
            sys.exit(0)
        link = links[i]
        links_name = [link.text for link in links]
        link_name = links_name[i]
        print("=={} \n".format(link_name))
        status = 'pass'
        if link_name not in name_appear and link_name != 'Job Seeker':
            name_appear.append(link_name)
            status = "deal"
        else:
            print("name error")
            continue
        # several tests
        # print("-------------")
        # print("link = {}".format(link.text))
        # print(link.get_attribute("attribute name"))
        # print(link.get_attribute("target"))
        # print(link.tag_name)
        # print(link.parent)
        # print(link.location)
        # print(link.size)
        # 
        #if not ("_blank" in link.get_attribute("target") or "http" in link.get_attribute("href")):
        #if link.get_attribute("target") == "_blank":
        try:
            time.sleep(7)
            js = """
            var i = arguments[0];
            console.log(i);
            document.getElementsByClassName("app_link")[i].target=""; 

            """
            browser.execute_script(js, i)
            browser.find_element_by_link_text(link_name).click()

            page_to_json(browser.page_source,"data_grab.json",status) #browser.current_url
            time.sleep(4)
            browser.back()
        except:
            print("execute error")
            continue

    browser.find_element_by_css_selector(".confirm-nav.next").click() # click next
    page+=1
    #browser.find_elements_by_class_name("confirm-nav next").click()
           
    assert "No results found." not in browser.page_source  #如果当前页面文本中有“No results found.”则程序跳出
driver.close()  #关闭webdriver


# ===========
