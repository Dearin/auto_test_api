# -*-coding: utf-8-*-
import sys,re

def lines(file):
    for line in file:
        yield line
        yield '\n'

def blocks(file):
    block = []
    for line in lines(file):
        if line.strip():
            block.append(line)
        elif block:
            yield ''.join(block).strip()
            block=[]

if __name__ == '__main__':   
    print('<html><body>')
    title = True
    for block in blocks(sys.stdin):
        block = re.sub(r'\*(.+?)\*',r'<em>\1</em>',block)
        if title:
            print('<h1>')
            print(block)
            print('</h1>')
            title = False
        else:
            print('<p>')
            print(block)
            print('</p>')
    print('</body></html>')
