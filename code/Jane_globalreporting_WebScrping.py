from pyquery import PyQuery as pq
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep

browser = webdriver.Chrome()
browser.get('https://database.globalreporting.org/search/')

# TODO 1: search for african companies

# click region
button1 = browser.find_element_by_css_selector('body > div > section > div:nth-child(3) > div > div:nth-child(4) > div > div > button')
button1.click()
# click africa
button2 = browser.find_element_by_css_selector('body > div > section > div:nth-child(3) > div > div:nth-child(4) > div > div > div > ul > li:nth-child(1) > a')
button2.click()
# click search
button3 = browser.find_element_by_css_selector('#home-search-text')
button3.click()
WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "total-time")))


# Todo 2: collect information
org, orglink, sz, sec, cty, reg, repo = [], [], [], [], [], [], []


for i in range(72): # 71
    sleep(0.5)
    doc = pq(browser.page_source)
    items = doc('tbody tr').items()
    for item in items:
        name = str(item('tr td h4 a').text())
        name_url = 'https://database.globalreporting.org' + item('tr td h4 a').attr('href')
        size = item('tr > td:nth-child(2)').text()
        sector = item('tr > td:nth-child(3)').text()
        country = item('tr > td:nth-child(4) > img').attr('src')[-6:-4]
        region = item('tr> td:nth-child(5)').text()
        report = []
        reports = item('tr > td:nth-child(6) a').items()
        for r in reports:
            year = r('a span:nth-child(1)').text()
            # label = r('a span:nth-child(2)').text()
            url = 'https://database.globalreporting.org' + r('a').attr('href')
            report.append(year+': '+url)
        org.append(name)
        orglink.append(name_url)
        sz.append(size)
        sec.append(sector)
        cty.append(country)
        reg.append(region)
        repo.append(report)
    sleep(0.5)
    # don't click last page
    if i == 71:
        break
    WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="results-datatable_next"]/a'))).click()
    sleep(0.5)


df = pd.DataFrame({'ORG Name': org, 'ORG Link': orglink, 'Size':sz, 'Sector': sec, 'Country': cty, 'Region': reg, 'Report':repo})
df.to_csv('draft.csv')
print(df)
