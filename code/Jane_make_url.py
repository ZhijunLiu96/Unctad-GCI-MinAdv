import ast
import re
import pandas as pd
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


def generate_download_url(url):
    url = re.sub('report-covers','report-pdfs',url)
    url = re.sub('/profile.jpg','.pdf',url)
    result = re.search('(.*?AWSAccessKeyId.*?AKIAJZQ4KYD2D35QKCDA).*?',url,re.S)
    return result.group(1)


def get_token(urls):
    names, links = [], []
    for url in urls:
        try:
            result = re.search('(\d.*?)\:\s(http.*?$)', url, re.S)
            name = result.group(1)
            link = result.group(2)
            browser = webdriver.Chrome()
            browser.set_window_size(50, 100)
            browser.get(link)
            doc = pq(browser.page_source)
            # while True:
            #     sleep(0.5)
            #     if EC.visibility_of_element_located(By.CSS_SELECTOR, "body"):
            #         break
            #     else:
            #         browser.refresh()
            #         doc = pq(browser.page_source)
            browser.close()
            # get the token
            text = doc('body > div > div > div.col-md-4 > img').attr('src')
            link = generate_download_url(text)
            file_name = re.search('.*?report-pdfs(.*?pdf.*?)AWSAccessKeyId.*?', link, re.S)
            file_name = file_name.group(1)
            file_name = file_name[6:-1]
            names.append(name + '' + file_name)
            links.append(link)
        except: pass
    return names, links



if __name__ == "__main__":
    df = pd.read_csv('draft.csv')
    df['download'] = [[]]*len(df)
    for i in range(554, len(df)):
        df['Report'][i] = ast.literal_eval(df['Report'][i])
        df['Report'][i], df['download'][i] = get_token(df['Report'][i])
        print(i)
        df.to_csv('download.csv', index=False)
    print('Successfully scraped all file links!')
