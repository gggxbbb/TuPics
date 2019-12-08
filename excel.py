import json

import xlwt

input_pics = json.loads(open('build/all.json', 'r', encoding='utf-8').read())

output_pics = []

for pic in input_pics['today']:
    if not pic['TID'] in [v['TID'] for v in input_pics['not_updated']['sort']]:
        output_pics.append(pic)
    output_pics += input_pics['archive'][pic['TID']]

output_table = []
output_table.append([
    '标题', 
    'ID', 
    '类别', 
    '日期',
    '介绍', 
    '上传者', 
    '地址', 
    '原始地址', 
    '主题色', 
    '文本建议色',
    '永久地址'
    ])
for pic in output_pics:
    output_table.append([
        pic['p_title'], 
        pic['PID'], 
        input_pics['sort_map'][pic['TID']]['T_NAME'], 
        pic['p_date'],
        pic['p_content'], 
        pic['username'], 
        pic['local_url'], 
        pic['p_link'], 
        pic['theme_color'], 
        pic['text_color'],
        'https://www.dailypics.cn/member/id/'+pic['PID']
        ])


output_book = xlwt.Workbook()

output_table_info = output_book.add_sheet('信息')

output_table_info.write(0,1,'开始时间')
output_table_info.write(0,2,'结束时间')

output_table_info.write(1,0,'总体')
output_table_info.write(1,1,input_pics['info']['start'])
output_table_info.write(1,2,input_pics['info']['end'])

output_table_info.write(2,0,'今日')
output_table_info.write(2,1,input_pics['info']['today']['start'])
output_table_info.write(2,2,input_pics['info']['today']['end'])

output_table_info.write(3,0,'归档')
output_table_info.write(3,1,input_pics['info']['sort']['all']['start'])
output_table_info.write(3,2,input_pics['info']['sort']['all']['end'])

output_table_pic = output_book.add_sheet('归档')

row = 0
for pic in output_table:
    col = 0
    for v in pic:
        output_table_pic.write(row, col, v)
        col += 1
    row += 1

output_book.save('build/Tujian.xls')
