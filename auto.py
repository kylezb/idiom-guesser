import os

from playwright.sync_api import Playwright, sync_playwright

from guesser import get_sql, query


def wordle(idiom, shengmu_list, yunmu_list, condition, strict=True):
    idiom_list = []
    shengdiao_list = []

    cod = get_sql(idiom=idiom, idiom_list=idiom_list, shengmu_list=shengmu_list, yunmu_list=yunmu_list,
                  shengdiao_list=shengdiao_list, strict=strict)
    condition += cod
    if strict:
        sql = 'select word,freq from STRICT where ' + str(' and '.join(condition)) + ' ORDER BY freq desc '
    else:
        sql = 'select word,freq from IDIOM where ' + str(' and '.join(condition)) + ' ORDER BY freq desc '

    idioms = query(sql, echo=False)
    return idioms, condition


def get_num_from_color(text):
    if 'gray' in text:
        return 0
    if 'yellow' in text:
        return 1
    if 'green' in text:
        return 2


def run(playwright: Playwright) -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    browser = playwright.chromium.launch_persistent_context(
        headless=False,
        channel="msedge",
        # 换成自己的用户目录,
        user_data_dir=os.path.join(current_dir, 'userdata'),
    )
    page = browser.new_page()
    # 默认创建2个窗口，关闭第一个空窗口
    browser.pages[0].close()

    # browser = playwright.chromium.launch(headless=False, channel="msedge")
    # context = browser.new_context()
    # page = context.new_page()

    page.goto("https://allanchain.github.io/chinese-wordle/")

    # page.locator("svg[role=\"img\"]").first.click()

    page.locator("input").click()

    def get_list(selector):
        aa = selector.query_selector_all('xpath=/div')
        shengmu_list = []
        yunmu_list = []
        for item in aa:
            w1 = item.query_selector('xpath=/div[1]/div[1]/div[1]').get_attribute('class')
            w2 = item.query_selector('xpath=/div[1]/div[1]/div[3]').get_attribute('class')
            shengmu_list.append(get_num_from_color(w1))
            yunmu_list.append(get_num_from_color(w2))
        return shengmu_list, yunmu_list

    while 1:

        word = '长治久安'
        page.locator("input").fill(word)
        page.locator("text=确认").click()

        condition = []
        for i in range(1, 9):

            if '你猜对了' in page.query_selector(f'xpath=//*').inner_text():
                print(666)
                page.wait_for_timeout(500)
                page.locator("svg[role=\"img\"]").first.click()
                page.locator("text=重开").click()
                break

            while 1:
                selector = page.query_selector(f'xpath=//*[@id="app"]/div/div[3]/div[{i}]')
                print(len(selector.inner_text()))
                if len(selector.inner_text()) > 4:
                    break
            selector = page.query_selector(f'xpath=//*[@id="app"]/div/div[3]/div[{i}]')

            shengmu_list, yunmu_list = get_list(selector)
            idioms, condition = wordle(word, shengmu_list, yunmu_list, condition)
            print(idioms[0][0])
            page.locator("input").fill(idioms[0][0])
            page.locator("text=确认").click()

            word = idioms[0][0]

    # context.close()
    # browser.close()


if __name__ == '__main__':
    with sync_playwright() as playwright:
        run(playwright)
