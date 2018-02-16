#爬取url = http://www.pastenglish.com/Course/?cid=50&sign=YYget --------- 1.2 名词基础训练(二)
#2018年2月10日 11:46:16    目前把问题、选项、答案解析都存为一个列表保存
from pyquery import PyQuery as pq
from selenium import webdriver
import re


f = open('test.html','r',encoding='utf-8')
text = f.read()

doc = re.compile(r'<div.*?td.*?id="j\d\d">(.*?)<br />(.*?)<br />.*?</div>')
content = doc.findall(text)

def get_question(content):
    '''获取网站里的问题并存为list'''
    question = []
    for i in range(0, 20):
        # 将列表里的元组变为list
        question.append(list(content[i]))

        if question[i][1].find('A.') == 0:
            del question[i][1]
        # print(question[i])    #【测试行】
    # print(question)           #【测试行】
    # return question

def get_answer(text):

    doc = re.compile(r'div.*?td.*?id="j\d\d">.*?(?<=(A\.|B\.|C\.|D\.))(.*?)<br /><div')
    temp = doc.findall(text)
    a1 = []
    for i in range(0, 20):
        a1.append(list(temp[i]))
    a2 = a1
    a3 = []
    temp1 = []
    for i in range(0,20):
        a3.append(a1[i][0] + a2[i][1])

        temp1.append(re.sub(r'\xa0\xa0|<br />', '', a3[i]))
        # temp2 = re.sub(r'<br />', '\n', a3[i])
    print(temp1)    #【测试行】



def get_detail(text):
    temp = pq(text)
    items = temp('.s ').items()
    analysis = []

    for item in items:
            analysis.append(item.find('.ans').text())
    # print(analysis)     #【测试行】每个元素都有一个\n，不知道后续加入数据库有没有影响

if __name__ == '__main__':
    get_detail(text)

