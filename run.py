#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import re
import sys
from fractions import Fraction

import pytz
import requests
from jinja2 import Template
from markdown import markdown
from pinyin import get as pinyin

addition = {'~~': 'del'}


def md(text):
    _t = text
    for k in addition:
        _type = 0
        while k in _t:
            if _type == 0:
                _t = _t.replace(k, f'<{addition[k]}>', 1)
                _type = 1
            else:
                _t = _t.replace(k, f'</{addition[k]}>', 1)
                _type = 0
    return _t


ua = [
    'TuPics/' + datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y%m%d%H'),
]

ss = []

for v in ua:
    # 实例化 session
    s = requests.session()
    # 设置不同的 UA
    s.headers.update({'User-Agent': v})
    # 添加到 List
    ss.append(s)

http_count = 0


# 获取 Response
def get_req(url) -> requests.Response:
    # 随机获取 session
    _s = ss[random.randint(0, len(ua) - 1)]
    # 获取 Response
    req = _s.get(
        url,
        verify=False,
        )
    # 判断是否获取成功
    if not req.status_code == 200:
        # 失败抛出输出错误
        print(req.url, req.status_code, req.text)
        # 并退出
        sys.exit(1)
    global http_count
    http_count += 1
    # 返回获取的 Response
    return req


# 获取 JSON 数据
def get_json(url):
    # 获取 Response
    req = get_req(url)
    # 设置编码
    req.encoding = 'utf-8'
    # 序列化并返回
    # noinspection PyBroadException
    try:
        json.loads(req.text)
    except Exception:
        print(req.text)
    return json.loads(req.text)


# 获得 Bytes
def get_bytes(url):
    # 获得 Response 并直接返回 Content
    return get_req(url).content


# 获取格式化的北京时间
# 获得 datetime 对象
beijing_time = datetime.datetime.now(pytz.timezone('PRC')).replace(hour=0, minute=0, second=0)


def get_time():
    # 返回格式化时间
    return datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d %H:%M:%S')


# 从 cos 获得图片数据
# noinspection PyUnusedLocal
def get_info_from_cos(_pic):
    # try:
    # print('getFromCatch')
    # catch = json.loads(open('build/%s.json'%_pic['PID']).read())
    # if catch['info']['image']['size'] == 0:
    #    raise Exception('useless catch')
    # if (catch['nativePath'] == _pic['nativePath']):
    #    return catch['info']
    # raise Exception('useless catch')
    # except:
    # print('getFromCos')
    info = {'image': {'size': 0, 'format': 'null'}, 'exif': {}}
    # try:
    # info['image'] = getJson(_pic['s1_url']+'?imageInfo')
    # info['exif'] = getJson(_pic['s1_url']+'?exif')
    # except:
    return info


# 下载图片
def download(_pic):
    # 存储原始图片文件的路径
    # file_path = 'build/%s' % _pic['file_name']
    # 存储缩略图片文件的路径
    file_lite = 'img/%s' % _pic['PID']
    # 判断原始图片文件是否已存在
    # if os.path.isfile(file_path):
    #    # 存在输出提示
    #    print('%s 已存在' % file_path)
    # else:
    #    # 否则下载
    #    print('download')
    #    # 获得原始图片
    #    data = getBytes(_pic['mainland_url']+'?p=0')
    #    # 存储到文件
    #    with open(file_path, 'wb') as _f:
    #        _f.write(data)
    #        _f.close()
    # 判断缩略图片文件是否存在
    if os.path.isfile(file_lite):
        # 存在输出提示
        print('%s 已存在' % file_lite)
    else:
        # 否则下载
        print('-d')
        # 获得缩略图
        data2 = get_bytes(_pic['s1_url'])
        # 保存到文件
        with open(file_lite, 'wb') as _f:
            _f.write(data2)
            _f.close()
    return file_lite


