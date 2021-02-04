[<img src="figure/gai.png" align="right">](https://www.globalai.co)

-------

# Unctad GCI MinAdv

Our goal is to analyze South African companies' yearly reports on the two websites, globalreporting.org and unglobalcompact.org.

The web scraping and part of the text extraction were finished. I also wrote some instruction and provided coded and examples for future steps.

# Contents
- **[Done] [Obtain External Data](#external)**
    - **[unglobalcompact.org](#ungc)**
    - **[globalreporting.org](#report)**
- **[Future Step] [Text Extraction](#text)**
    - **[Done][unglobalcompact](#ungc-text)**
    - **[Pending][globalreporting](#report-text)**
    - **[Previous Work](#prev)**
- **[Future Step] [Keywords Extraction](#keywords)**
    - **[Rules](#rule)**
    - **[Example][Extraction Function](#function)**
- **[Future Step] [Calculate Scores](#analytics)**
- **[Future Step] [Visualize Trend](#trend)**
    - **[Trend of thresholds](#threshold)**
    - **[Visualize the distribution](#distribution)**
    - **[Trend of indcator](#indicator)**
    - **[Trend of category](#category)**
    - **[Trend of region](#region)**
- **[Reference](#reference)**

----

# Obtain External Data <a id="external"></a>

- The two websites needs different web scraping techniques to get the metadata and download the report.
- Check current progress in the Google Drive Folder: https://drive.google.com/drive/folders/17Q0zgOgYiPjKl3dXW04JtqyWPjN06qFw
## Unglobal Compact <a id="ungc"></a>
- Target Link: https://unglobalcompact.org/what-is-gc/participants/search?search%5Bcountries%5D%5B%5D=224
- All pdf files are downloaded to the Google Drive Folder: https://drive.google.com/drive/folders/1m0db_NkRBRclQWOQ1PvNfeYCYyqMdp9j

<br>

**1. Meta data** 

Check the [unglobalcompact_metadata_Scape.py](code/Jane_unglobalcompact_metadata_Scape.py
) to scrape the meta data, and see the result to the file [unglobalcompact_metadata.csv](data/unglobalcompact_metadata.csv)
```python
from pyquery import PyQuery as pq
import pandas as pd

def parse_one_page(doc):
    items = doc('body tr').items()
    for item in items:
        name = item('tr .name a').text()
        Type = item('tr .type').text()
        sector = item('tr .sector').text()
        country = item('tr .country').text()
        join = item('tr .joined-on').text()
        nameL.append(name)
        typeL.append(Type)
        sectorL.append(sector)
        countryL.append(country)
        joinL.append(join)

nameL, typeL, sectorL, countryL, joinL = [],[],[],[],[]
for i in range(1,8):
    url = 'https://unglobalcompact.org/what-is-gc/participants/search?page='+str(i)+'&search%5Bcountries%5D%5B%5D=224'
    doc = pq(url)
    parse_one_page(doc)
    print(i)
df = pd.DataFrame({'Name':nameL,'Type':typeL,'Sector':sectorL,'Country':countryL,'Joined On':joinL})
df = df[df.Type != 'Type']
df.to_csv('unglobalcompact_metadata.csv', index=False)
```

<img src="figure/ungc_meta.png">

<br>

<br>

**2. Download Reports**

Check the Code [Zian_Zhang_web_unglobalcompact.ipynb](code/Zian_Zhang_web_unglobalcompact.ipynb)
- Firstly it saves urls to the file [download_url_file.csv](data/download_url_file.csv)
- Then download all pdfs

```python
import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import pandas as pd
import urllib.request as urllib2

filename = 'download_url_file.csv'
f = open(filename, 'w')
headers = 'Name,url\n'
f.write(headers)

for i in range(1,8):
    my_url = 'https://unglobalcompact.org/what-is-gc/participants/search?page=' + str(i) + '&search%5Bcountries%5D%5B%5D=224'
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()

    page_soup = soup(page_html, 'html.parser')
    table = page_soup.body.main.section.div.table.findAll('tr')
    
    for i in table:
        try:
            Name = i.th.a.text.strip()
        
            url = 'https://unglobalcompact.org' + i.th.a.attrs["href"]
        
            f.write(Name + ',' + url + '\n')
        except:
            continue
f.close()

def download_file(download_url, filename):
    response = urllib2.urlopen(download_url)
    file = open(filename + '.pdf', 'wb')
    file.write(response.read())
    file.close()

df_url = pd.read_csv('download_url_file.csv')
count = 0
for index, row in df_url.iterrows():
    try:
        source_url = row['url']
        org_name = row['Name']
        uClient = uReq(source_url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, 'html.parser')
    
        download_url = 'http:' + page_soup.body.main.section.div.section.findAll('a', {'target' : '_blank'})[0].attrs["href"]
        
        download_file(download_url,org_name)
        
        count += 1
        
    except:
        print('Download failed: ' + org_name)
        continue

print('Successfully downloaded ' + str(count) + ' files') 
```

## Global Reporting <a id="report"></a>
This website can only use **selenium** to scrape
- Target Link: https://database.globalreporting.org/search/
- All pdf files are downloaded to the Google Drive Folder: https://drive.google.com/drive/folders/1PhP6qipqh9rMlOfKxreFdFzmnxksTskc

<br>

**1. Meta data**
- Code: [Jane_globalreporting_WebScrping.py](code/Jane_globalreporting_WebScrping.py)
- Meta data: [draft.csv](data/draft.csv)
- Meta data 2 (with modified urls): [download.csv](data/download.csv)

**Step 1**: Install packages ```pyquery``` and ```selenium```. Also, you need to download a ```webdriver```.
```python
from pyquery import PyQuery as pq
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
```
**Step 2**: Since only a subset is required, we need to add some filter. Simulate opening a browser, and clicking three buttons sequentially: region, Africa, and search.

<img src='figure/button.png'>

```python
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
```
**Step 3**: Use PyQuery to parse the page_source, and simulate clicking the 'next page' button

<img src="figure/web.png">

```python
# TODO 2: collect information
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
```
**Step 4**: Finally, save all data to [draft.csv]("data/draft.csv)

<img src="figure/draft.png"> 

Notes:
- Column Country is the two-digit ISO code
- Column Reoort is a list of report links for each year

<br>

**2. Download Reports**
- Code to Modify report pages to download pages: [Jane_make_url.py](code/Jane_make_url.py)
- Code to download pdfs to Google Drive Folder: [Jane_downloadToDrive.ipynb](code/Jane_downloadToDrive.ipynb)

<br>

**Step 1: Deal with the robot check**

- If we go to the download page and click the download button, we need to pass the Captcha, which is a challenge for web crawlers. But in this case, I found a way to avoid this problem.

<img src="figure/check.png">

- If we open the pdf file, the download link is as follow:
```
https://sdd-pdf.s3.amazonaws.com/report-pdfs/2014/name.pdf?AWSAccessKeyId=key&Expires=1598662304&Signature=L1Vc5az2kDV%2BfjstZEtCVXzZy3w%3D
```
- Let's try to search for the AWSAccessKey on the web script. 

<img src="figure/token.png">

- Just make a little bit modification!

<img src='figure/modify.png'>

<br>
<br>
<br>

**Step 2: Code to implement the method**

```python
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
```

**Step 3: Download to Google Drive**
```python
from google.colab import drive
drive.mount('/content/drive/')
```
```python
cd 'drive/My Drive/pdf'
```
```python
import ast
import requests
import pandas as pd

def download(url):
    r = requests.get(url, stream=True)
    name = url[50:-36]
    path = 'data/'+name
    with open(path, 'wb') as f:
        f.write(r.content)

data = pd.read_csv('download.csv')
urls_all = list(data['download'])

for i in range(len(urls_all)):
    urls = ast.literal_eval(urls_all[i])
    for url in urls:
        try:
            download(url)
        except: print('error')
    print(i+1)
```


# Text Extraction <a id="text"></a>
Currently, we have extracted the text for files downloaded from UN Global Compact.

- Code: [Jane_read_text.py](code/Jane_read_text.py)
- Result: [ungc_result.csv](data/ungc_result.csv)
## Text Extraction for Global Compact <a id="ungc-text"></a>
- Use ```pdf2text_and_numpage()``` to extact the text and page number for each file
- Use ```clean_text()``` to clean the extracted text 
```python
import glob
import os
import textract
import PyPDF2
import re
import pandas as pd

def clean_text(text):
    text = re.sub("b'", ' ', text)
    text = re.sub(r"\\n|\\\w+\d+|\\\w+", ' ', text)
    text = re.sub("^\s|\s$", '', text)
    text = re.sub("\s+", ' ', text)
    text = re.sub("\.+", '.', text)
    return text

def pdf2text_and_numpage(filename):
    pdfFileObj = open(filename,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    num_pages = pdfReader.numPages
    count = 0
    text = ""
    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count += 1
        text += pageObj.extractText()
    return (str(textract.process(filename, method='tesseract')), num_pages)


if __name__=="__main__":
    current = os.getcwd()
    os.chdir('pdf')
    filenames = [x for x in glob.glob('*')]
    data = pd.DataFrame(columns=['file name', 'page number', 'text'])

    for file in filenames:
        try:
            text, num = pdf2text_and_numpage(file)
            row = row = {"file name": file, "page number": num, "text": clean_text(text)}
        except:
            row = row = {"file name": file, "page number": None, "text": None}
        data = data.append(row, ignore_index=True)

    os.chdir(current)
    data.to_csv("ungc_result.csv")
```

## (Pending) Text Extraction for Global Reporting <a id="report-text"></a>
> This part will be very similar to the **Text Extraction for Global Compact**. <br>
> Attention: 
>
> - You might need to select files under the South Afirca category,  
> - You can extact the text and save to a dataframe with two columns ("file name", "extracted text"), use the following code to parse the [download.csv](data/download.csv), and match the company.

You can use the code to parse each row to the following JSON format.
```python
df = pd.read_csv('download.csv')
for i in range(len(df)):
    row = dict()
    row["_id"] = i+1
    repoList = []
    repo = list(df['Report'])[i]
    for file in ast.literal_eval(repo):
        instance = dict()
        instance["Year"] = file[:4]
        type_ = file[6:-36]
        type_ = type_[:len(type_)//2]
        instance["Type"] = type_
        file_name = file[-36:]
        instance["File"] = file_name
        repoList.append(instance)
    row['Reports'] = repoList
    co = dict()
    co['Name'] = list(df['ORG Name'])[i]
    co['Page'] = list(df['ORG Link'])[i]
    co['Size'] = list(df['Size'])[i]
    co['Sector'] = list(df['Sector'])[i]
    row['Company'] = co
    region = dict()
    region['Region'] = list(df['Region'])[i]
    region['alpha2'] = list(df['Country'])[i].upper()
    row['Region'] = region
```
Here is how each row looks like:
```
{'_id': 1,  
 'Company': 
    {'Name': '1time', 
     'Page': 'https://database.globalreporting.org/organizations/4821/', 
     'Size': 'Large', 
     'Sector': 'Logistics'}, 
 'Reports': 
    [{'Year': '2012', 'Type': ' Non - GRI', 'File': '8d5b7751288d013ce932b983f305051b.pdf'}, 
     {'Year': '2011', 'Type': ' Non - GRI', 'File': 'b233f59e19db460a8ae2eec256e4bf83.pdf'}],
 'Region': {'Region': 'Africa', 'alpha2': 'ZA'}}
```


## Previous Work for Reference <a id="prev"></a>
You can check the previous work in the [UNGC repository](https://github.com/globalaiorg/PROJECT-UNGC-COPS) (https://github.com/globalaiorg/PROJECT-UNGC-COPS.git) **(ask for permission)**, including:

- Extact text from different file formats (pdf, ppt, docx)
- Parallel processing


# Keywords Extraction <a id="keywords"></a>
In this part, we need to evaluate reports base on the rules we set up. Version I and II are old versions. 

For example, in our [old rule](rule/wikirate_indicator_version1.txt), there is a indicator **A.3.1** under the category **environment**, and it corresponding keywords are **expenditure, investment, cost, pay, and paid**. 

- We use **completeness** to measure each indicator
- If the report **doesn't mention** any of the keywords of a given indicator, we say the **completeness** of this indicator is **0**
- If the report only mentioned one or more keywords, but **without corresponding number**, we say the **completeness** of this indicator is **1**
- If the report mentions **both keywords and corresponding number**, we say its completeness is **2** 
- **Example**: CO2 emission is 200 tons. **Emission** is a keyword and **200** is the corresponding number

<img src="figure/rule.png">

## Rules  <a id="rule"></a>

For each version, we need two files, ```wikirate_indicator_version1.txt``` and ```wikirate_to_indicator_version1.csv```.

- ```wikirate_indicator_version.txt``` is a txt file, each line describes the index, category, and a list of keywords
- ```wikirate_to_indicator_version.csv```: is a csv file, each row describes the index, indicator and metric name.


**Version I**

- [wikirate_indicator_version1.txt](rule/wikirate_indicator_version1.txt)
- [wikirate_to_indicator_version1.csv](rule/wikirate_to_indicator_version1.csv)

**Version II**

- [wikirate_indicator_version2.txt](rule/wikirate_indicator_version2.txt)
- [wikirate_to_indicator_version2.csv](rule/wikirate_to_indicator_version2.csv)

**Version III (Latest)**

For the latest version, we only have an instruction [KEYWORDS-MinAdv-AUG13.xlsx](rule/KEYWORDS-MinAdv-AUG13.xlsx), you have to make the two files mentioned above to run the following extraction function.

## Extraction Function <a id="function"></a>
Check the file: [extraction_example.py](code/extraction_example.py), all input files can be found in the folder [data/extract_example](/data/extract_example). The [selected_2017_co.csv](data/extract_example/selected_2017_co.csv) is a small sample, because couldn't upload large files here.

- **[Can Skip] TODO 1**: Some tools used to compare results
- **TODO 2**: Functions to extract keywords and numbers
- **[Can Skip] TODO 3**: Match the required input data
- **TODO 4**: Implement rules and extraction functions

Check the previous documentation to preview the what the input and output data look like: [keywords_extraction_visualization.docx](prev_docu/keywords_extraction_visualization.docx)

# Calculate Scores <a id="analytics"></a>

- Code: [Jane_template_to_calculate_score_for_each_corp.ipynb](code/Jane_template_to_calculate_score_for_each_corp.ipynb)
- Data: [two_year_result.csv](data/visualization/two_year_result.csv)

For further analysis, we might need to evaluate a company and calculate score based on the completeness of all indicators. Given the **rule version I**, here is an example of how to do the evaluation for the first 

Goal is to determine if EACH company meets the minimum criteria. So, if company has at least (1) in each category (4 categories), then it qualifies and the value for that company that year becomes One; otherwise Zero

<img src="figure/score_rule.png">

We can use the weight dictionary to calculate the total score

```
weight = {'1.1':5, '1.2':5, '1.3':5, '1.4':5, '1.5':5,
    '2.1':12.5, '2.2':12.5,
    '3.1':5, '3.2':5, '3.3':5, '3.4':5, '3.5':5,
    '4.1':25/6, '4.2':25/6, '4.3':25/6, '4.4':25/6, '4.5':25/6, '4.6':25/6}
```

Here I considered two scenarios: 

- For each indicator, if its completeness equal to 1 or 2, then it can get its corresponding points
- For each indicator, only its completeness equal to 2, can it get its corresponding points

```python
for co in companies:
    cache = {'1.1':0, '1.2':0, '1.3':0, '1.4':0, '1.5':0, '2.1':0, '2.2':0, '3.1':0, '3.2':0, '3.3':0, '3.4':0, '3.5':0, '4.1':0, '4.2':0, '4.3':0, '4.4':0, '4.5':0, '4.6':0}
    indicator = score_data[co].to_list()[:-2]
    for i in range(32):
        if indicator[i] == 1 or indicator[i] == 2:
            cache[example[ind[i]]] = weight[example[ind[i]]]
    score_data[co][32] = sum(cache.values())

for co in companies:
    cache = {'1.1':0, '1.2':0, '1.3':0, '1.4':0, '1.5':0, '2.1':0, '2.2':0, '3.1':0, '3.2':0, '3.3':0, '3.4':0, '3.5':0, '4.1':0, '4.2':0, '4.3':0, '4.4':0, '4.5':0, '4.6':0}
    indicator = score_data[co].to_list()[:-2]
    for i in range(32):
        if indicator[i] == 2:
            cache[example[ind[i]]] = weight[example[ind[i]]]
    score_data[co][33] = sum(cache.values())
```

<img src="figure/completeness.png">

# Visualize Trend <a id="trend"></a>
- Code: [Jane_UNCTAD_visualization.ipynb](Code/Jane_UNCTAD_visualization.ipynb)

## Visualize the threshold <a id="threshold"></a>
In this part, we want to see how many companies have scores higher than the threshold.

- First we need to use the following function to count how many companies are above the threshold, and generate a meta data table for the visualization.

```python
def metadata(df, col, threshold, complete):
    if complete == 1:
        ind = 32
    else: ind = 33
    counts = []
    for i in range(len(threshold)):
        count = 0
        for item in col:
            if df[item][ind] >= threshold[i]:
                count += 1
                counts.append(count)
    return counts
```


<img src="figure/threshold.png">

- The 5th row means that:
    - There are 1516 companies whose scores are higher than 4 based on the first scenario (considering completeness=1 and completeness=2) in 2017, accounting for 51%;
    - There are 1339 companies whose scores are higher than 4 based on the second scenario (considering completeness=2) in 2017, accounting for 45%;
    - There are 2952 companies whose scores are higher than 4 based on the first scenario (considering completeness=1 and completeness=2) in 2018, accounting for about 100%;
    - There are 2846 companies whose scores are higher than 4 based on the second scenario (considering completeness=2) in 2018, accounting for 96%;

- And here is how the plots look like

<img src="figure/thresh_compare.png">

## Visualize the distribution <a id="distribution"></a>

Also, you can check the code to visualize the distribution for each year, by using stacked bar chats.

<img src="figure/distribution.png">

```python
plt.subplot(121)
plt.barh(index0, x0, color="lightsteelblue")
plt.barh(index0, x1, left=x0, color="royalblue")
plt.barh(index0, x2, left=x01, color="navy")
plt.legend(['completeness = 0', 'completeness = 1', 'completeness = 2'])
plt.xlabel('Number of corps (2901 in total)', fontsize=16)  
plt.ylabel('Indicators', fontsize=16)
plt.grid(True)
plt.title('Distribution of completeness in 2018', fontsize=16)

plt.subplot(122)
plt.barh(index0, x0_, color="lightsteelblue")
plt.barh(index0, x1_, left=x0_, color="royalblue")
plt.barh(index0, x2_, left=x01_, color="navy")
plt.legend(['completeness = 0', 'completeness = 1', 'completeness = 2'])
plt.xlabel('Number of corps (2901 in total)', fontsize=16)  
plt.ylabel('Indicators', fontsize=16)
plt.grid(True)
plt.title('Distribution of completeness in 2017', fontsize=16)

plt.show()
```


## Visualize the trend of each indicator <a id="indicator"></a>

<img src="figure/indicator_trend.png">

We can use the following code to calculate the score (simple average with the maximum of 2) for each indicator, visualized the trend for each indicator, and grouped by the categories of indicators

- Data Processing

```python
score2017, score2018 = [], []
for i in range(32):
    sum2017, sum2018 = 0, 0
    for item in col2017:
        sum2017 += score_data[item][i]
    for item in col2018:
        sum2018 += score_data[item][i]
    score2017.append(sum2017/total)
    score2018.append(sum2018/total)

score = {}
for i in range(32):
    score[ind[i]]=[score2017[i], score2018[i]]

score = pd.DataFrame(data=score)
```

- Visualization Code

```python
x = [1,2]
color=['tab:blue','tab:brown','tab:orange','tab:pink','tab:green','tab:gray','tab:red','tab:olive','tab:purple','tab:cyan']
plt.figure(figsize=(16,10))


plt.subplot(221)
for i in range(0,8):
    y=score[ind[i]]
    plt.plot(x, y,color=color[i])
    
    x_ = 1+0.1*(i)
    y_ = y[0]+(y[1]-y[0])*0.1*(i)
    th1 = plt.text(x_, y_, '{}'.format(ind[i]), fontsize=12, rotation_mode='anchor',bbox=dict(facecolor=color[i],alpha=0.5))
plt.grid()
plt.xticks(x,['2017','2018'],fontsize=14)
plt.ylabel('Simple average',fontsize=14)
plt.ylim((0,2))
plt.title('Economic Indicators',fontsize=16)
# plt.legend(list(ind.values())[:8],loc='upper center', bbox_to_anchor=(0.5, -0.05),fancybox=True, shadow=True, ncol=10, fontsize = 10)
plt.legend(list(ind.values())[:8],loc='center left', bbox_to_anchor=(1, 0.5),fontsize=10)

plt.subplot(222)
for i in range(8,18):
    y=score[ind[i]]
    plt.plot(x, y,color=color[i-8])
    
    x_ = 1+0.1*(i-8)
    y_ = y[0]+(y[1]-y[0])*0.1*(i-8)
    th1 = plt.text(x_, y_, '{}'.format(ind[i]), fontsize=12, rotation_mode='anchor',bbox=dict(facecolor=color[i-8],alpha=0.5))
plt.grid()
plt.xticks(x,['2017','2018'],fontsize=14)
plt.ylabel('Simple average',fontsize=14)
plt.ylim((0,2))
plt.title('Environmental Indicators',fontsize=16)
plt.legend(list(ind.values())[8:18],loc='center left', bbox_to_anchor=(1, 0.5),fontsize=10)

plt.subplot(223)
for i in range(18,25):
    y=score[ind[i]]
    plt.plot(x, y,color=color[i-18])
    
    x_ = 1+0.1*(i-18)
    y_ = y[0]+(y[1]-y[0])*0.1*(i-18)
    th1 = plt.text(x_, y_, '{}'.format(ind[i]), fontsize=12, rotation_mode='anchor',bbox=dict(facecolor=color[i-18],alpha=0.5))
plt.grid()
plt.xticks(x,['2017','2018'],fontsize=14)
plt.ylabel('Simple average',fontsize=14)
plt.ylim((0,2))
plt.title('Social Indicators',fontsize=16)
plt.legend(list(ind.values())[18:25],loc='center left', bbox_to_anchor=(1, 0.5),fontsize=10)

plt.subplot(224)
for i in range(25,32):
    y=score[ind[i]]
    plt.plot(x, y,color=color[i-25])
    
    x_ = 1+0.1*(i-25)
    y_ = y[0]+(y[1]-y[0])*0.1*(i-25)
    th1 = plt.text(x_, y_, '{}'.format(ind[i]), fontsize=12, rotation_mode='anchor',bbox=dict(facecolor=color[i-25],alpha=0.5))
plt.grid()
plt.xticks(x,['2017','2018'],fontsize=14)
plt.ylabel('Simple average',fontsize=14)
plt.ylim((0,2))
plt.title('Institutional and Governance',fontsize=16)
plt.legend(list(ind.values())[25:32],loc='center left', bbox_to_anchor=(1, 0.5),fontsize=10)

plt.tight_layout()
plt.show()
```

## Visualize the trend of each category <a id="category"></a>

We calculated the simple average for each category and visualized the trend for each category

<img src="figure/category_trend.png">

- Data Processing

```python
def avg_4_catagory(df, year):
    catagory = {"Economic Indicators":0, "Environmental Indicators":0, "Social Indicators":0, "Institutional and Governance":0}
    indicator = list(ind.values())
    if year==2017:
        order = 0
    if year == 2018:
        order = 1
    A,B,C,D = 0,0,0,0
    for item in indicator:
        if item[0]=='A':
            catagory["Economic Indicators"] += score[item][order]
            A += 1
        elif item[0]=='B':
            catagory["Environmental Indicators"] += score[item][order]
            B += 1
        elif item[0]=='C':
            catagory["Social Indicators"] += score[item][order]
            C += 1
        else:
            catagory["Institutional and Governance"] += score[item][order]
            D += 1
    catagory["Economic Indicators"]=catagory["Economic Indicators"]/A
    catagory["Environmental Indicators"] = catagory["Environmental Indicators"]/B
    catagory["Social Indicators"] = catagory["Social Indicators"]/C
    catagory["Institutional and Governance"] = catagory["Institutional and Governance"]/D

    return catagory

catagory2017 = avg_4_catagory(score, 2017); print(catagory2017)
catagory2018 = avg_4_catagory(score, 2018); print(catagory2018)

catagory = defaultdict(list)
col = ["Economic Indicators", "Environmental Indicators", "Social Indicators", "Institutional and Governance"]
for item in col:
    catagory[item].append(catagory2017[item])
    catagory[item].append(catagory2018[item])
score_2 = pd.DataFrame(data=catagory)
```

- Visualization

```python
x = [1,2]
color=['tab:blue','tab:brown','tab:orange','tab:pink','tab:green','tab:gray','tab:red','tab:olive','tab:purple','tab:cyan']
plt.figure(figsize=(8,6))

for i in range(0,4):
    y=score_2[col[i]]
    plt.plot(x, y,color=color[i])
    
    x_ = 1+0.22*(i)
    y_ = y[0]+(y[1]-y[0])*0.22*(i)

plt.grid()
plt.xticks(x,['2017','2018'],fontsize=14)
plt.ylabel('Simple average',fontsize=14)
plt.ylim((0,2))
plt.legend(col,loc='center left', bbox_to_anchor=(1, 0.5),fontsize=12)

plt.title('GCI YoY Change',fontsize=16)

plt.show()
```

## Visualize the trend of each region <a id="region"></a>

We calculated the simple average for each sub region and the trend
- Average all indicators to calculate the score of each category
- Average four categories to calculate the score of each corp
- Average the score of all corps in a region to get the score of that region


<img src="figure/region_trend.png">

- Data Processing

> Check the Juoyter Notebook

- Visualization

```python
col4 = sub
x = [1,2]
color=['tab:blue','tab:brown','tab:orange','tab:pink','tab:green','tab:gray','tab:red','tab:olive','tab:purple','tab:cyan',
       'purple','brown','b','lime','black','gray']
plt.figure(figsize=(8,6))

for i in range(len(col4)):
    y=region3[col4[i]]
    plt.plot(x, y,color=color[i])
plt.grid()
plt.xticks(x,['2017','2018'],fontsize=14)
plt.ylabel('Simple average',fontsize=14)
plt.ylim((0,2))
plt.legend(col4,loc='center left', bbox_to_anchor=(1, 0.5),fontsize=12)

plt.title('GCI YoY Change Group By Sub-region',fontsize=16)

plt.show()
```


# Reference <a id="reference"></a>

[1] Previous documentation for text extraction from pdf files: [UNGC repository](https://github.com/globalaiorg/PROJECT-UNGC-COPS) (https://github.com/globalaiorg/PROJECT-UNGC-COPS.git) **(ask for permission)**

[2] Previous documentation for keywords extraction and visualization: [keywords_extraction_visualization.docx](prev_docu/keywords_extraction_visualization.docx)


----

<br>

<br>

<br>

If you have any question about this documentation, e-mail to the following address:

**Jane zl2772@columbia.edu**

