import json
import sqlite3
from pypinyin import pinyin, Style


def ct_table():
    conn = sqlite3.connect('idioms.sqlite')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS STRICT(
           ID INT PRIMARY KEY     NOT NULL,
           word           char(4)    NOT NULL,
           pinyin           char(40)    NOT NULL,
           pinyin2           char(40)    NOT NULL,
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
    c.execute('delete from STRICT ')
    with open('idiom.json', mode='r', encoding='utf-8') as f:
        idoms = json.load(f)
    for index, idom in enumerate(idoms):
        w = idom[0]
        # print(w, py(w), start(w), final(w), tones(w), )

        print(f'''
          {index + 1},{w},{py(w)},{py2_s(w)},{freq(w)},{w[0]},{w[1]},{w[2]},{w[3]},{start_s(w)[0]},{start_s(w)[1]},{start_s(w)[2]},{start_s(w)[3]},{final_s(w)[0]},{final_s(w)[1]},{final_s(w)[2]},{final_s(w)[3]},{tones_s(w)[0]},{tones_s(w)[1]},{tones_s(w)[2]},{tones_s(w)[3]}
          ''')
        c.execute('''INSERT INTO STRICT (id, word, pinyin,pinyin2,freq, w1, w2, w3, w4, s1,s2, s3, s4, f1, f2, f3, f4,t1, t2,t3,t4)
          VALUES ( ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (index + 1, w, py(w), py2_s(w), freq(w), w[0], w[1], w[2], w[3], start_s(w)[0], start_s(w)[1],
                   start_s(w)[2],
                   start_s(w)[3],
                   final_s(w)[0], final_s(w)[1], final_s(w)[2], final_s(w)[3], tones_s(w)[0], tones_s(w)[1],
                   tones_s(w)[2],
                   tones_s(w)[3]))
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


def py2_s(word):
    py = pinyin(word, style=Style.NORMAL, )
    idiom_py = ''
    for p in py:
        idiom_py = idiom_py + ' ' + p[0]
    return idiom_py.strip()


def start_s(word):
    py = pinyin(word.strip(), style=Style.INITIALS)
    start = []
    for i, p in enumerate(py):
        if p[0]:
            start.append(p[0])
        else:
            start.append('Ø')
    return start


def final_s(word):
    py = pinyin(word.strip(), style=Style.FINALS)
    final = []
    for p in py:
        final.append(p[0])
    return final


def tones_s(word):
    py = pinyin(word.strip(), style=Style.TONE3, neutral_tone_with_five=True)
    tones = []
    for p in py:
        if int(p[0][-1]) == 5:
            tones.append(1)
        else:
            tones.append(int(p[0][-1]))
    return tones


if __name__ == '__main__':
    insert_table()
