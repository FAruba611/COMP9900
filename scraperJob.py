"""
-------------------------
Program:scraperJob.py
Author: Group: CS9900_4AM
Python3 -V: 3.6.3
Prog -Version: 2.2
Current progress:
\\ add ip pool(not tested yet)
\\ inplementing next button clicking
\\ applying header cookies for authentication
\\ add tag of name in json
Date: 2018.09.10 21:18 PM
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



def page_to_json(page_src,filename,tag):
    
    soup = BeautifulSoup(page_src, 'html.parser')
    try:
        job=soup.select("div.jobsearch-JobComponent")
        #print(resume)
        _tag=tag
    except:
        print("scrape error")
        _tag = "pass"

    print("status: {}".format(_tag))
    if _tag == "deal":
        #print("=>{} {}".format(len(name_appear), name_appear))
        name=job[0].find(class_="jobsearch-JobInfoHeader-title").get_text()
        info=job[0].find(class_="jobsearch-JobComponent-description").get_text()
        print("===")
        
        obj={}
        obj["name"]=name
        obj["info"]=info
        
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
name_appear = []
path = "/usr/local/bin/chromedriver"
origin_webpage = "https://au.indeed.com/"

account = "franklee940611@gmail.com"
password = "9900testing"
browser = webdriver.Chrome(path)

browser.get(origin_webpage)
browser.set_window_size(1155, 1400)
# browser.set_window_size(1400, 1400)

# ==== simulate to login the website
browser.find_element_by_link_text("Sign in").click()
browser.find_element_by_id("signin_email").clear()
browser.find_element_by_id("signin_email").send_keys(account)
browser.find_element_by_id("signin_password").clear()
browser.find_element_by_id("signin_password").send_keys(password)
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

# ==== find jobs and write to json db
browser.find_element_by_link_text("Find Jobs").click()
# browser.find_element_by_link_text(u"Next »").click()
browser.find_element_by_id("text-input-what").click()
browser.find_element_by_id("text-input-what").clear()
browser.find_element_by_id("text-input-what").send_keys("Marketing")
browser.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='job title, keywords, or company'])[1]/following::div[2]").click()
browser.find_element_by_id("text-input-where").click()
browser.find_element_by_id("text-input-where").clear()
browser.find_element_by_id("text-input-where").send_keys("Sydney NSW")
browser.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='city, state/territory or postcode'])[1]/following::div[2]").click()
browser.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='city, state/territory or postcode'])[1]/following::button[1]").click()

# browser.find_element_by_css_selector(".confirm-nav.next").click()
# time.sleep(10)
# browser.find_element_by_css_selector(".confirm-nav.next").click()
page = 0
while True:
    time.sleep(5)
    links = browser.find_elements_by_class_name("turnstileLink")
    init_len = len([link for link in links if link.get_attribute("data-tn-element") == "jobTitle"])
    # rec per page
    for i in range(0,init_len):  
        print("\npage {} link {}".format(page + 1, i + 1))
        links = browser.find_elements_by_class_name("turnstileLink")
        valid_links = [link for link in links if link.get_attribute("data-tn-element") == "jobTitle"]
        # for i,l in enumerate(valid_links):
        #     print(valid_links[i].text)
        #     #valid_links[i].text = re.sub(r'target=\"_blank\"',r'target=\"\"',l.text)
        curr_len = len(valid_links)
        # print(curr_len)
        if (curr_len > init_len and i == init_len-1) or (curr_len < init_len and i == curr_len - 1) :
            print("=====")
            break
        
        links_name = [valid_link.text for valid_link in valid_links]
        link_name = links_name[i]
        print("=={} \n".format(link_name))
        status = 'pass'
        if link_name not in name_appear:
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
            time.sleep(9)
            
            print("===> {}".format(browser.find_element_by_link_text(link_name).get_attribute('target')))

            js = """
            arguments[0].target = "";
            
            """
            browser.execute_script(js, browser.find_element_by_link_text(link_name))
            print("===> {}".format(browser.find_element_by_link_text(link_name).get_attribute('target')))
            print("---")
            #link_name = re.sub("target=\"_blank\"", "target=\"\"", link_name)
            # print(browser.find_element_by_link_text(link_name).get_attribute('innerHTML'))
            # browser.find_element_by_link_text(link_name).click()
            curr_url = browser.find_element_by_link_text(link_name).get_attribute("href")
            browser.get(curr_url)
            page_to_json(browser.page_source, "data_job.json", status) #browser.current_url
            time.sleep(4)
            browser.back()
        except:
            print("execute error")
            continue
    time.sleep(3)
    g = browser.find_elements_by_class_name('np')[0].click()
   
    
     
    # click next
    page+=1
    
    
    #browser.find_elements_by_class_name("confirm-nav next").click()
           
    assert "No results found." not in browser.page_source  #如果当前页面文本中有“No results found.”则程序跳出
driver.close()  #关闭webdriver


# ===========
