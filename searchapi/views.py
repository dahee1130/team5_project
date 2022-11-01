# 전달받은 정보에 필요한 데이터를 모듈에게 달라고 요청
import json
import urllib.request
import pandas as pd
import re

from django.shortcuts import render

from sqlalchemy import create_engine
import pymysql

# from .model import Searchapi

# from django.db import connection

# ipconfig 주소 설정
engine = create_engine("mysql+pymysql://director:1234@127.0.0.1:3306/mymovie")
# engine = create_engine("mysql+pymysql://director:1234@172.30.1.32:3306/mymovie")
conn = engine.connect

client_id = "QNw9k2mLukjBHx1zWHsG"
client_secret = "GvPiAz3U6C"



def search(request):

    # 검색 키워드 (pasre.quote : utf8 변경)
    # 결과 JSON 값으로 출력, key + value
    # encText = urllib.parse.quote("컴퓨터")
    query = urllib.parse.quote(input("검색어: "))

    # 인덱스 1000개까지 불러오도록 설정
    idx = 0 
    # 네이버 API 기본 10개까지 보여줌, 100개 단위로 가져오도록 설정
    display = 100
    start = 1
    end = 1000
    sort = "sim"
    # data print 값으로 불러오는 게 아니라, pandas 사용해서 불러오기
    # pandas DataFrame : 테이블 형식의 데이터를 다룰 때 사용(열 8개의 데이터프레임 완성)
    # 링크 필요없을 것 같으면 빼기**
    movie_df = pd.DataFrame(columns=('Title', 'Link', 'Image', 'Subtitle', 'Publication Date', 'Director', 'Actor','User Rating'))

    # 1부터 1000까지, 100개 단위(100개씩 가져와야 하니까)
    for start_index in range(start, end, display):

        # JSON 결과, 시작 위치가 계속 바뀌면서 출력 가능
        url = "https://openapi.naver.com/v1/search/movie?query=" + query \
            + "&display=" + str(display) \
            + "&start=" + str(start_index) \
            + "&sort=" + sort


        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",client_id)
        request.add_header("X-Naver-Client-Secret",client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()

        # rescode==200, 성공 의미, API 요청 응답을 받았다는 의미(정상적인 응답)
        if(rescode==200):
            response_body = response.read()
            # 파싱
            response_dict = json.loads(response_body.decode('utf-8'))
            # items 안의 값을 가져와야 하므로, items 키에 해당하는 거 다 가져옴 
            items = response_dict['items']

            for item_index in range(0, len(items)):
                # 결과값에 <b>검색어</b> 태그 설정되어 있으므로 태그 삭제하기 위한 re 모듈 import
                remove_tag = re.compile('<.*?>')
                title = re.sub(remove_tag, "", items[item_index]['title'])
                link = items[item_index]['link']
                image = items[item_index]['image']
                subtitle = items[item_index]['subtitle']
                pub_date = items[item_index]['pubDate']
                director = items[item_index]['director']
                actor = items[item_index]['actor']
                user_rating = items[item_index]['userRating']

                # 만들어놓은 데이터프레임에 넣어주기
                movie_df.loc[idx] = [title, link, image, subtitle, pub_date, director, actor, user_rating]
                idx += 1  # index 값 +1 씩 증가
        else:
            print("Error Code:" + rescode)

    # 주피터에서는 print 함수 안쓰고 movie_df라고만 해도 출력됨

    print(movie_df) 

    # to_sql : db 넣기
    movie_df.to_sql(name='searchmovie',con=engine, if_exists='replace')
        
    # return render(request, 'search/search.html')

def searchData(request):
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM searchmovie"
        result = cursor.execute(query)
        datas = cursor.fetchall()

        data = []

        for data in datas:
            row = {
                'id': datas[0],
                'title': datas[1],
                'link': datas[2],
                'image': datas[3],
                'subtitle': datas[4],
                'pub_date': datas[5],
                'director': datas[6],
                'actor': datas[7],
                'user_rating': datas[8],
            }

            data.append(row)

            conn.commit()
            conn.close()

    except:
        # conn.rollback()
        print("fail")

    context = {'datas': datas}

    return render(request, "search/search.html", context)