# 获得图片信息
def get_info(_pic):
    _v = _pic
    # 获得非常友好的链接
    _v['s1_url'] = 'https://s1.images.dailypics.cn' + _v['nativePath']
    _v['s2_url'] = 'https://s2.images.dailypics.cn' + _v['nativePath']
    _v['type'] = os.path.splitext(_v['nativePath'])[-1]
    # 获得长宽比
    _v['aspect_ratio'] = get_asp(_v['height'], _v['width'])
    _v['info'] = get_info_from_cos(_v)
    # 获得文件体积
    _v['size_b'] = int(_v['info']['image']['size'])
    _v['size_kb'] = float('%.2f' % (_v['size_b'] / 1024))
    _v['size_mb'] = float('%.2f' % (_v['size_b'] / 1048576))
    if _v['size_mb'] < 1:
        _v['size'] = str(_v['size_kb']) + 'KB'
    else:
        _v['size'] = str(_v['size_mb']) + 'MB'
    # 格式化 p_content
    _v['p_content_html'] = md(
        markdown(
            re.sub(
                '(?!<= {2})\n',
                '  \n',
                _v['p_content'].replace('\r', '')
            )
        )
    )
    # 默认不是今日的图片 (:
    _v['if_today'] = False
    # 计算此图片和今日相差几天
    date = datetime.datetime.strptime(_v['p_date'], '%Y-%m-%d').replace(tzinfo=pytz.timezone('PRC'))
    _v['ago'] = (beijing_time - date).days
    if _v['ago'] == 0:
        _v['ago_zh'] = '今日'
    elif _v['ago'] == 1:
        _v['ago_zh'] = '昨天'
    elif _v['ago'] == 2:
        _v['ago_zh'] = '前天'
    else:
        _v['ago_zh'] = str(_v['ago']) + '天前'
    # 归类
    put_asp(_v)
    put_user(_v)
    put_date(_v)

    return _v


# 计算长宽比
def get_asp(height, width):
    _f = Fraction(width, height)
    n = _f.numerator
    d = _f.denominator
    if (n > 20) or (d > 20):
        _n = 0
        if n > d:
            _n = 16
        if n < d:
            _n = 9
        _d = d * _n / n
        n = _n
        d = ('%0.1f' % _d).replace('.0', '')
    return '%s:%s' % (n, d)


def put_user(_pic):
    if not (_pic['username'] in output_pics['username']):
        output_pics['username'].append(_pic['username'])
        output_pics['users'][_pic['username']] = []
    if not _pic['PID'] in [_v['PID'] for _v in output_pics['users'][_pic['username']]]:
        output_pics['users'][_pic['username']].append(_pic)


def put_asp(_pic):
    if not (_pic['aspect_ratio'] in output_pics['aspect_ratio']):
        output_pics['asp'].append(_pic['aspect_ratio'])
        output_pics['aspect_ratio'][_pic['aspect_ratio']] = []
    if not _pic['PID'] in [_v['PID'] for _v in output_pics['aspect_ratio'][_pic['aspect_ratio']]]:
        output_pics['aspect_ratio'][_pic['aspect_ratio']].append(_pic)


def put_date(_pic):
    if not (_pic['p_date'] in output_pics['dates']):
        output_pics['dates'].append(_pic['p_date'])
        output_pics['date'][_pic['p_date']] = []
    if not _pic['PID'] in [_v['PID'] for _v in output_pics['date'][_pic['p_date']]]:
        output_pics['date'][_pic['p_date']].append(_pic)


def sort_dict(_dict, reverse=False, key=lambda e: e[0]):
    n_keys = []
    n_dict = {}
    s_list = sorted(_dict.items(), key=key, reverse=reverse)
    for _v in s_list:
        n_keys.append(_v[0])
        n_dict[_v[0]] = _v[1]
    return n_keys, n_dict


# 初始化字典
# noinspection PyDictCreation
output_pics = {}
output_pics['info'] = {}
# noinspection PyTypeChecker
output_pics['info']['start'] = get_time()
output_pics['username'] = []
output_pics['users'] = {}
output_pics['asp'] = []
output_pics['aspect_ratio'] = {}
output_pics['date'] = {}
output_pics['dates'] = []
output_pics['count'] = {}

# 获取格式化的今日日期(北京时间)
date_today = datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d')

# 创建输出目录
if not os.path.isdir('build'):
    os.mkdir('build')

# 加载 Detail 页面模板
with open('pages/detail.html', 'r', encoding='utf-8') as f:
    detail_page = Template(f.read())
    f.close()
with open('pages/archive.html', 'r', encoding='utf-8') as f:
    archive_page = Template(f.read())
    f.close()


# 用于构建单张图片的 Detail 页面


def build_one(_pic):
    with open('build/%s.html' % _pic['PID'], 'w', encoding='utf-8') as _f:
        _f.write(detail_page.render(
            pic=_pic, sort=output_pics['sort_map'][_pic['TID']]))
        _f.close()
    with open('build/%s.json' % _pic['PID'], 'w', encoding='utf-8') as _f:
        _f.write(json.dumps(_pic))
        _f.close()


