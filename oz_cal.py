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
import streamlit.components.v1 as stc

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
        page_icon="uma_icon.png",
        initial_sidebar_state="expanded"
    )
    
    st.title('競馬期待値計算機')
    st.text('オッズ、出馬数、掛け金を入力して競馬の掛け方別の期待値を計算してくれます。')
    st.text('期待値の下には掛け金と期待値の差を表示します。')
    st.text('賭ける時にどれくらいかける価値があるかの参考にお使いください。')
    st.text('※単純にレースの出馬数に応じた賭け方別の組み合わせから確率を求めたものになります。※')
    st.text('※馬の特徴や、馬場、レース上、距離、天気などの要素は考慮されておりませんのでご注意ください。※')
    
    pub1,pub2,pub3 = st.columns(3)
    with pub1:
        stc.html('''
        <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3UQ4L6+1JS2+IFD69" rel="nofollow">
        <img border="0" width="125" height="125" alt="" src="https://www23.a8.net/svt/bgt?aid=230702425233&wid=006&eno=01&mid=s00000007229003095000&mc=1"></a>
        <img border="0" width="1" height="1" src="https://www11.a8.net/0.gif?a8mat=3TCR4P+3UQ4L6+1JS2+IFD69" alt="">
        ''',height=130)
        
        st.markdown('<a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3UQ4L6+1JS2+HWPVM" rel="nofollow">100円で最高6億円！！【オッズパークLOTO】</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=3TCR4P+3UQ4L6+1JS2+HWPVM" alt="">',unsafe_allow_html=True) 
        
    with pub2:
        stc.html("""
        <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3SXTRU+1JS2+6PJZL" rel="nofollow">
        <img border="0" width="125" height="125" alt="" src="https://www24.a8.net/svt/bgt?aid=230702425230&wid=006&eno=01&mid=s00000007229001127000&mc=1"></a>
        <img border="0" width="1" height="1" src="https://www18.a8.net/0.gif?a8mat=3TCR4P+3SXTRU+1JS2+6PJZL" alt="">        """,
                 height=130)
        st.markdown('<a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3SXTRU+1JS2+5ZMCI" rel="nofollow">携帯電話でも地方競馬の馬券購入OK！</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=3TCR4P+3SXTRU+1JS2+5ZMCI" alt="">',unsafe_allow_html=True)        
    
    with pub3:
        stc.html("""
        <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+7XS70A+1V0I+HW2Q9" rel="nofollow">
        <img border="0" width="125" height="125" alt="" src="https://www28.a8.net/svt/bgt?aid=230702425480&wid=006&eno=01&mid=s00000008685003005000&mc=1"></a>
        <img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=3TCR4P+7XS70A+1V0I+HW2Q9" alt="">""",height = 130)
        st.markdown('<a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+7XS70A+1V0I+HZ2R6" rel="nofollow">無料で勝馬予想！ <br>穴馬券を当てる！</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=3TCR4P+7XS70A+1V0I+HZ2R6" alt="">',unsafe_allow_html=True)
    
    number = st.number_input('オッズ',value = 1.00)
    horces = st.number_input('馬数',format='%d',value=18,min_value=1,max_value=18)
    bet = st.number_input('掛け金',format='%d',value=100,min_value=0)
    st.write('---')
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
    
    st.write('---')
    stc.html(
        """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
    <iframe src="https://rcm-fe.amazon-adsystem.com/e/cm?o=9&p=48&l=ur1&category=echoauto&banner=0VQAXFW9622P0NK7V382&f=ifr&linkID=fcb2e50250a1f550d4dc6f5b00efa39a&t=takishun03-22&tracking_id=takishun03-22" width="728" height="90" scrolling="no" border="0" marginwidth="0" style="border:none;" frameborder="0" sandbox="allow-scripts allow-same-origin allow-popups allow-top-navigation-by-user-activation"></iframe>
    </body>
    </html> 
        """,
        height=90,
    )

