# !pip install pyquery
from pyquery import PyQuery as pq
import pandas as pd

nameL, typeL, sectorL, countryL, joinL = [],[],[],[],[]

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


for i in range(1,8):
    url = 'https://unglobalcompact.org/what-is-gc/participants/search?page='+str(i)+'&search%5Bcountries%5D%5B%5D=224'
    doc = pq(url)
    parse_one_page(doc)
    print(i)

df = pd.DataFrame({'Name':nameL,'Type':typeL,'Sector':sectorL,'Country':countryL,'Joined On':joinL})
df = df[df.Type != 'Type']
df.to_csv('unglobalcompact_metadata.csv', index=False)
print('done!')