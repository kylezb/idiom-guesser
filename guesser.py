import os
import sqlite3
from time import sleep

import rich
from rich.console import Console
from rich.panel import Panel

from idioms2db import start, final, tones
from idioms2db_strict import start_s, final_s, tones_s


def get_sql(idiom, idiom_list=None, shengmu_list=None, yunmu_list=None, shengdiao_list=None, strict=True):
    if shengdiao_list is None:
        shengdiao_list = []
    if yunmu_list is None:
        yunmu_list = []
    if shengmu_list is None:
        shengmu_list = []
    if idiom_list is None:
        idiom_list = []
    if strict:
        shengmu = start_s(idiom)
        yunmu = final_s(idiom)
        shengdiao = tones_s(idiom)
    else:
        shengmu = start(idiom)
        yunmu = final(idiom)
        shengdiao = tones(idiom)
    cod = []
    if shengmu_list:
        for index, item in enumerate(shengmu_list):
            exclude = [1, 2, 3, 4]
            if item == 0:
                tmp = shengmu.copy()
                ind = []
                for i in range(shengmu.count(shengmu[index])):
                    a = tmp.index(shengmu[index])
                    tmp.pop(a)
                    ind.append(a + i)
                if shengmu.count(shengmu[index]) == 1 or len(set([shengmu_list[i] for i in ind])) == 1:
                    # 当所有声母都不同的时候才添加查询参数，避免出现互斥现象
                    # 当有声母相同的时候，如果均为0（不存在）则添加查询参数，避免出现互斥现象
                    cod.append(f's1 != "{shengmu[index]}"')
                    cod.append(f's2 != "{shengmu[index]}"')
                    cod.append(f's3 != "{shengmu[index]}"')
                    cod.append(f's4 != "{shengmu[index]}"')
                else:
                    cod.append(f's{index + 1} != "{shengmu[index]}"')

            if item == 1:
                cod.append(f's{index + 1} != "{shengmu[index]}"')
                exclude.remove(index + 1)
                cod2 = []
                for i in exclude:
                    cod2.append(f's{i} = "{shengmu[index]}"')
                a = ' or '.join(cod2)
                cod.append(f'({a})')

            if item == 2:
                cod.append(f's{index + 1} = "{shengmu[index]}"')
                if f's{index + 1} != "{shengmu[index]}"' in cod:
                    cod.remove(f's{index + 1} != "{shengmu[index]}"')
    if yunmu_list:
        for index, item in enumerate(yunmu_list):
            exclude = [1, 2, 3, 4]
            if item == 0:
                tmp = yunmu.copy()
                ind = []
                for i in range(yunmu.count(yunmu[index])):
                    a = tmp.index(yunmu[index])
                    tmp.pop(a)
                    ind.append(a + i)
                if yunmu.count(yunmu[index]) == 1 or len(set([yunmu_list[i] for i in ind])) == 1:
                    # 只有当所有韵母都不同的时候才添加查询参数，避免出现互斥现象
                    # 当有韵母相同的时候，如果均为0（不存在）则添加查询参数，避免出现互斥现象
                    cod.append(f'f1 != "{yunmu[index]}"')
                    cod.append(f'f2 != "{yunmu[index]}"')
                    cod.append(f'f3 != "{yunmu[index]}"')
                    cod.append(f'f4 != "{yunmu[index]}"')
                else:
                    cod.append(f'f{index + 1} != "{yunmu[index]}"')
            if item == 1:
                cod.append(f'f{index + 1} != "{yunmu[index]}"')
                exclude.remove(index + 1)
                cod2 = []
                for i in exclude:
                    cod2.append(f'f{i} = "{yunmu[index]}"')
                a = ' or '.join(cod2)
                cod.append(f'({a})')
            if item == 2:
                cod.append(f'f{index + 1} = "{yunmu[index]}"')
                if f'f{index + 1} != "{yunmu[index]}"' in cod:
                    cod.remove(f'f{index + 1} != "{yunmu[index]}"')

    if idiom_list:
        for index, item in enumerate(idiom_list):
            exclude = [1, 2, 3, 4]
            if item == 0:
                if idiom.count(idiom[index]) == 1:
                    cod.append(f'word not like "%{idiom[index]}%"')
            if item == 1:
                cod.append(f'w{index + 1} != "{idiom[index]}"')
                exclude.remove(index + 1)
                cod2 = []
                for i in exclude:
                    cod2.append(f'w{i} = "{idiom[index]}"')
                a = ' or '.join(cod2)
                cod.append(f'({a})')

            if item == 2:
                cod.append(f'w{index + 1} = "{idiom[index]}"')
                if f'w{index + 1} != "{idiom[index]}"' in cod:
                    cod.remove(f'w{index + 1} != "{idiom[index]}"')

    if shengdiao_list:
        for index, item in enumerate(shengdiao_list):
            if item == 0:
                cod.append(f't{index + 1} != "{shengdiao[index]}"')
            if item == 1:
                cod.append(f't{index + 1} != "{shengdiao[index]}"')
            if item == 2:
                cod.append(f't{index + 1} = "{shengdiao[index]}"')

    cod_sorted = list(set(cod))  # 去重
    cod_sorted.sort(key=cod.index)  # 按原列表排序
    return cod_sorted


def query(sql, echo=True):
    if echo:
        print(sql)
    conn = sqlite3.connect('idioms.sqlite')
    c = conn.cursor()
    c.execute(sql)
    idioms = c.fetchall()

    return idioms


