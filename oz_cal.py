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
    2024/02/10 広告掲載変更。
    ※確率値は単純に出走馬数から場合の数を計算した値になります。馬場や個々の馬の調子、能力は考慮されていません。
    ''')

    st.write('---')

    fpub1,fpub2,fpub3 = st.columns(3)

    with fpub1:
        stc.html(
            """
            <!-- Rakuten Widget FROM HERE --><script type="text/javascript">rakuten_affiliateId="0ea62065.34400275.0ea62066.204f04c0";rakuten_items="ctsmatch";rakuten_genreId="0";rakuten_recommend="on";rakuten_design="slide";rakuten_size="120x240";rakuten_target="_blank";rakuten_border="on";rakuten_auto_mode="on";rakuten_adNetworkId="a8Net";rakuten_adNetworkUrl="https%3A%2F%2Frpx.a8.net%2Fsvt%2Fejp%3Fa8mat%3D3N237F%2BFM1BP6%2B2HOM%2BBS629%26rakuten%3Dy%26a8ejpredirect%3D";rakuten_pointbackId="a22012721403_3N237F_FM1BP6_2HOM_BS629";rakuten_mediaId="20011816";</script><script type="text/javascript" src="//xml.affiliate.rakuten.co.jp/widget/js/rakuten_widget.js"></script><!-- Rakuten Widget TO HERE -->
            <img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=3N237F+FM1BP6+2HOM+BS629" alt="">
            """,
            height=250,
        )

    with fpub2:
        stc.html(
            """<table cellpadding="0" cellspacing="0" border="0" style=" border:1px solid #ccc; width:300px;"><tbody><tr style="border-style:none;"><td style="vertical-align:top; border-style:none; padding:10px; width:44px;"><a href="https://rpx.a8.net/svt/ejp?a8mat=3N237F+FM1BP6+2HOM+BWGDT&rakuten=y&a8ejpredirect=https%3A%2F%2Fhb.afl.rakuten.co.jp%2Fhgc%2Fg00q0724.2bo11c45.g00q0724.2bo12179%2Fa22012721403_3N237F_FM1BP6_2HOM_BWGDT%3Fpc%3Dhttps%253A%252F%252Fitem.rakuten.co.jp%252Fbook%252F17658846%252F%26amp%3Bm%3Dhttp%253A%252F%252Fm.rakuten.co.jp%252Fbook%252Fi%252F21088017%252F" rel="nofollow"><img border="0" alt="" src="https://thumbnail.image.rakuten.co.jp/@0_mall/book/cabinet/5462/2100013555462_1_3.jpg?_ex=64x64" /></a></td><td style="font-size:12px; vertical-align:middle; border-style:none; padding:10px;"><p style="padding:0; margin:0;"><a href="https://rpx.a8.net/svt/ejp?a8mat=3N237F+FM1BP6+2HOM+BWGDT&rakuten=y&a8ejpredirect=https%3A%2F%2Fhb.afl.rakuten.co.jp%2Fhgc%2Fg00q0724.2bo11c45.g00q0724.2bo12179%2Fa22012721403_3N237F_FM1BP6_2HOM_BWGDT%3Fpc%3Dhttps%253A%252F%252Fitem.rakuten.co.jp%252Fbook%252F17658846%252F%26amp%3Bm%3Dhttp%253A%252F%252Fm.rakuten.co.jp%252Fbook%252Fi%252F21088017%252F" rel="nofollow">【楽天ブックス限定全巻購入特典】『ウマ箱3』第3コーナー(アニメ「ウマ娘 プリティーダービー Season 3」トレーナーズBOX)【Blu-ray】(オリジナルキャンバスアート キタサンブラック＆ナイスネイチャ(雑誌版権イラスト使用)) [ Cygames ]</a></p><p style="color:#666; margin-top:5px line-height:1.5;">価格:<span style="font-size:14px; color:#C00; font-weight:bold;">9790円</span><br/><span style="font-size:10px; font-weight:normal;">(2024/2/10 12:00時点)</span><br/><span style="font-weight:bold;">感想(0件)</span></p></td></tr></tbody></table>
            <img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=3N237F+FM1BP6+2HOM+BWGDT" alt="">
            """,
        height=250,
        )

    with fpub3:
        stc.html(
            """
            <a target="_blank" href="https://www.amazon.co.jp/gp/search?ie=UTF8&tag=takishun03-22&linkCode=ur2&linkId=771c5c556c0a605e746208aa6bbe231d&camp=247&creative=1211&index=aps&keywords=幸運グッズ　競馬">幸運グッズ　競馬</a>
            """,
        height=250,
        )

    # pub1,pub2,pub3 = st.columns(3)
    # with pub1:
    #     stc.html('''
    #     <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3RQYKA+19NM+C03K1" rel="nofollow">
    #     <img border="0" width="200" height="125" alt="" src="https://www26.a8.net/svt/bgt?aid=230702425228&wid=006&eno=01&mid=s00000005917002016000&mc=1"></a>
    #     <img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=3TCR4P+3RQYKA+19NM+C03K1" alt="">''',
    #     height=130)
    #     st.markdown('<a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3RQYKA+19NM+BY642" rel="nofollow">【楽天競馬】が【楽天銀行（旧イーバンク銀行）】でご利用可能に！</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=3TCR4P+3RQYKA+19NM+BY642" alt="">',unsafe_allow_html=True)
    #
    # with pub2:
    #     stc.html("""
    #     <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3SXTRU+1JS2+6PJZL" rel="nofollow">
    #     <img border="0" width="125" height="125" alt="" src="https://www24.a8.net/svt/bgt?aid=230702425230&wid=006&eno=01&mid=s00000007229001127000&mc=1"></a>
    #     <img border="0" width="1" height="1" src="https://www18.a8.net/0.gif?a8mat=3TCR4P+3SXTRU+1JS2+6PJZL" alt="">        """,
    #     height=130)
    #     st.markdown('<a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3SXTRU+1JS2+5ZMCI" rel="nofollow">携帯電話でも地方競馬の馬券購入OK！</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=3TCR4P+3SXTRU+1JS2+5ZMCI" alt="">',unsafe_allow_html=True)
    #
    # with pub3:
    #     stc.html("""
    #     <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+7XS70A+1V0I+HW2Q9" rel="nofollow">
    #     <img border="0" width="125" height="125" alt="" src="https://www28.a8.net/svt/bgt?aid=230702425480&wid=006&eno=01&mid=s00000008685003005000&mc=1"></a>
    #     <img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=3TCR4P+7XS70A+1V0I+HW2Q9" alt="">""",height = 130)
    #     st.markdown('<a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+7XS70A+1V0I+HZ2R6" rel="nofollow">無料で勝馬予想！ <br>穴馬券を当てる！</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=3TCR4P+7XS70A+1V0I+HZ2R6" alt="">',unsafe_allow_html=True)

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
    #
    # stc.html("""
    # <body>
    # <!-- admax -->
    # <script src="https://adm.shinobi.jp/s/6658c80bd06583e1574c8c92c085b252"></script>
    # <!-- admax -->
    # </body>
    # """,height=100)
    #
    # stc.html("""
    # <body>
    # <!-- admax -->
    # <script src="https://adm.shinobi.jp/s/45435edce7e7017f98344e0a9b71123c"></script>
    # <!-- admax -->
    # </body>
    # """,height=60)