def build_archive(_pics, title, name):
    with open('build/%s.html' % name, 'w', encoding='utf-8') as _f:
        _f.write(archive_page.render(
            pics=_pics, sort=output_pics['sort_map'], title=title))
        _f.close()


# 获取分类
print('sorts')
# 记录开始时间
# noinspection PyTypeChecker
output_pics['info']['sort'] = {'all': {'start': get_time()}}
# 获取分类数据
sort = get_json('https://v2.api.dailypics.cn/sort')['result']
# 将分类数据存入字典
output_pics['sort'] = sort
# 初始化存储
output_pics['sort_map'] = {}
output_pics['archive'] = {}
# 打个输出，以免看着心慌
print(sort)
# 遍历分类
for v in sort:
    # 打个输出，以免看着心慌
    print(v)
    # 将 List 变为 Dict
    output_pics['sort_map'][v['TID']] = v
    # 初始化各分类归档
    output_pics['archive'][v['TID']] = []
    output_pics['info']['sort'][v['TID']] = {}
# 记录结束时间
# noinspection PyTypeChecker
output_pics['info']['sort']['all']['end'] = get_time()

# 获取今日
print('today')
# 记录开始时间
# noinspection PyTypeChecker
output_pics['info']['today'] = {}
# noinspection PyTypeChecker
output_pics['info']['today']['start'] = get_time()
# 获取今日
today = get_json('https://v2.api.dailypics.cn/today')
output_pics['today'] = []
# 处理今日
for v in today:
    print(v['PID'])
    v = get_info(v)
    output_pics['today'].append(v)
# 记录结束时间
# noinspection PyTypeChecker
output_pics['info']['today']['end'] = get_time()

# 是否咕咕咕
print('GuGuGu')
# 初始化 List
GuGuGu = []
GuGuGu_key = []
# 遍历今日图片
for v in output_pics['today']:
    # 判断是否咕咕咕并存储
    if v['p_date'] == date_today:
        v['if_today'] = True
    else:
        v['if_today'] = False
        # 记录咕咕咕的分类
        if not v['TID'] in GuGuGu_key:
            GuGuGu.append(output_pics['sort_map'][v['TID']])
            GuGuGu_key.append(v['TID'])
# 将咕咕咕的分类存入主 Dict
output_pics['not_updated'] = {'sort': GuGuGu}
# 输出可读的咕咕咕情况
print(GuGuGu)
if len(GuGuGu) == 0:
    GuGuGu_str = '所有分类均已更新'
elif len(GuGuGu) == len(sort):
    GuGuGu_str = '所有分类均未更新'
else:
    # 如果咕咕咕输出咕咕咕的分类
    GuGuGu_str = ','.join([v['T_NAME'] for v in GuGuGu]) + '没有更新'
# 将可读的咕咕咕情况存入主 Dict
# noinspection PyTypeChecker
output_pics['not_updated']['info'] = GuGuGu_str

# 单个分类
print('sort')
# 遍历所有分类
for v in sort:
    # 打个输出，以免看着心慌
    print(v['TID'])
    # 记录开始时间
    # noinspection PyTypeChecker
    output_pics['info']['sort'][v['TID']]['start'] = get_time()
    # 获取第一页和总页数
    first_page = get_json(
        'https://v2.api.dailypics.cn/list/?page=1&size=15&sort=%s' % v['TID'])
    # noinspection SpellCheckingInspection
    max_page = first_page['maxpage']
    # 打个输出，以免看着心慌
    print(max_page)
    # 遍历结果，存入主 Dict
    for pic in first_page['result']:
        output_pics['archive'][pic['TID']].append(pic)
    # 循环获取之后的个页
    for p in range(1, int(max_page)):
        page = p + 1
        this_page = get_json(
            'https://v2.api.dailypics.cn/list/?page=%s&size=15&sort=%s' % (page, v['TID']))['result']
        print(page)
        for pic in this_page:
            output_pics['archive'][pic['TID']].append(pic)
    # 记录结束时间
    # noinspection PyTypeChecker
    output_pics['info']['sort'][v['TID']]['end'] = get_time()

# 处理归档
for v in sort:
    pics = []
    for pic in output_pics['archive'][v['TID']]:
        print(pic['PID'])
        pic = get_info(pic)
        pics.append(pic)
    # noinspection PyTypeChecker
    output_pics['count'][v['TID']] = len(pics)
    output_pics['archive'][v['TID']] = pics
    if not v['TID'] in GuGuGu_key:
        output_pics['count'][v['TID']] += 1

