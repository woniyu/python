#template.py
#coding=utf-8
import fileinput,re

#匹配中括号里的字段：
field_pat = re.compile(r'\[(.+?)\]')

#我们将变量收集到这里
scope={}

#用于re.sub中
def replacement(match):
    code = match.group(1)
    try:
        #如果字段可以求职，返回他
        return str(eval(code,scope))
    except SyntaxError:
        exec code in scope
        #…………返回空字符串
        return ''

#将所有文本以一个字符串的形式获取
lines = []

for line in fileinput.input():
    lines.append(line)

text = ''.join(lines)

#将field模式的所有匹配项都替换掉：
print field_pat.sub(replacement(),text)
