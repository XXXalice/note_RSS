import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import feedgenerator

def main():
    '''メインの処理'''
    driver = webdriver.PhantomJS()
    #phantomjsのウィンドウサイズを設定
    driver.set_window_size(800, 600)
    navigate(driver)
    screen_shot(driver)
    posts = scrape_posts(driver)
    with open('rss/recommend.rss','w') as f:
        save_as_feed(f, posts)

def navigate(driver):
    '''目的のページに遷移させる関数'''
    #file=sys.stderrは標準エラー出力
    print('Navigating...', file=sys.stderr)
    driver.get('https://note.mu/')
    try:
        assert 'note' in driver.title
    except AssertionError as ass:
        print('AssertionError:', ass)
    else:
        print('title:', driver.title)
        time.sleep(3)
        #ページの一番下までスクロールする execute_script()でjsのコードが実行できる
        driver.execute_script('scroll(0, document.body.scrollHeight)')
        print('waiting for contents to be loaded...', file=sys.stderr)
        time.sleep(2)
        #二回め
        driver.execute_script('scroll(0, document.body.scrollHeight)')
        #10秒でタイムアウトするWebDriverWaitオブジェクトを作成する
        wait = WebDriverWait(driver, 10)
        print('Waiting for the more button to be clickable...',file=sys.stderr)
        #もっとみる　ボタンがクリック可能になるまで待つ。
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn.btn-more.fl-c')))
        button.click()
        time.sleep(3)

def scrape_posts(driver):
    '''文章コンテンツのURL、タイトル、概要を含むdictのリストを取得する'''
    posts = []

    for a in driver.find_elements_by_css_selector('a.p-post--basic'):
        posts.append({
            'url': a.get_attribute('href'),
            'title': a.find_element_by_css_selector('h4.c-post__title').text,
            'description': a.find_element_by_css_selector('div.c-post__description').text
        })

    return posts

def save_as_feed(file, posts):
    '''文章コンテンツのリストをフィードとして保存する'''
    feed = feedgenerator.Rss201rev2Feed(
        title='おすすめノート',
        link='https://note.mu/',
        description='おすすめノート'
    )

    for post in posts:
        #フィードにアイテムを追加する
        feed.add_item(title=post['title'],
                      link=post['url'],
                      description=post['description'],
                      #idを指定しておくとRSSリーダーがアイテムの重複なく使える
                      unique_id=post['url']
                      )
        #ファイルオブジェクトに書き込む。第二引数にエンコーディングを指定する。
        feed.write(file, 'utf-8')

def screen_shot(driver):
    driver.save_screenshot('img/note.png')

if __name__ == '__main__':
    main()