output_pics['username'], output_pics['users'] = sort_dict(output_pics['users'], key=lambda _v: pinyin(_v[0]).lower())


def fix_asp(_v):
    asp = _v[0]
    if asp.index(':') == 1:
        asp = '0' + asp
    length = len(asp)
    if '.' in asp:
        length = asp.index('.') + 1
    if length - (asp.index(':') + 1) == 1:
        asp.replace(':', ':0')
    return asp


output_pics['asp'], output_pics['aspect_ratio'] = sort_dict(output_pics['aspect_ratio'], key=fix_asp)
output_pics['dates'], output_pics['date'] = sort_dict(output_pics['date'], True)

# 计算项目存活时间
start_time = datetime.datetime.strptime(output_pics['dates'][-1], '%Y-%m-%d').replace(tzinfo=pytz.timezone('PRC'))
output_pics['project_age'] = (beijing_time - start_time).days

# 记录结束时间
# noinspection PyTypeChecker
output_pics['info']['end'] = get_time()

print('output')

# 输出今日图片的 Detail 页面
for p in today:
    print(p['PID'])
    build_one(p)

# 输出所有图片的 Detail 页面
# 遍历所有分类
for v in sort:
    # 遍历归档
    for p in output_pics['archive'][v['TID']]:
        print(p['PID'])
        build_one(p)

# 输出主页
# 加载模板
with open('pages/home.html', 'r', encoding='utf-8') as f:
    index_page = Template(f.read())
    f.close()
# 输出主页
with open('build/index.html', 'w', encoding='utf-8') as f:
    f.write(index_page.render(pics=output_pics, not_updated=GuGuGu_str))
    f.close()

# 输出 JSON
# 输出今日图片
with open('build/today.json', 'w', encoding='utf-8') as f:
    build_archive(output_pics['today'], '今日', 'today')
    f.write(json.dumps(output_pics['today'], ensure_ascii=False))
    f.close()
# 输出分类
with open('build/sort.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['sort'], ensure_ascii=False))
    f.close()
# 输出转换后的分类
with open('build/sort2.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['sort_map'], ensure_ascii=False))
    f.close()
# 输出 Users
with open('build/username.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['username'], ensure_ascii=False))
    f.close()
with open('build/user-all.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['users'], ensure_ascii=False))
    f.close()
for v in output_pics['username']:
    with open('build/user-%s.json' % v, 'w', encoding='utf-8') as f:
        build_archive(output_pics['users'][v], v, 'user-' + v)
        f.write(json.dumps(output_pics['users'][v], ensure_ascii=False))
        f.close()

with open('build/date.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['dates'], ensure_ascii=False))
    f.close()
with open('build/date-all.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['date'], ensure_ascii=False))
    f.close()
for v in output_pics['date'].keys():
    with open('build/date-%s.json' % v, 'w', encoding='utf-8') as f:
        build_archive(output_pics['date'][v], v, 'date-' + v)
        f.write(json.dumps(output_pics['date'][v], ensure_ascii=False))
        f.close()
# 输出 纵横比
with open('build/asp.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['asp'], ensure_ascii=False))
    f.close()
with open('build/asp-all.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['aspect_ratio'], ensure_ascii=False))
    f.close()
for v in output_pics['aspect_ratio'].keys():
    with open(('build/asp-%s.json' % v).replace(':', '-'), 'w', encoding='utf-8') as f:
        build_archive(output_pics['aspect_ratio'][v],
                      v, ('asp-' + v).replace(':', '-'))
        f.write(json.dumps(output_pics['aspect_ratio'][v], ensure_ascii=False))
        f.close()
# 输出各分类归档
with open('build/sort-all.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['archive'], ensure_ascii=False))
    f.close()
for v in sort:
    # 输出归档
    with open('build/sort-%s.json' % v['TID'], 'w', encoding='utf-8') as f:
        build_archive(output_pics['archive'][v['TID']],
                      v['T_NAME'], 'sort-' + v['TID'])
        f.write(json.dumps(output_pics['archive'][v['TID']], ensure_ascii=False))
        f.close()
# 输出时间
with open('build/info.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['info'], ensure_ascii=False))
    f.close()
# 输出咕咕咕情况
with open('build/not_updated.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics['not_updated'], ensure_ascii=False))
    f.close()
# 输出主 Dict
with open('build/all.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_pics, ensure_ascii=False))
    f.close()

print('共进行%s次 HTTP 请求' % http_count)
