#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import pytz  
import datetime  
import time
from urllib import request
from jinja2 import Template

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

def getJson(url):
    req = request.Request(url, headers=header)
    data = request.urlopen(req).read().decode('utf-8')
    return json.loads(data)

def getTime():
    beijing_time = datetime.datetime.now(pytz.timezone('PRC'))
    return beijing_time.strftime('%Y-%m-%d %H:%M:%S')


output_pics={}
output_pics['info'] = {}
output_pics['info']['start'] = getTime()
today = datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d')

if not os.path.isdir('build'):
    os.mkdir('build')

with open('pages/detail.html','r',encoding='utf-8') as f:
    datail_page = Template(f.read())
    f.close()

def buildOne(pic):
    with open('build/%s.html'%pic['PID'],'w',encoding='utf-8') as f:
        f.write(datail_page.render(pic=pic,sort=output_pics['sort_map'][pic['TID']]))
        f.close()
    with open('build/%s.json'%pic['PID'],'w',encoding='utf-8') as f:
        f.write(json.dumps(pic))
        f.close()

# sort_all
output_pics['info']['sort'] = {'all':{'start':getTime()}}
sort = getJson('https://v2.api.dailypics.cn/sort')['result']
output_pics['sort'] = sort
output_pics['sort_map'] = {}
output_pics['archive']={}
print(sort)
for v in sort:
    print(v)
    output_pics['sort_map'][v['TID']] = v
    output_pics['archive'][v['TID']]=[]
    output_pics['info']['sort'][v['TID']] = {}
output_pics['info']['sort']['all']['end']=getTime()

# today
output_pics['info']['today'] = {}
output_pics['info']['today']['start']= getTime()
today = getJson('https://v2.api.dailypics.cn/today')
output_pics['today'] = today
output_pics['info']['today']['end']= getTime()

# if GuGuGu
GuGuGu = []
for v in output_pics['today']:
    if v['p_date'] == today:
        v['if_today'] = True
    else:
        v['if_today'] = False
        GuGuGu.append(output_pics['sort_map'][v['TID']])
output_pics['not_updated'] = {'sort':GuGuGu}
if not (len(GuGuGu) == 0):
    GuGuGu_srt = ','.join([v['T_NAME'] for v in GuGuGu]) + '没有更新'
else:
    GuGuGu_srt = '所有分类均已更新'
output_pics['not_updated']['info'] = GuGuGu_srt

# sort_one
for v in sort:
    print(v)
    output_pics['info']['sort'][v['TID']]['start'] = getTime()
    first_page = getJson('https://v2.api.dailypics.cn/list/?page=1&size=15&sort=%s' % v['TID'])
    max_page = first_page['maxpage']
    print(max_page)
    for pic in first_page['result']:
        output_pics['archive'][pic['TID']].append(pic)
    for p in range(1, int(max_page)):
        page = p+1
        this_page = getJson('https://v2.api.dailypics.cn/list/?page=%s&size=15&sort=%s' % (page, v['TID']))['result']
        print(page)
        for pic in this_page:
            output_pics['archive'][pic['TID']].append(pic)
    output_pics['info']['sort'][v['TID']]['end'] = getTime()

# output
output_pics['info']['end']= getTime()

## detail
for v in today:
    for p in today:
        print(p['PID'])
        buildOne(p)

## sort_one
for v in sort:
    for p in output_pics['archive'][v['TID']]:
        print(p['PID'])
        buildOne(p)

## home page
with open('pages/home.html','r',encoding='utf-8') as f:
    index_page = Template(f.read())
    f.close()

with open('build/index.html','w',encoding='utf-8') as f:
    f.write(index_page.render(pics=output_pics,not_updated=GuGuGu_srt))
    f.close()

## json_today
with open('build/today.json','w',encoding='utf-8') as f:
    f.write(json.dumps(today))
    f.close()

## json_sort
with open('build/sort.json','w',encoding='utf-8') as f:
    f.write(json.dumps(sort))
    f.close()

## json_sort_map
with open('build/sort2.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics['sort_map']))
    f.close()

## json_archive
for v in sort:
    with open('build/sort-%s.json'%v['TID'],'w',encoding='utf-8') as f:
        f.write(json.dumps(output_pics['archive'][v['TID']]))
        f.close()

## json_info
with open('build/info.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics['info']))
    f.close()

## json_not_updated
with open('build/not_updated.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics['not_updated']))
    f.close()

## json_all
with open('build/all.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics))
    f.close()