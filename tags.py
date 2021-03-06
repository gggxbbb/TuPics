import json
import jieba

input_pic = json.loads(open('build/all.json', 'r', encoding='utf-8').read())

tags = {}


def p_content(_pic):
    tag = jieba.cut(_pic['p_content'])
    for t in tag:
        if tags.get(t):
            if not _pic['PID'] in tags[t]:
                tags[t].append(_pic['PID'])
        else:
            tags[t] = [_pic['PID']]


for v in input_pic['today']:
    p_content(v)

for v in input_pic['sort_map']:
    for pic in input_pic['archive'][v]:
        p_content(pic)

with open('build/tags.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(tags, ensure_ascii=False))
    f.close()
