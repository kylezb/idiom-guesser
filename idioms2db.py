import json
from pypinyin import pinyin, Style
import sqlite3


def ct_table():
    conn = sqlite3.connect('idioms.sqlite')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS IDIOM(
           ID INT PRIMARY KEY     NOT NULL,
           word           char(4)    NOT NULL,
           pinyin         char(40)    NOT NULL,
           pinyin2        char(40)    NOT NULL,
           freq           int    ,
           
           w1          char(1)    NOT NULL,
           w2          char(1)    NOT NULL,
           w3          char(1)    NOT NULL,
           w4          char(1)    NOT NULL,
           s1          char(1)    NOT NULL,
           s2          char(1)    NOT NULL,
           s3          char(1)    NOT NULL,
           s4          char(1)    NOT NULL,
           f1          char(10)    NOT NULL,
           f2          char(10)    NOT NULL,
           f3          char(10)    NOT NULL,
           f4          char(10)    NOT NULL,
           t1          int(1)    NOT NULL,
           t2          int(1)    NOT NULL,
           t3          int(1)    NOT NULL,
           t4          int(1)    NOT NULL);
           ''')
    conn.commit()
    conn.close()


def insert_table():
    ct_table()
    conn = sqlite3.connect('idioms.sqlite')
    c = conn.cursor()
    c.execute('delete from IDIOM ')
    with open('idiom.json', mode='r', encoding='utf-8') as f:
        idoms = json.load(f)
    for index, idom in enumerate(idoms):
        w = idom[0]
        # print(w, py(w), start(w), final(w), tones(w), )

        print(f'''
          {index + 1},{w},{py(w)},{py2(w)},{freq(w)},{w[0]},{w[1]},{w[2]},{w[3]},{start(w)[0]},{start(w)[1]},{start(w)[2]},{start(w)[3]},{final(w)[0]},{final(w)[1]},{final(w)[2]},{final(w)[3]},{tones(w)[0]},{tones(w)[1]},{tones(w)[2]},{tones(w)[3]}
          ''')
        c.execute('''INSERT INTO IDIOM (id, word, pinyin,pinyin2,freq, w1, w2, w3, w4, s1,s2, s3, s4, f1, f2, f3, f4,t1, t2,t3,t4)
          VALUES ( ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (index + 1, w, py(w), py2(w), freq(w), w[0], w[1], w[2], w[3], start(w)[0], start(w)[1], start(w)[2],
                   start(w)[3],
                   final(w)[0], final(w)[1], final(w)[2], final(w)[3], tones(w)[0], tones(w)[1], tones(w)[2],
                   tones(w)[3]))
    conn.commit()
    print("数据插入成功")
    conn.close()


def freq(idiom):
    with open('idiom_frq.json', mode='r', encoding='utf-8') as f:
        idiom_freq: dict = json.load(f)
    freq = idiom_freq.get(idiom, 0)
    return freq


def w2p():
    with open('idiom.json', mode='r', encoding='utf-8') as f:
        idoms = json.load(f)
    for idom in idoms:
        print(idom[0], pinyin(idom[0]))


def py(word):
    py = pinyin(word)
    idiom_py = ''
    for p in py:
        idiom_py = idiom_py + ' ' + p[0]
    return idiom_py.strip()


def py2(word):
    py = pinyin(word, style=Style.NORMAL, strict=False)
    idiom_py = ''
    for p in py:
        idiom_py = idiom_py + ' ' + p[0]
    return idiom_py.strip()


def start(word):
    py = pinyin(word.strip(), style=Style.INITIALS, strict=False)
    start = []
    for i, p in enumerate(py):
        if p[0]:
            start.append(p[0])
        else:
            a = pinyin(word.strip()[i], style=Style.FIRST_LETTER, strict=False)
            if a[0][0] in ['e', 'a']:
                start.append('Ø')
            else:
                start.append(a[0][0])
    return start


def final(word):
    py = pinyin(word.strip(), style=Style.FINALS, strict=False)
    final = []
    for p in py:
        final.append(p[0])
    return final


def tones(word):
    py = pinyin(word.strip(), style=Style.TONE3, strict=False, neutral_tone_with_five=True)
    tones = []
    for p in py:
        if int(p[0][-1]) == 5:
            tones.append(1)
        else:
            tones.append(int(p[0][-1]))
    return tones


if __name__ == '__main__':
    insert_table()
