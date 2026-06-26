#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib  # noqa: F401  matplotlibの日本語フォント対応
import streamlit as st
from scipy.special import comb
from scipy.special import perm
import streamlit.components.v1 as stc

# 表示する馬券の種類(表示順)
BET_TYPES = ['単勝', '複勝', '三連単', '三連複', '馬単', '馬連', 'ワイド', '枠連']


def baken_prob(name, horses):
    """馬券の種類ごとの的中確率(%)を出馬数から求める。"""
    return {
        '単勝': 100 / horses,
        '複勝': 100 * 3 / horses,
        '三連単': 100 / perm(horses, 3),
        '三連複': 100 / comb(horses, 3),
        '馬単': 100 / perm(horses, 2),
        '馬連': 100 / comb(horses, 2),
        'ワイド': 100 * perm(3, 2) / comb(horses, 2),
        '枠連': 100 / comb(9, 2),
    }[name]


def baken_metrics(name, bet, horses, number):
    """馬券1種類の期待値・確率・損益分岐オッズ・回収率をまとめて算出する。"""
    prob = baken_prob(name, horses)
    expected = bet * number * prob / 100
    fair_odds = 100 / prob  # 期待値が掛け金と等しくなる損益分岐(公正)オッズ
    payout_rate = number * prob  # 期待回収率(%) = 期待値 / 掛け金 × 100
    return {
        'name': name,
        'prob': prob,
        'expected': expected,
        'fair_odds': fair_odds,
        'payout_rate': payout_rate,
        'is_value': number >= fair_odds,
    }


def show_baken(col, name, bet, horses, number):
    """期待値( = 掛け金 × オッズ × 確率/100 )・的中確率・妙味判定を1列分表示する。"""
    m = baken_metrics(name, bet, horses, number)
    col.subheader(name)
    col.metric(
        label=name + '期待値',
        value=round(m['expected'], 2),
        delta=round(m['expected'] - bet, 2),
    )
    col.write('確率　' + str(round(m['prob'], 2)) + '%')
    col.write('損益分岐オッズ　' + str(round(m['fair_odds'], 2)) + '倍')
    if m['is_value']:
        col.success('妙味あり（割安）')
    else:
        col.warning('妙味なし（割高）')


def breakeven_chart(name, bet, horses, current_odds):
    """馬券種ごとに 期待値 vs オッズ を描画し、損益分岐オッズと利益ゾーンを示す。"""
    prob = baken_prob(name, horses)
    fair_odds = 100 / prob  # 期待値が掛け金と等しくなる損益分岐オッズ
    x_max = max(fair_odds * 2, current_odds * 1.2, 1.0)
    xs = np.linspace(0, x_max, 200)
    ys = bet * xs * prob / 100  # 各オッズでの期待値(円)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(xs, ys, color='#1f77b4', label='期待値')
    ax.axhline(bet, color='gray', linestyle='--', label=f'掛け金 {bet}円（損益分岐）')
    ax.axvline(fair_odds, color='red', linestyle=':', label=f'損益分岐オッズ {fair_odds:.1f}倍')
    ax.fill_between(xs, bet, ys, where=(ys >= bet), color='green', alpha=0.15, label='利益ゾーン')

    cur_ev = bet * current_odds * prob / 100
    ax.scatter([current_odds], [cur_ev], color='black', zorder=5)
    ax.annotate(
        f'入力オッズ {current_odds:.1f}倍\n期待値 {cur_ev:.1f}円',
        (current_odds, cur_ev), textcoords='offset points', xytext=(10, 10), fontsize=8,
    )

    ax.set_xlabel('オッズ（倍）')
    ax.set_ylabel('期待値（円）')
    ax.set_title(f'{name} の損益分岐グラフ（{horses}頭・掛け金{bet}円）')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig, fair_odds

