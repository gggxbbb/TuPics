import os
import json
from urllib import request
from email.utils import formatdate

output_pics={}

output_pics['info'] = {}
output_pics['info']['start'] = formatdate(None, usegmt=True)

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

def getJson(url):
    req = request.Request(url, headers=header)
    data = request.urlopen(req).read().decode('utf-8')
    return json.loads(data)

if not os.path.isdir('build'):
    os.mkdir('build')

# today
output_pics['info']['today'] = {}
output_pics['info']['today']['start']= formatdate(None, usegmt=True)
today = getJson('https://v2.api.dailypics.cn/today')
output_pics['today'] = today
output_pics['info']['today']['end']= formatdate(None, usegmt=True)

# sort_all
output_pics['info']['sort'] = {'all':{'start':formatdate(None, usegmt=True)}}
sort = getJson('https://v2.api.dailypics.cn/sort')['result']
output_pics['sort'] = sort
output_pics['archive']={}
print(sort)
for k in sort:
    print(k)
    output_pics['archive'][k['TID']]=[]
    output_pics['info']['sort'][k['TID']] = {}
output_pics['info']['sort']['all']['end']=formatdate(None, usegmt=True)

# sort_one
for k in sort:
    print(k)
    output_pics['info']['sort'][k['TID']]['start'] = formatdate(None, usegmt=True)
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
    output_pics['info']['sort'][k['TID']]['end'] = formatdate(None, usegmt=True)

output_pics['info']['end']= formatdate(None, usegmt=True)

# output
with open('build/all.json','w',encoding='utf-8') as f:
    f.write(json.dumps(output_pics))
    f.close()