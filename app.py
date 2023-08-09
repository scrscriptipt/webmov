#패키지 설치
import pickle
import pandas as pd
import streamlit as st
from tmdbv3api import Movie, TMDb
from googletrans import Translator
from ast import literal_eval
import streamlit.components.v1 as components
def main():
    st.set_page_config(layout = 'wide') #화면에 꽉 채우기
    st.sidebar.title('웹툰 정보') #sidebar에 웹툰정보 타이틀 쓰기

    translator = Translator() #번역 패키지에서 인스턴트 생성

    with open('style.css', encoding='UTF8') as f: #css 파일 받아와 스타일 적용하기
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    movie = Movie() #movie 인스턴트 생성
    tmdb = TMDb() #tmdb 인스턴트 생성
    tmdb.api_key = 'c68a2c0e7baa469a4ed83b78fb280ce6' #tmdb 개인 키 가져오기
    tmdb.language = 'ko-KR' #tmdb 언어 한국어로 설정
    movie_info = pd.read_csv('tmdb_5000_movies.csv') #영화 정보 받아오기
    df1 = pd.DataFrame(movie_info)
    naver_csv = pd.read_csv('naver.csv') #웹툰 정보 받아오기
    df2 = pd.DataFrame(naver_csv)
    indx = pd.Series(df1.index, index = df1['title']).drop_duplicates()
    indx2 = pd.Series(df2.index, index = df2['title']).drop_duplicates()

    df1['genres'] = df1['genres'].apply(literal_eval)

    def get_recommendations(title):
        # 입력한 웹툰의 인덱스값 받아오기
        idx = webtoon[webtoon['title'] == title].index[0]
        # 입력한 웹툰과 모든 영화의 유사도를 리스트로 만들기
        sim_score = list(enumerate(cos[idx]))
        # 영화 유사도 리스트를 높은 순으로 정렬하기
        cos_scores = sorted(sim_score, key=lambda x: x[1], reverse=True)
        # 영화 유사도 1위 부터 10위까지 받아오기
        cos_scores = cos_scores[1:11]
        # 영화 유사도를 기준으로 타이틀 값과 인덱스 값 받아오기
        movie_title_idx = [i[0] for i in cos_scores]
        titles = []
        titles_en = []
        images = []

        for i in movie_title_idx:
            #영화 서버에서 id를 기분으로 디테일 값 받아오기
            id = movies['id'].iloc[i]
            detail = movie.details(id)

            #이미지가 있는지 확인하고 있으면 이미지를 가져오고 없으면 없다고 표시
            image_path = detail['poster_path']
            if image_path:
                image_path = 'https://image.tmdb.org/t/p/w500'+ image_path
            else:
                image_path = 'no_image.jpg'

            #이미지 리스트에 이미지 링크 저장하기
            images.append(image_path)
            #타이틀 리스트에 한국어로 타이틀 저장하기
            titles.append(detail['title'])
            # 영어 타이틀 리스트에 영어로 타이틀 저장하기
            titles_en.append(movies.loc[i, 'title'])
        return images, titles, titles_en

    # 웹사이트에 가상의 레이아웃 생성
    empty1, col_title, empty2 = st.columns([1,8,1])
    col_des = st.columns(1)

    # 피클 파일 받아오기
    movies = pickle.load(open("movies.pickle","rb")) #영화 타이틀과 id
    webtoon = pd.read_pickle('webtoon.pickle') #웹툰 타이틀과 id
    cos = pd.read_pickle('cos.pickle') #코사인 유사도 파일

    col_title.image('component 1.png') #제목 작성

    webtoon_l = webtoon['title'].values
    title = col_title.selectbox('좋아하는 웹툰을 고르세요.',webtoon_l) #웹툰 input에서 값 받아오기
    if col_title.button('영화 추천 받기'): #버튼 값이 참이 되었을 때
        with st.spinner('검색하는 중...'): #로딩 창 보여주기
            tab1, tab2= st.tabs(['영화 이름 및 포스터' , '영화 정보']) #두개의 tab 생성하기
            images, titles, titles_en = get_recommendations(title) #함수로 추천 된 영화의 이미지, 타이틀, 영어 타이틀 값 받아오기

            #웹툰에 대한 정보 받아오고 사이드바에 표시
            st.sidebar.subheader('1.웹툰 작가')
            st.sidebar.write(df2.loc[indx2[title], 'author'])
            st.sidebar.write('')
            st.sidebar.subheader('2.웹툰 장르')
            st.sidebar.write(df2.loc[indx2[title], 'genre'])
            st.sidebar.write('')
            st.sidebar.subheader('3.웹툰 연령대')
            st.sidebar.write(df2.loc[indx2[title], 'age'])
            st.sidebar.write('')
            st.sidebar.subheader('4.웹툰 소개')
            st.sidebar.write(df2.loc[indx2[title], 'description'])
            st.sidebar.write('')
            st.sidebar.subheader('5.웹툰 링크')
            st.sidebar.write(df2.loc[indx2[title], 'link'])
            st.sidebar.write('')

            #영화 이미지와 제목 표시
            idx = 0
            for i in range(0,2):
                cols = tab1.columns(5)
                for col in cols:
                    col.subheader('{0}. {1}'.format(idx+1, titles[idx]))
                    col.image(images[idx])
                    idx += 1

            #영화 정보 표시
            idx = 0
            for i in range(0,10):
                cols = tab2.columns(1)
                for col in cols:
                    col.header('{0}. {1}'.format(idx+1, titles[idx]))
                    col.subheader('영화 정보')
                    result = translator.translate(movie_info.loc[indx[titles_en[idx]], 'overview'], dest = 'ko') #영화 내용이 영어 이므로 해석
                    col.write('영어: {0}'.format(movie_info.loc[indx[titles_en[idx]], 'overview']))
                    col.write('한국어: {0}'.format(result.text))
                    col.write('')
                    t_s = ''
                    for n in range(len(df1.loc[indx[titles_en[idx]],'genres'])): #장르 정보 받아와 표시
                        t_s = ('{0} '.format(t_s + df1.loc[indx[titles_en[idx]], 'genres'][n]['name']))
                    col.subheader('영화 장르')
                    col.write(t_s)
                    idx += 1

if __name__ == '__main__':
    main()