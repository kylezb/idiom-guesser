import os
import sqlite3
from idioms2db import start, final, tones
from idioms2db_strict import start_s, final_s, tones_s


def get_sql(idiom, idiom_list=[], shengmu_list=[], yunmu_list=[], shengdiao_list=[], strict=True):
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
            if item == 0:
                if idiom.count(idiom[index]) == 1:
                    cod.append(f'word not like "%{idiom[index]}%"')
            if item == 1:
                cod.append(f'w{index + 1} != "{idiom[index]}"')
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


def wordle(strict=True):
    condition = []
    idiom_list = []
    shengdiao_list = []

    print('帮助：(0:不存在  1:存在，位置不对  2:存在，位置正确)   例如：1201 默认：0000')

    while 1:
        idiom = input('成语：(在此输入四字成语继续，输入q重新开始)：')
        if idiom == 'q':
            os.system('cls')
            return wordle()
        if len(idiom) != 4:
            continue
        # print(idiom, py2_s(idiom))

        b = input('声母情况:')
        if b.strip() != '':
            shengmu_list = ','.join(b).strip().split(',')
            shengmu_list = list(map(int, shengmu_list))
            if max(shengmu_list) > 2 or min(shengmu_list) < 0:
                continue
            if len(shengmu_list) != 4:
                continue
        else:
            shengmu_list = [0, 0, 0, 0]

        c = input('韵母情况:')
        if c.strip() != '':
            yunmu_list = ','.join(c).strip().split(',')
            yunmu_list = list(map(int, yunmu_list))
            if max(yunmu_list) > 2 or min(yunmu_list) < 0:
                continue
            if len(yunmu_list) != 4:
                continue
        else:
            yunmu_list = [0, 0, 0, 0]
        if not strict:
            a = input('成语情况:')
            if a.strip() != '':
                idiom_list = ','.join(a).strip().split(',')
                idiom_list = list(map(int, idiom_list))
                if max(idiom_list) > 2 or min(idiom_list) < 0:
                    continue
                if len(idiom_list) != 4:
                    continue
            else:
                idiom_list = [0, 0, 0, 0]
        if not strict:

            d = input('声调情况:')
            if d.strip() != '':
                shengdiao_list = ','.join(d).strip().split(',')
                shengdiao_list = list(map(int, shengdiao_list))
                if max(shengdiao_list) > 2 or min(shengdiao_list) < 0:
                    continue
                if len(shengdiao_list) != 4:
                    continue
            else:
                shengdiao_list = []

        cod = get_sql(idiom=idiom, idiom_list=idiom_list, shengmu_list=shengmu_list, yunmu_list=yunmu_list,
                      shengdiao_list=shengdiao_list, strict=strict)
        condition += cod
        if strict:
            sql = 'select word,freq from STRICT where ' + str(' and '.join(condition)) + ' ORDER BY freq desc '
        else:
            sql = 'select word,freq from IDIOM where ' + str(' and '.join(condition)) + ' ORDER BY freq desc '

        idioms = query(sql, echo=False)
        print(f'匹配数量：{len(idioms)} 条', ' '.join(str(i[0]) for i in idioms[:20]))


if __name__ == '__main__':
    """
    0:不存在
    1:存在，位置不对
    2:存在，位置正确
    """
    try:
        print('选择版本：\n1-->汉兜(https://handle.antfu.me/)  2-->拼成语(https://allanchain.github.io/chinese-wordle/)')
        a = input('请选择合适的版本，否则将难以得到准确答案:')
        if int(a) == 1:
            wordle(strict=False)
        if int(a) == 2:
            wordle()
    except Exception as e:
        print(e)
    input('按任意键退出')
