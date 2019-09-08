#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import pytz  
import datetime  
import time
import random
from urllib import request
from jinja2 import Template

ua = [
    'Mozilla/5.0 (Android 9; Mobile; rv:68.0) Gecko/68.0 Firefox/68.0',
]

# 获取 JOSN 数据
def getJson(url):
    req = request.Request(url, headers={'User-Agent':ua[random.randint(0,len(ua)-1)]})
    data = request.urlopen(req).read().decode('utf-8')
    return json.loads(data)

# 获取格式化的北京时间
def getTime():
    beijing_time = datetime.datetime.now(pytz.timezone('PRC'))
    return beijing_time.strftime('%Y-%m-%d %H:%M:%S')

# 下载图片
def download(pic):
    file_path = 'build/%s.jpeg'%pic['PID']
    if os.path.isfile(file_path):
        print('%s.jpeg 已存在'%pic['PID'])
        return 0
    req = request.Request(pic['local_url']+'?p=0', headers={'User-Agent':ua[random.randint(0,len(ua)-1)]})
    data = request.urlopen(req).read()
    with open(file_path,'wb') as f:
        f.write(data)
        f.close()

# 初始化字典
output_pics={}
output_pics['info'] = {}
output_pics['info']['start'] = getTime()

# 获取格式化的今日日期(北京时间)
date_today = datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d')

# 创建输出目录
if not os.path.isdir('build'):
    os.mkdir('build')

# 加载 Detail 页面模板
with open('pages/detail.html','r',encoding='utf-8') as f:
    datail_page = Template(f.read())
    f.close()

# 用于构建单张图片的 Detail 页面
def buildOne(pic):
    with open('build/%s.html'%pic['PID'],'w',encoding='utf-8') as f:
        f.write(datail_page.render(pic=pic,sort=output_pics['sort_map'][pic['TID']]))
        f.close()
    with open('build/%s.json'%pic['PID'],'w',encoding='utf-8') as f:
        f.write(json.dumps(pic))
        f.close()


# 获取分类
print('sorts')
## 记录开始时间
output_pics['info']['sort'] = {'all':{'start':getTime()}}
## 获取分类数据
sort = getJson('https://v2.api.dailypics.cn/sort')['result']
## 将分类数据存入字典
output_pics['sort'] = sort
## 初始化存储
output_pics['sort_map'] = {}
output_pics['archive']={}
## 打个输出，以免看着心慌
print(sort)
## 遍历分类
for v in sort:
    ### 打个输出，以免看着心慌
    print(v)
    ### 将 List 变为 Dict
    output_pics['sort_map'][v['TID']] = v
    ### 初始化各分类归档
    output_pics['archive'][v['TID']]=[]
    output_pics['info']['sort'][v['TID']] = {}
## 记录结束时间
output_pics['info']['sort']['all']['end']=getTime()


# 获取今日
print('today')
## 记录开始时间
output_pics['info']['today'] = {}
output_pics['info']['today']['start']= getTime()
## 获取今日
today = getJson('https://v2.api.dailypics.cn/today')
output_pics['today'] = today
## 存储备案过的地址并下载图片
for v in output_pics['today']:
    print(v['PID'])
    v['mainland_url'] = v['local_url'].replace('img.dpic.dev','images.dailypics.cn')
    download(v)
## 记录结束时间
output_pics['info']['today']['end']= getTime()


# 是否咕咕咕
print('GuGuGu')
## 初始化 List
GuGuGu = []
## 遍历今日图片
for v in output_pics['today']:
    ### 判断是否咕咕咕并存储
    if (v['p_date'] == date_today):
        v['if_today'] = True
    else:
        v['if_today'] = False
        #### 记录咕咕咕的分类
        GuGuGu.append(output_pics['sort_map'][v['TID']])
## 将咕咕咕的分类存入主 Dict
output_pics['not_updated'] = {'sort':GuGuGu}
## 输出可读的咕咕咕情况
print(GuGuGu)
if (not (len(GuGuGu) == 0)):
    ### 如果咕咕咕输出咕咕咕的分类
    GuGuGu_srt = ','.join([v['T_NAME'] for v in GuGuGu]) + '没有更新'
else:
    GuGuGu_srt = '所有分类均已更新'
## 将可读的咕咕咕情况存入主 Dict
output_pics['not_updated']['info'] = GuGuGu_srt

# 单个分类
print('sort')
## 遍历所有分类
for v in sort:
    ### 打个输出，以免看着心慌
    print(v['TID'])
    ### 记录开始时间
    output_pics['info']['sort'][v['TID']]['start'] = getTime()
    ### 获取第一页和总页数
    first_page = getJson('https://v2.api.dailypics.cn/list/?page=1&size=15&sort=%s' % v['TID'])
    max_page = first_page['maxpage']
    ### 打个输出，以免看着心慌
    print(max_page)
    ### 遍历结果，存入主 Dict
    for pic in first_page['result']:
        output_pics['archive'][pic['TID']].append(pic)
    ### 循环获取之后的个页
    for p in range(1, int(max_page)):
        page = p+1
        this_page = getJson('https://v2.api.dailypics.cn/list/?page=%s&size=15&sort=%s' % (page, v['TID']))['result']
        print(page)
        for pic in this_page:
            output_pics['archive'][pic['TID']].append(pic)
    ### 记录结束时间
    output_pics['info']['sort'][v['TID']]['end'] = getTime()

## 存储备案过的地址并下载图片
for v in sort:
    for pic in output_pics['archive'][v['TID']]:
        print(pic['PID'])
        pic['mainland_url'] = pic['local_url'].replace('img.dpic.dev','images.dailypics.cn')
        download(pic)

## 记录结束时间
output_pics['info']['end']= getTime()

print('output')

# 输出今日图片的 Detail 页面
for p in today:
    print(p['PID'])
    buildOne(p)

# 输出所有图片的 Detail 页面
## 遍历所有分类
for v in sort:
    ### 遍历归档
    for p in output_pics['archive'][v['TID']]:
        print(p['PID'])
        buildOne(p)

# 输出主页
## 加载模板
with open('pages/home.html','r',encoding='utf-8') as f:
    index_page = Template(f.read())
    f.close()
## 输出主页
with open('build/index.html','w',encoding='utf-8') as f:
    f.write(index_page.render(pics=output_pics,not_updated=GuGuGu_srt))
    f.close()

# 输出 JSON
## 输出今日图片
with open('build/today.json','w',encoding='utf-8') as f:
    f.write(json.dumps(today))
    f.close()
## 输出分类
with open('build/sort.json','w',encoding='utf-8') as f:
    f.write(json.dumps(sort))
    f.close()
## 输出转换后的分类
with open('build/sort2.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics['sort_map']))
    f.close()
## 输出各分类归档
### 遍历分类
for v in sort:
    #### 输出归档
    with open('build/sort-%s.json'%v['TID'],'w',encoding='utf-8') as f:
        f.write(json.dumps(output_pics['archive'][v['TID']]))
        f.close()
## 输出时间
with open('build/info.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics['info']))
    f.close()
## 输出咕咕咕情况
with open('build/not_updated.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics['not_updated']))
    f.close()
## 输出主 Dict
with open('build/all.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics))
    f.close()
