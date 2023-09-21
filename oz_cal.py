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

def tanshou_prob(horces,number):
    return bet/horces*number

def hukushou_prob(horces,number):
    return 100*3/horces*number

def sanrentan_prob(horces,number):
    return 100*number/perm(horces,3)

def sanrenpuku_prob(horces,number):
    return 100*number/comb(horces,3)

def umaren_prob(horces,number):
    return 100*number/comb(horces,2)

def umatan_prob(horces,number):
    return 100*number/perm(horces,2)

def wide_prob(horces,number):
    return 100*number*perm(3,2)/comb(horces,2)

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
    
    st.subheader('更新内容')
    st.text('''
    2023/09/17 確率表示を追加。
    ※確率値は単純に出走馬数から場合の数を計算した値になります。馬場や個々の馬の調子、能力は考慮されていません。
    ''')
    
    st.write('---')
    pub1,pub2,pub3 = st.columns(3)
    with pub1:
        stc.html('''
        <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3RQYKA+19NM+C03K1" rel="nofollow">
        <img border="0" width="200" height="125" alt="" src="https://www26.a8.net/svt/bgt?aid=230702425228&wid=006&eno=01&mid=s00000005917002016000&mc=1"></a>
        <img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=3TCR4P+3RQYKA+19NM+C03K1" alt="">''',
        height=130)
        st.markdown('<a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3RQYKA+19NM+BY642" rel="nofollow">【楽天競馬】が【楽天銀行（旧イーバンク銀行）】でご利用可能に！</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=3TCR4P+3RQYKA+19NM+BY642" alt="">',unsafe_allow_html=True)
        
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
    col1.write('確率　'+str(round(tanshou_prob(horces,number),2))+'%')
    
    col2.metric(label='複勝期待値', value = round(hukushou_cal(bet,horces,number),2),delta = round(hukushou_cal(bet,horces,number)-bet,2))
    col2.write('確率　'+str(round(hukushou_prob(horces,number),2))+'%')
    
    #三連単、三連複
    st.subheader('三連単、三連複期待値')
    col3,col4 = st.columns(2)
    col3.metric(label='三連単期待値', value = round(sanrentan(bet,horces,number),2),delta = round(sanrentan(bet,horces,number)-bet,2))
    col3.write('確率　'+str(round(sanrentan_prob(horces,number),2))+'%')
    
    col4.metric(label='三連複期待値', value = round(sanrenpuku(bet,horces,number),2),delta = round(sanrenpuku(bet,horces,number)-bet,2))
    col4.write('確率　'+str(round(sanrenpuku_prob(horces,number),2))+'%')
               
    #馬単、馬連、ワイド
    st.subheader('馬単、馬連、ワイド期待値')
    col5,col6,col7 = st.columns(3)
    col5.metric(label='馬単期待値', value = round(umatan(bet,horces,number),2),delta = round(umatan(bet,horces,number)-bet,2))
    col5.write('確率　'+str(round(umatan_prob(horces,number),2))+'%')    
    
    col6.metric(label='馬連期待値', value = round(umaren(bet,horces,number),2),delta = round(umaren(bet,horces,number)-bet,2))
    col6.write('確率　'+str(round(umaren_prob(horces,number),2))+'%')    
    
    col7.metric(label='ワイド期待値', value = round(wide(bet,horces,number),2),delta = round(wide(bet,horces,number)-bet,2))
    col7.write('確率　'+str(round(wide_prob(horces,number),2))+'%')    
    st.write('---')
    fpub1,fpub2,fpub3 = st.columns(3)
    
    with fpub1:
        stc.html(
            """
            <iframe sandbox="allow-popups allow-scripts allow-modals allow-forms allow-same-origin" style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//rcm-fe.amazon-adsystem.com/e/cm?lt1=_blank&bc1=000000&IS2=1&bg1=FFFFFF&fc1=000000&lc1=0000FF&t=takishun03-22&language=ja_JP&o=9&p=8&l=as4&m=amazon&f=ifr&ref=as_ss_li_til&asins=B0C5QJ62D9&linkId=975a3db0015cb4a15ae63b4bb02fb730"></iframe>
            """,
            height=250,
        )
        
    with fpub2:
        stc.html(
        """
        <iframe sandbox="allow-popups allow-scripts allow-modals allow-forms allow-same-origin" style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//rcm-fe.amazon-adsystem.com/e/cm?lt1=_blank&bc1=000000&IS2=1&bg1=FFFFFF&fc1=000000&lc1=0000FF&t=takishun03-22&language=ja_JP&o=9&p=8&l=as4&m=amazon&f=ifr&ref=as_ss_li_til&asins=B07KS1YY9P&linkId=a6e95646c6d4d4df7d355dc042f4839f"></iframe>
        """,
        height=250,
        )
        
    with fpub3:
        stc.html(
            """
            <iframe sandbox="allow-popups allow-scripts allow-modals allow-forms allow-same-origin" style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//rcm-fe.amazon-adsystem.com/e/cm?lt1=_blank&bc1=000000&IS2=1&bg1=FFFFFF&fc1=000000&lc1=0000FF&t=takishun03-22&language=ja_JP&o=9&p=8&l=as4&m=amazon&f=ifr&ref=as_ss_li_til&asins=B08YC7HLJ8&linkId=899f2daa66c3d4426a0380210d45c455"></iframe>
            """,
        height=250,
        )
        
    stc.html("""
    <body>
    <!-- admax -->
    <script src="https://adm.shinobi.jp/s/6658c80bd06583e1574c8c92c085b252"></script>
    <!-- admax -->
    </body>
    """,height=100)
    
    stc.html("""
    <body>
    <!-- admax -->
    <script src="https://adm.shinobi.jp/s/45435edce7e7017f98344e0a9b71123c"></script>
    <!-- admax -->
    </body>
    """,height=60)
 

