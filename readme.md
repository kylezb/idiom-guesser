
## 让我们开始！

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


|*|程序|结果      |
| ----| ---- | ---- |
|[汉兜](https://handle.antfu.me)|![ex1](./img/ex1.png) | ![ex2](./img/ex2.png) |
|[拼成语](https://allanchain.github.io/chinese-wordle/)|![ex3](./img/ex3.png) | ![ex4](./img/ex4.png) |

## 更多
基于[Playwright](https://playwright.dev/) 的自动化 ~~无情的~~ 猜成语机器
![gif1](./img/gif1.gif) 
使用idiom-guesser基本能在3-4次内猜出成语
![ex5](./img/ex5.png) 
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