if __name__ == "__main__":
    st.set_page_config(
        page_title="競馬期待値カリキュレーター",
        page_icon="uma_icon.png",
        initial_sidebar_state="expanded",
        layout="wide"
    )

    st.title('競馬期待値計算機')
    st.caption('オッズ・出馬数・掛け金を入力すると、馬券の種類ごとに期待値と「妙味（割安かどうか）」を計算します。')

    with st.expander('📖 使い方・計算方法・注意事項', expanded=False):
        st.markdown(
            """
            **使い方**
            1. 検討したい馬券の **オッズ** を入力します。
            2. レースの **出馬数** を選びます。
            3. 賭けたい **掛け金** を入力します。

            **見方**
            - **期待値** … 掛け金 × オッズ × 的中確率。下の差分が＋なら期待値プラスです。
            - **損益分岐オッズ** … 期待値が掛け金とちょうど等しくなる理論上の公正オッズ。
            - **妙味判定** … 入力オッズが損益分岐オッズを上回れば「妙味あり（割安）」と判定します。
            - **妙味ランキング** … 全馬券を期待回収率の高い順に並べ、最も妙味のある馬券を表示します。

            **注意**
            - 単純にレースの出馬数に応じた賭け方別の組み合わせから確率を求めたものです。
            - 馬の特徴・馬場・距離・天気などの要素は考慮していませんので、参考程度にご利用ください。
            """
        )

    with st.expander('🆕 更新内容', expanded=False):
        st.markdown(
            """
            - **2026/06/17** 損益分岐グラフのタブを追加（画面をタブ構成に変更）、アフィリエイトリンクを追加・更新
            - **2026/06/06** 妙味判定（損益分岐オッズ）と妙味ランキングを追加、使い方ガイドを整理
            - **2025/07/17** サイトURL、レイアウト更新
            """
        )

    st.markdown('<a target="_blank" href="https://www.jra.go.jp/">JRA公式サイト</a>',unsafe_allow_html=True)
    st.markdown('<a target="_blank" href="https://amzn.to/4coJX86">ウマ娘を見るならAmazonPrimeVideo</a>',unsafe_allow_html=True)

    st.write('---')

    number = st.number_input('オッズ', value=1.00,
                             help='検討したい馬券のオッズ（払戻倍率）を入力してください。')
    horses = st.number_input('馬数', format='%d', value=18, min_value=1, max_value=18,
                             help='そのレースに出走する頭数です。')
    bet = st.number_input('掛け金', format='%d', value=100, min_value=0,
                          help='1点あたりに賭ける金額（円）です。')

    st.write('---')

    tab1, tab2 = st.tabs(['📊 期待値計算', '📈 損益分岐グラフ'])

    with tab1:
        # 単勝、複勝
        col1, col2, colex = st.columns(3)
        show_baken(col1, '単勝', bet, horses, number)
        show_baken(col2, '複勝', bet, horses, number)

        # 三連単、三連複、馬単
        col3, col4, colex2 = st.columns(3)
        show_baken(col3, '三連単', bet, horses, number)
        show_baken(col4, '三連複', bet, horses, number)
        show_baken(colex2, '馬単', bet, horses, number)

        # 枠連、馬連、ワイド
        col5, col6, col7 = st.columns(3)
        show_baken(col5, '枠連', bet, horses, number)
        show_baken(col6, '馬連', bet, horses, number)
        show_baken(col7, 'ワイド', bet, horses, number)

        st.write('---')

        # 妙味ランキング: 全馬券を期待回収率の高い順に並べて比較する
        st.subheader('💡 妙味ランキング')
        metrics = [baken_metrics(name, bet, horses, number) for name in BET_TYPES]
        metrics.sort(key=lambda m: m['payout_rate'], reverse=True)

        best = metrics[0]
        if best['is_value']:
            st.success(
                f"最も妙味があるのは「{best['name']}」です（期待回収率 {best['payout_rate']:.1f}%）。"
            )
        else:
            st.info(
                f"このオッズでは妙味のある馬券はありません。最も回収率が高いのは「{best['name']}」"
                f"（{best['payout_rate']:.1f}%）ですが、いずれも100%を下回ります。"
            )

        ranking = pd.DataFrame(
            {
                '馬券': [m['name'] for m in metrics],
                '的中確率(%)': [round(m['prob'], 2) for m in metrics],
                '損益分岐オッズ(倍)': [round(m['fair_odds'], 2) for m in metrics],
                '期待値(円)': [round(m['expected'], 2) for m in metrics],
                '期待回収率(%)': [round(m['payout_rate'], 1) for m in metrics],
                '妙味': ['◎ 割安' if m['is_value'] else '× 割高' for m in metrics],
            }
        )
        st.dataframe(ranking, hide_index=True, use_container_width=True)
        st.caption('※ 期待回収率 = 期待値 ÷ 掛け金 × 100。100%を超えるほど妙味があります。')

    with tab2:
        st.subheader('📈 損益分岐グラフ')
        st.caption('馬券種を選ぶと、「オッズが何倍を超えれば利益（期待値プラス）になるか」を可視化します。')
        graph_name = st.selectbox('馬券種を選択', BET_TYPES, key='graph_baken')
        fig, fair_odds = breakeven_chart(graph_name, bet, horses, number)
        st.pyplot(fig)
        plt.close(fig)
        st.info(
            f'「{graph_name}」（{horses}頭）の損益分岐オッズは {fair_odds:.2f}倍です。'
            f'入力オッズがこれを上回れば期待値プラス（妙味あり）になります。'
        )

    st.write('---')
    fpub1,fpub2,fpub3 = st.columns(3)

    with fpub1:
        stc.html(
            """
            <a href="https://px.a8.net/svt/ejp?a8mat=4B5YSD+5YC6EY+4JVQ+614CX" rel="nofollow">
            <img border="0" width="300" height="250" alt="" src="https://www25.a8.net/svt/bgt?aid=260618845360&wid=006&eno=01&mid=s00000021239001013000&mc=1"></a>
            <img border="0" width="1" height="1" src="https://www18.a8.net/0.gif?a8mat=4B5YSD+5YC6EY+4JVQ+614CX" alt="">
            """,
            height=260,
        )
        stc.html(
            """
            <a href="https://px.a8.net/svt/ejp?a8mat=45GG1D+2RFINU+4RKY+63H8H" rel="nofollow">
            <img border="0" width="300" height="250" alt="" src="https://www20.a8.net/svt/bgt?aid=251030065167&wid=006&eno=01&mid=s00000022237001024000&mc=1"></a>
            <img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=45GG1D+2RFINU+4RKY+63H8H" alt="">
            """,
            height=260,
        )

    with fpub2:
        stc.html(
            """
            <a href="https://px.a8.net/svt/ejp?a8mat=4B5YSD+5XQQT6+2Z0I+IHXRL" rel="nofollow">
            <img border="0" width="300" height="250" alt="" src="https://www23.a8.net/svt/bgt?aid=260618845359&wid=006&eno=01&mid=s00000013869003107000&mc=1"></a>
            <img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B5YSD+5XQQT6+2Z0I+IHXRL" alt="">
            """,
            height=260,
        )
        stc.html(
            """
            <a href="https://px.a8.net/svt/ejp?a8mat=3NF11N+2A5Y4A+2PEO+1I4AW1" rel="nofollow">
            <img border="0" width="300" height="250" alt="" src="https://www24.a8.net/svt/bgt?aid=220730891138&wid=006&eno=01&mid=s00000012624009090000&mc=1"></a>
            <img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=3NF11N+2A5Y4A+2PEO+1I4AW1" alt="">
            """,
            height=260,
        )

    with fpub3:
        stc.html(
            """
            <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3RQYKA+19NM+C03K1" rel="nofollow">
            <img border="0" width="300" height="250" alt="" src="https://www22.a8.net/svt/bgt?aid=230702425228&wid=006&eno=01&mid=s00000005917002016000&mc=1"></a>
            <img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=3TCR4P+3RQYKA+19NM+C03K1" alt="">
            """,
        height=250,
        )
        stc.html(
            """
            <a href="https://px.a8.net/svt/ejp?a8mat=4B5YSD+4W8FP6+3IB8+609HT" rel="nofollow">
            <img border="0" width="250" height="250" alt="" src="https://www27.a8.net/svt/bgt?aid=260618845296&wid=006&eno=01&mid=s00000016370001009000&mc=1"></a>
            <img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B5YSD+4W8FP6+3IB8+609HT" alt="">
            """,
            height=260,
        )

    st.write('---')
    st.text('作成者:eta')
    st.text('お問い合わせは下記まで')
    st.markdown('<a href = "https://twitter.com/Psylibia_">Twitter</a>',unsafe_allow_html=True)
    st.text('e-mail:shun.takinami.cr*gmail.com')
    st.text('「*」を[@]に読み換えてください。')

    stc.html("""
    <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+7YZ27U+47AY+601S1" rel="nofollow">
    <img border="0" width="300" height="250" alt="" src="https://www29.a8.net/svt/bgt?aid=230702425482&wid=006&eno=01&mid=s00000019609001008000&mc=1"></a>
    <img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=3TCR4P+7YZ27U+47AY+601S1" alt="">
    """)

