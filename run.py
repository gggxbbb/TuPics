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
for k in sort:
    print(k)
    output_pics['sort_map'][k['TID']] = k
    output_pics['archive'][k['TID']]=[]
    output_pics['info']['sort'][k['TID']] = {}
output_pics['info']['sort']['all']['end']=getTime()

# today
output_pics['info']['today'] = {}
output_pics['info']['today']['start']= getTime()
today = getJson('https://v2.api.dailypics.cn/today')
output_pics['today'] = today
output_pics['info']['today']['end']= getTime()

# sort_one
for k in sort:
    print(k)
    output_pics['info']['sort'][k['TID']]['start'] = getTime()
    first_page = getJson('https://v2.api.dailypics.cn/list/?page=1&size=15&sort=%s' % k['TID'])
    max_page = first_page['maxpage']
    print(max_page)
    for pic in first_page['result']:
        output_pics['archive'][pic['TID']].append(pic)
    for p in range(1, int(max_page)):
        page = p+1
        this_page = getJson('https://v2.api.dailypics.cn/list/?page=%s&size=15&sort=%s' % (page, k['TID']))['result']
        print(page)
        for pic in this_page:
            output_pics['archive'][pic['TID']].append(pic)
    output_pics['info']['sort'][k['TID']]['end'] = getTime()

# output

output_pics['info']['end']= getTime()

for v in today:
    for p in today:
        print(p['PID'])
        buildOne(p)

for v in sort:
    for p in output_pics['archive'][v['TID']]:
        print(p['PID'])
        buildOne(p)

with open('pages/home.html','r',encoding='utf-8') as f:
    index_page = Template(f.read())
    f.close()

with open('build/index.html','w',encoding='utf-8') as f:
    f.write(index_page.render(pics=output_pics))
    f.close()

with open('build/today.json','w',encoding='utf-8') as f:
    f.write(json.dumps(today))
    f.close()

with open('build/sort.json','w',encoding='utf-8') as f:
    f.write(json.dumps(sort))
    f.close()

with open('build/sort2.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics['sort_map']))
    f.close()

for v in sort:
    with open('build/sort-%s.json'%v['TID'],'w',encoding='utf-8') as f:
        f.write(json.dumps(output_pics['archive'][v['TID']]))
        f.close()

with open('build/all.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics))
    f.close()