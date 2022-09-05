from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import folium
import openpyxl
from openpyxl import load_workbook
import pandas as pd


# 원하는 지역 선택
print("1 : 서울 , 2 : 부산 , 3 : 대구 , 4 : 인천, 5: 광주, 6 : 대전, 7 : 울산, 8 : 경기, 9 : 강원, 10 : 충북, 11 : 충남, 12 : 세종, 13 : 전북, 14 : 전남, 15 : 경북, 16 : 경남, 17 : 제주")
region = int(input("Please choose your region number:"))

if (region=='')or(region>17) :
    print("Please enter an integer below 17")
    region = int(input("Please choose your region number:"))

region_data = pd.read_excel('kimstudy_map.xlsx')
url = region_data['지역별 링크'][region-1]

html = urlopen(url)
soup = BeautifulSoup(html,"html.parser")

tmp_one = soup.find_all('div', class_='text text-ellipsis text-basic-black text-sm')

age = []
subject = []
place= []

for i in range(204):
    result = tmp_one[i].get_text()

    if i%3==0 :
        age.append(result.strip())
    elif i%3==1 :
        subject.append(result.strip())
    elif i%3==2 :
        place.append(result.strip())
        

#자료 엑셀로 변환
kimstudy = pd.DataFrame(
    {'age' : age, 'subject' : subject, 'place' : place})
kimstudy.to_excel('kimstudy.xlsx')


def find_places(searching):
    url = 'http://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(searching)
    headers = {"Authorization" : "KakaoAK 7cecf6205ed0332615a9906f5a18e070"}
    places = requests.get(url,headers = headers).json()['documents']

    place = places[0]
    name = place['place_name']
    x=place['x']
    y=place['y']
    data = [name,x,y,searching]

    return data
    

wb = load_workbook('kimstudy.xlsx')
data = wb.active
col = data['D']
locations_inform=[ ]

for cell in col:
    va= cell.value
    
    if (va[len(va)-1]=='구'):
          plus = '구청'
    elif (va[len(va)-1]=='군'):
        plus = '군청'
    elif (va[len(va)-1]=='시'):
        plus = '시청'
    else :
        plus = ''
    pl = va + plus 
    contents = find_places(pl)
    locations_inform.append(contents)

#locations 파일 생성
     
locations_inform_df = pd.DataFrame(locations_inform)
locations_inform_df.columns = ['장소 이름','경도','위도','과외 장소']
locations_inform_df.to_excel('locations.xlsx',index=True)
locations_inform_df=locations_inform_df.drop(locations_inform_df.index[[0]])
locations_inform_df.to_excel('locations.xlsx',index=True)

location_data1 = pd.read_excel('locations.xlsx')

#지도에 시각화

middle = [37.5,128.02]

map_korea = folium.Map(location = middle, zoom_start = 7)

for i in range(len(location_data1)):
    
    name1 = location_data1 ['과외 장소'][i]
    delname = name1[len(name1)-2 : len(name1)]
    name2 = name1.replace(delname,'')
    
    long = float(location_data1['위도'][i])
    lat=float(location_data1['경도'][i])
    folium.CircleMarker((long,lat) , radius = 20, color = 'blue', fill_color = 'navy',popup=name2).add_to(map_korea)    

map_korea.save('kim_location_map.html')
map_korea