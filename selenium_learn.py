from selenium import webdriver
from time import sleep
from pyquery import PyQuery as pq
import re

try:
    brower = webdriver.Chrome()
    brower.get('http://www.pastenglish.com/Course/?cid=50&sign=YYget')
    brower.find_element_by_css_selector("[onclick='opendiv(2,this)']").click()

    sleep(5)    #等待网页代码加载
    html = brower.page_source
    print(html)
    doc = pq(html)
    sleep(5)

finally:
    brower.close()