def rich_input(msg, lst):
    while 1:
        console = Console()

        ctx = console.input(msg).strip()
        if ctx == '':
            ctx_list = [0, 0, 0, 0]
        else:
            if len(ctx) != 4:
                continue
            if not ctx.isdigit():
                continue
            ctx_list = ','.join(ctx).strip().split(',')
            ctx_list = list(map(int, ctx_list))
        if max(ctx_list) > 2 or min(ctx_list) < 0:
            continue
        # refer:https://www.freesion.com/article/7148743579/
        # refer:https://stackoverflow.com/questions/64388282/overwrite-input-line-on-python
        print('\033[1A' + '\033[K' + '\033[1A')
        rich.print(f"[red]{msg}[/red]", end="")
        colors = ["#9ba0a8", "#de7525", "#1d9c9c", ]  # 颜色分别对应0，1，2
        string = ''
        for index, item in enumerate(ctx_list):
            sleep(0.1)
            string = string + f" [{colors[item]}]{lst[index]}[/{colors[item]}]"
            length = 5 - len(str(lst[index]))
            if '\u4e00' <= str(lst[index]) <= '\u9fff':  # 汉字占2单位宽度
                length = 4 - len(str(lst[index]))
            console.print(f" [{colors[item]}]{lst[index]}[/{colors[item]}]" + ' ' * length, end="", )
        rich.print("\r")
        return ctx_list


def wordle(strict=True):
    condition = []
    idiom_list = []
    shengdiao_list = []

    os.system('cls')

    console = Console()
    console.print('帮    助: [#9ba0a8]0:不存在[/#9ba0a8] [#de7525]1:存在，位置不对[/#de7525] [#1d9c9c]2:存在，位置正确[/#1d9c9c] ',
                  '例如:[#9ba0a8]0[/#9ba0a8][#de7525]11[/#de7525][#1d9c9c]2[/#1d9c9c] 默认:[#9ba0a8]0000[/#9ba0a8]')
    console.print('[#8eaf44]推荐开局: [/#8eaf44][#7b963c]长治久安 一目了然 无可厚非 取而代之 排忧解难 举足轻重 统筹兼顾 热火朝天 顺理成章 死灰复燃 大江南北[/#7b963c]')
    idioms = []

    while 1:
        idiom = input('成    语: (输入成语继续，默认选择备选第一个，输入q重新开始): ')
        if idiom == '':
            if len(idioms) < 1:
                continue
            idiom = idioms[0][0]
        if idiom == 'q':
            os.system('cls')
            return wordle(strict)
        if len(idiom) != 4:
            continue

        if strict:
            shengmu = start_s(idiom)
            yunmu = final_s(idiom)
            shengdiao = tones_s(idiom)
        else:
            shengmu = start(idiom)
            yunmu = final(idiom)
            shengdiao = tones(idiom)
        print('\033[1A' + '\033[K' + '\033[1A')
        rich.print(f'[#f92b77]成    语: {idiom}[/#f92b77]')

        shengmu_list = rich_input('声母情况:', shengmu)
        yunmu_list = rich_input('韵母情况:', yunmu)

        if not strict:
            shengdiao_list = rich_input('声调情况:', shengdiao)
            idiom_list = rich_input('成语情况:', idiom)

        cod = get_sql(idiom=idiom, idiom_list=idiom_list, shengmu_list=shengmu_list, yunmu_list=yunmu_list,
                      shengdiao_list=shengdiao_list, strict=strict)
        condition += cod
        if strict:
            sql = 'select word,freq from STRICT where ' + str(' and '.join(condition)) + ' ORDER BY freq desc '
        else:
            sql = 'select word,freq from IDIOM where ' + str(' and '.join(condition)) + ' ORDER BY freq desc '

        idioms = query(sql, echo=False)
        # rich.print(f'匹配数量: {len(idioms)} 条',' '.join(str(i[0]) for i in idioms[:20]))
        rich.print(f'[#8eaf44]匹配数量: {len(idioms)} 条[/#8eaf44]\n'
                   f'[#8eaf44]备选成语: [/#8eaf44][#7b963c]{" ".join(str(i[0]) for i in idioms[:20])} [/#7b963c]')


if __name__ == '__main__':
    """
    0:不存在
    1:存在，位置不对
    2:存在，位置正确
    """
    try:
        os.system('cls')
        idiom_guesser = '''
          ___     _  _                                                 
         |_ _| __| |(_) ___  _ __    __ _  _  _  ___  ___ ___ ___  _ _ 
          | | / _` || |/ _ \| '  \  / _` || || |/ -_)(_-<(_-</ -_)| '_|
         |___|\__,_||_|\___/|_|_|_| \__, | \_,_|\___|/__//__/\___||_|  
                                    |___/                              
                                    '''
        p = '选择版本: \n1-->汉兜(https://handle.antfu.me/)  \n2-->拼成语(https://allanchain.github.io/chinese-wordle/)\n' \
            '项目地址:\nGitee:https://gitee.com/kylezb/idiom-guesser \tGithub:https://github.com/kylezb/idiom-guesser'
        rich.print(Panel(idiom_guesser, title="Idiom", subtitle="Guesser"))
        rich.print(Panel(p))

        a = input('请选择合适的版本，否则将难以得到准确答案:')
        if int(a) == 1:
            wordle(strict=False)
        if int(a) == 2:
            wordle()
    except Exception as e:
        print(e)
    input('按任意键退出')
