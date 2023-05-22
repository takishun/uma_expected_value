#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import datetime
import matplotlib.pyplot as plt
import japanize_matplotlib
import seaborn as sns
import streamlit as st
from scipy.special import comb
from scipy.special import perm

def tanshou_cal(bet,horces,number):
    return bet/horces*number

def hukushou_cal(bet,horces,number):
    return bet*3/horces*number

def sanrentan(bet,horces,number):
    return bet*number/perm(horces,3)

def sanrenpuku(bet,horces,number):
    return bet*number/comb(horces,3)

def umaren(bet,horces,number):
    return bet*number/comb(horces,2)

def umatan(bet,horces,number):
    return bet*number/perm(horces,2)

def wide(bet,horces,number):
    return bet*number*perm(3,2)/comb(horces,2)

if __name__ == "__main__":
    st.set_page_config(
        page_title="競馬期待値カリキュレーター",
        page_icon="🏇",
        initial_sidebar_state="expanded"
    )
    
    st.title('競馬期待値計算機')
    st.text('オッズ、出馬数、掛け金を入力して競馬の掛け方別の期待値を計算してくれます。')
    st.text('期待値の下には掛け金と期待値の差を表示します。')
    st.text('賭ける時にどれくらいかける価値があるかの参考にお使いください。')
    st.text('※単純にレースの出馬数に応じた賭け方別の組み合わせから確率を求めたものになります。※')
    st.text('※馬の特徴や、馬場、レース上、距離、天気などの要素は考慮されておりませんのでご注意ください。※')
    
    pub1,pub2,pub3,pub4 = st.columns(4)
    with pub1:
        st.components.v1.html('<a href="https://www.amazon.co.jp/%E7%AB%B6%E9%A6%AC%E3%81%AE%E6%95%99%E7%A7%91%E6%9B%B8-%E7%99%BA%E6%83%B3%E3%82%92%E5%A4%89%E3%81%88%E3%82%8B%E3%81%A0%E3%81%91%E3%81%A7%E5%9B%9E%E5%8F%8E%E7%8E%87%E3%81%AF%E4%B8%8A%E3%81%8C%E3%82%8B-%E7%8E%89%E5%B6%8B-%E4%BA%AE/dp/4801490719?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&keywords=%E7%AB%B6%E9%A6%AC&qid=1684756147&sr=8-5&linkCode=li2&tag=takishun03-22&linkId=f7966740090910e75f97213c1381ea2a&language=ja_JP&ref_=as_li_ss_il" target="_blank"><img border="0" src="//ws-fe.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=4801490719&Format=_SL160_&ID=AsinImage&MarketPlace=JP&ServiceVersion=20070822&WS=1&tag=takishun03-22&language=ja_JP" ></a><img src="https://ir-jp.amazon-adsystem.com/e/ir?t=takishun03-22&language=ja_JP&l=li2&o=9&a=4801490719" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />')
        st.markdown('<a href = "https://amzn.to/3MO8OYz">競馬の教科書 発想を変えるだけで回収率は上がる</a>',unsafe_allow_html=True)
    with pub2:
        st.components.v1.html("""
        <a href="https://www.amazon.co.jp/%E7%A5%9E%E3%81%AE%E9%A6%AC%E5%88%B8%E8%A1%93-%E5%B9%B4%E9%96%93%E5%8F%8E%E6%94%AF%E3%82%92%E3%83%97%E3%83%A9%E3%82%B9%E3%81%AB%E5%A4%89%E3%81%88%E3%82%8B43%E3%81%AE%E5%A5%A5%E7%BE%A9-%E3%82%AD%E3%83%A3%E3%83%97%E3%83%86%E3%83%B3%E6%B8%A1%E8%BE%BA/dp/4046061294?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&keywords=%E7%AB%B6%E9%A6%AC&qid=1684756147&sr=8-7&linkCode=li2&tag=takishun03-22&linkId=aaa5d765566937baa98565ddb89c1934&language=ja_JP&ref_=as_li_ss_il" target="_blank"><img border="0" src="//ws-fe.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=4046061294&Format=_SL160_&ID=AsinImage&MarketPlace=JP&ServiceVersion=20070822&WS=1&tag=takishun03-22&language=ja_JP" ></a><img src="https://ir-jp.amazon-adsystem.com/e/ir?t=takishun03-22&language=ja_JP&l=li2&o=9&a=4046061294" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />
        """)
        st.markdown('<a href = "https://amzn.to/3OvuGJe">神の馬券術 年間収支をプラスに変える43の奥義</a>',unsafe_allow_html=True)        
    with pub3:
        st.components.v1.html("""
        <a href="https://www.amazon.co.jp/%E6%BC%AB%E7%94%BB%E7%89%88-%E9%A6%AC%E5%88%B8%E8%A1%93%E6%94%BF%E6%B2%BB%E9%A8%8E%E6%89%8B%E5%90%8D%E9%91%912023-%E6%A8%8B%E9%87%8E%E7%AB%9C%E5%8F%B8/dp/4575318000?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&keywords=%E7%AB%B6%E9%A6%AC&qid=1684756147&sr=8-3&linkCode=li2&tag=takishun03-22&linkId=39778c213f3318fba44d6b0c415ceec3&language=ja_JP&ref_=as_li_ss_il" target="_blank"><img border="0" src="//ws-fe.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=4575318000&Format=_SL160_&ID=AsinImage&MarketPlace=JP&ServiceVersion=20070822&WS=1&tag=takishun03-22&language=ja_JP" ></a><img src="https://ir-jp.amazon-adsystem.com/e/ir?t=takishun03-22&language=ja_JP&l=li2&o=9&a=4575318000" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />
        """)
        st.markdown('<a href = "https://amzn.to/45ktJcR">漫画版　馬券術政治騎手名鑑2023</a>',unsafe_allow_html=True)
    with pub4:
        st.components.v1.html("""
        <a href="https://www.amazon.co.jp/%E5%8B%9D%E3%81%A1%E9%A6%AC%E3%81%8C%E3%82%8F%E3%81%8B%E3%82%8B-%E8%A1%80%E7%B5%B1%E3%81%AE%E6%95%99%E7%A7%91%E6%9B%B82-0-%E4%BA%80%E8%B0%B7-%E6%95%AC%E6%AD%A3/dp/4262144739?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&keywords=%E7%AB%B6%E9%A6%AC&qid=1684756147&sr=8-6&linkCode=li2&tag=takishun03-22&linkId=d842b38dc6e58368dd2b960957f59494&language=ja_JP&ref_=as_li_ss_il" target="_blank"><img border="0" src="//ws-fe.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=4262144739&Format=_SL160_&ID=AsinImage&MarketPlace=JP&ServiceVersion=20070822&WS=1&tag=takishun03-22&language=ja_JP" ></a><img src="https://ir-jp.amazon-adsystem.com/e/ir?t=takishun03-22&language=ja_JP&l=li2&o=9&a=4262144739" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />
        """)
        st.markdown('<a href = "https://amzn.to/3MMttMp">勝ち馬がわかる 血統の教科書2.0</a>',unsafe_allow_html=True)
    
    number = st.number_input('オッズ',value = 1.00)
    horces = st.number_input('馬数',format='%d',value=18,min_value=1,max_value=18)
    bet = st.number_input('掛け金',format='%d',value=100,min_value=0)
    
    st.subheader('単勝、複勝期待値')
    col1, col2 = st.columns(2)
    col1.metric(label='単勝期待値', value = round(tanshou_cal(bet,horces,number),2),delta = round(tanshou_cal(bet,horces,number)-bet,2))
    col2.metric(label='複勝期待値', value = round(hukushou_cal(bet,horces,number),2),delta = round(hukushou_cal(bet,horces,number)-bet,2))
    
    #三連単、三連複
    st.subheader('三連単、三連複期待値')
    col3,col4 = st.columns(2)
    col3.metric(label='三連単期待値', value = round(sanrentan(bet,horces,number),2),delta = round(sanrentan(bet,horces,number)-bet,2))
    col4.metric(label='三連複期待値', value = round(sanrenpuku(bet,horces,number),2),delta = round(sanrenpuku(bet,horces,number)-bet,2))
        
    #馬単、馬連、ワイド
    st.subheader('馬単、馬連、ワイド期待値')
    col5,col6,col7 = st.columns(3)
    col5.metric(label='馬単期待値', value = round(umatan(bet,horces,number),2),delta = round(umatan(bet,horces,number)-bet,2))
    col6.metric(label='馬連期待値', value = round(umaren(bet,horces,number),2),delta = round(umaren(bet,horces,number)-bet,2))
    col7.metric(label='ワイド期待値', value = round(wide(bet,horces,number),2),delta = round(wide(bet,horces,number)-bet,2))
    