def afil():
    st.title('競馬で勝ったらウマ娘！')
    st.text('競馬で勝ったらウマ娘グッズを買おう！')

    pub1,pub2,pub3 = st.columns(3)
    with pub1:
        # stc.html('''
        # <a href="'" rel="nofollow">
        # ''',
        # height=130)
        st.markdown('<a href="https://www.amazon.co.jp/%E3%83%97%E3%83%AA%E3%83%86%E3%82%A3%E3%83%BC%E3%83%80%E3%83%BC%E3%83%93%E3%83%BC-Blu-ray-%E3%82%B7%E3%83%BC%E3%82%BA%E3%83%B31%EF%BD%9E3-Road-6%E6%9E%9A%E7%BB%842BOX/dp/B0DP3N88W8?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&crid=1KSVDKM50RH0F&dib=eyJ2IjoiMSJ9.Nsw8AgZcm-Y7wfqw-1g8ApHyze9WkvJFwlsbEDCZETIFnIX0R98bbdLsq32szz33qFGty_aW39N4UO6dLe6NPLj9x9Ee1ycy-MF45w77HxRA0eAL1mU4Co4qZa9t0Q6hgzXPMVZm7delsiPwaEnlwx0LRteoRCyVQToUhL7CmbnlbxsycEX7qRRQq5sj7qB_8kgqg9ADZcRWZ--Jg3qZ_T_kBnP7mmByqOsIpqYGRJYFRRsprekh6fTcf4DtuTBbgxXtCg6Z35dIUgYwgwsRCgc3bWnieC7U-MKprSxBDEg.o06tIcWrOXqhZY0S5602312lOWiXqFVyeCpcHZHzgm8&dib_tag=se&keywords=%E3%82%A6%E3%83%9E%E5%A8%98&qid=1733034522&sprefix=%E3%82%A6%E3%83%9E%E5%A8%98%2Caps%2C190&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1&linkCode=ll1&tag=takishun03-22&linkId=2d1fa6e4e309668d1680d9937012e122&language=ja_JP&ref_=as_li_ss_tl" rel="nofollow">ウマ娘 プリティーダービー Blu-ray シーズン1～3+OVA+Road to the Top 完全版 6枚组2BOX</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=3TCR4P+3RQYKA+19NM+BY642" alt="">',unsafe_allow_html=True)

        st.markdown('<a target="_blank" href="https://amzn.to/4coJX86">ウマ娘を見るならAmazonPrimeVideo</a>',unsafe_allow_html=True)
        st.markdown('<a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3SXTRU+1JS2+5ZMCI" rel="nofollow">携帯電話でも地方競馬の馬券購入OK！</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=3TCR4P+3SXTRU+1JS2+5ZMCI" alt="">',unsafe_allow_html=True)

    with pub2:
        stc.html("""
        <a href="https://px.a8.net/svt/ejp?a8mat=3ZLSFE+LFQEY+5ERO+5YZ75" rel="nofollow">
        <img border="0" width="300" height="250" alt="" src="https://www25.a8.net/svt/bgt?aid=241201706036&wid=006&eno=01&mid=s00000025242001003000&mc=1"></a>
        <img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=3ZLSFE+LFQEY+5ERO+5YZ75" alt="">
        """,height=250)

        stc.html(
            """
            <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3RQYKA+19NM+C03K1" rel="nofollow">
            <img border="0" width="300" height="250" alt="" src="https://www22.a8.net/svt/bgt?aid=230702425228&wid=006&eno=01&mid=s00000005917002016000&mc=1"></a>
            <img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=3TCR4P+3RQYKA+19NM+C03K1" alt="">
            """,
        height=250,
        )


    with pub3:
        stc.html("""
        <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+7XS70A+1V0I+HW2Q9" rel="nofollow">
        <img border="0" width="125" height="125" alt="" src="https://www28.a8.net/svt/bgt?aid=230702425480&wid=006&eno=01&mid=s00000008685003005000&mc=1"></a>
        <img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=3TCR4P+7XS70A+1V0I+HW2Q9" alt="">""",height = 130)
        st.markdown('<a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+7XS70A+1V0I+HZ2R6" rel="nofollow"></a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=3TCR4P+7XS70A+1V0I+HZ2R6" alt="">',unsafe_allow_html=True)

        stc.html("""
        <a href="https://px.a8.net/svt/ejp?a8mat=3TCR4P+3SXTRU+1JS2+6PJZL" rel="nofollow">
        <img border="0" width="125" height="125" alt="" src="https://www24.a8.net/svt/bgt?aid=230702425230&wid=006&eno=01&mid=s00000007229001127000&mc=1"></a>
        <img border="0" width="1" height="1" src="https://www18.a8.net/0.gif?a8mat=3TCR4P+3SXTRU+1JS2+6PJZL" alt="">        """,
        height=130)

        stc.html(
        """
        <!-- Rakuten Widget FROM HERE --><script type="text/javascript">rakuten_affiliateId="0ea62065.34400275.0ea62066.204f04c0";rakuten_items="ranking";rakuten_genreId="568591";rakuten_recommend="on";rakuten_design="slide";rakuten_size="120x240";rakuten_target="_blank";rakuten_border="on";rakuten_auto_mode="on";rakuten_adNetworkId="a8Net";rakuten_adNetworkUrl="https%3A%2F%2Frpx.a8.net%2Fsvt%2Fejp%3Fa8mat%3D3N237F%2BFM1BP6%2B2HOM%2BBS629%26rakuten%3Dy%26a8ejpredirect%3D";rakuten_pointbackId="a22012721403_3N237F_FM1BP6_2HOM_BS629";rakuten_mediaId="20011816";</script><script type="text/javascript" src="//xml.affiliate.rakuten.co.jp/widget/js/rakuten_widget.js"></script><!-- Rakuten Widget TO HERE -->
        <img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=3N237F+FM1BP6+2HOM+BS629" alt="">
        """,
        height=250,
        )

    stc.html("""
    <iframe class="note-embed" src="https://note.com/embed/notes/nd947001a1104" style="border: 0; display: block; max-width: 99%; width: 494px; padding: 0px; margin: 10px 0px; position: static; visibility: visible;" height="400"></iframe><script async src="https://note.com/scripts/embed.js" charset="utf-8"></script>
    """, height=420)
