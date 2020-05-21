import json
import jieba

input_pic = json.loads(open('build/all.json','r',encoding='utf-8').read())

tags = {}

def p_content(pic):
    tag = jieba.cut(pic['p_content'])
    for t in tag:
        if tags.get(t):
            if not pic['PID'] in tags[t]:
                tags[t].append(pic['PID'])
        else:
            tags[t] = [pic]

for v in input_pic['today']:
    p_content(v)

for v in input_pic['sort_map']:
    for pic in input_pic['archive'][v]:
        p_content(pic)

with open('build/tags.json','w',encoding='utf-8') as f:
    f.write(json.dumps(tags,ensure_ascii=False))
    f.close()
