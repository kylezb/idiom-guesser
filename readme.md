## 介绍：
这是一个用于解决类似[汉兜](https://handle.antfu.me)、[拼成语](https://allanchain.github.io/chinese-wordle/) 这类应用的程序

## 目录结构
```
├─requirements.txt      依赖
├─auto.py               自动猜成语
├─guesser.py            主程序
├─idiom.json            原始成语数据
├─idiom_freq.json       成语频率数据
├─idioms.sqlite         成语数据库
├─idioms2db.py          生成成语数据库（非严格模式）
├─idioms2db_strict.py   生成成语数据库（严格模式）
├─img                   md_img
└─userdata              自定义用户文件夹
```

## 使用说明
运行 `guesser.py`

>  如果你猜的成语中某一个声母或韵母(对于汉兜来说，还包含汉字与音调)：
>  - 位置与待猜成语相同，它就会被标成绿色，我们用 **2** 来表示
>  - 出现在待猜成语中但位置错误，就是黄色，我们用 **1** 来表示
>  - 压根没出现在待猜成语中，就是灰色，我们用 **0** 来表示
>
> 根据上述规则，以汉兜为例：输入 `无忧无虑` 得到4个字对应的声母、韵母等情况
>
>  - 声母应该为 `0000`，由于默认是 `0000`，我们可以不填
>  - 韵母应该为 `0100`
>  - 汉字应该为 `0000`，由于默认是 `0000`，不填
>  - 声调应该为 `0100`
>
> 敲下回车后会返回匹配的条目数以及出现频率最高的前20个成语备选
> 重复上述操作，应该会在3-4次内得到答案 

|*|程序|结果|
| ----| ---- | ---- |
|[汉兜](https://handle.antfu.me)|![ex1](./img/ex1.png) | ![ex2](./img/ex2.png) |
|[拼成语](https://allanchain.github.io/chinese-wordle/)|![ex3](./img/ex3.png) | ![ex4](./img/ex4.png) |

## 更多
基于[Playwright](https://playwright.dev/) 的自动化 ~~无情的~~ 猜成语机器
![gif1](./img/gif1.gif) 
使用idiom-guesser基本能在3-4次内猜出成语

![ex5](./img/ex5.png) 
5000次的数据，应该有较强的参考性

### 注意
使用下列代码将启用浏览器无痕模式

```
    browser = playwright.chromium.launch(headless=False, channel="msedge")
    context = browser.new_context()
    page = context.new_page()
```
若不想以无痕模式启动，使用下列代码
详见[playwright官网](https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch-persistent-context)
```   
    browser = playwright.chromium.launch_persistent_context(
        headless=False,
        channel="msedge",
        # 换成自己的用户目录,
        user_data_dir='D:/path/to/userdata',
    )
    page = browser.new_page()
```

