#!/usr/bin/env python
# coding: utf-8
"""競馬期待値計算機(Streamlitアプリ)のエントリポイント。

    streamlit run oz_cal.py

確率・期待値の計算は baken.py、広告の描画は affiliates.py が担当し、
このファイルは画面の組み立てに専念する。
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import affiliates
import baken

try:
    # matplotlibに日本語フォントを設定する。グラフのラベル表示にしか関わらないので、
    # 導入されていない環境でもアプリ自体は動くようにしておく。
    import japanize_matplotlib  # noqa: F401
except ImportError:
    pass

GRID_COLUMNS = 3  # 期待値カードを並べる列数
MEMO_MARKS = ['', '◎', '◯', '△', '▲', '✕', '？']  # 馬メモの評価印（先頭の空欄＝未評価）


def render_metric_card(col, metrics: baken.BakenMetrics, bet: int) -> None:
    """1つの式別の期待値・的中確率・妙味判定を1列分表示する。"""
    col.subheader(metrics.name)
    col.metric(
        label=f'{metrics.name}期待値',
        value=round(metrics.expected_value, 2),
        delta=round(metrics.expected_value - bet, 2),
        help='期待値と、掛け金との差額。差額がプラスなら期待値プラスです。',
    )
    col.write(f'確率　{metrics.probability:.2f}%')
    col.write(f'損益分岐オッズ　{metrics.fair_odds:.2f}倍')
    if metrics.is_value:
        col.success('妙味あり（割安）')
    else:
        col.warning('妙味なし（割高）')


def render_metric_grid(results: list[baken.BakenMetrics], bet: int) -> None:
    """全式別の期待値カードをグリッド状に並べる。"""
    for start in range(0, len(results), GRID_COLUMNS):
        cols = st.columns(GRID_COLUMNS)
        for col, metrics in zip(cols, results[start:start + GRID_COLUMNS]):
            render_metric_card(col, metrics, bet)


def ranking_table(results: list[baken.BakenMetrics]) -> pd.DataFrame:
    """期待回収率の高い順に並べた比較表を作る。"""
    return pd.DataFrame(
        {
            '馬券': [m.name for m in results],
            '的中確率(%)': [round(m.probability, 2) for m in results],
            '損益分岐オッズ(倍)': [round(m.fair_odds, 2) for m in results],
            '期待値(円)': [round(m.expected_value, 2) for m in results],
            '期待回収率(%)': [round(m.payout_rate, 1) for m in results],
            '妙味': ['◎ 割安' if m.is_value else '× 割高' for m in results],
        }
    )


def breakeven_chart(name: str, odds: float, bet: int, horses: int):
    """期待値 vs オッズ を描画し、損益分岐オッズと利益ゾーンを示す。"""
    metrics = baken.calculate(name, odds, bet, horses)
    probability, fair_odds = metrics.probability, metrics.fair_odds

    x_max = max(fair_odds * 2, odds * 1.2, 1.0)
    xs = np.linspace(0, x_max, 200)
    ys = bet * xs * probability / 100  # 各オッズでの期待値(円)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(xs, ys, color='#1f77b4', label='期待値')
    ax.axhline(bet, color='gray', linestyle='--', label=f'掛け金 {bet}円（損益分岐）')
    ax.axvline(fair_odds, color='red', linestyle=':', label=f'損益分岐オッズ {fair_odds:.1f}倍')
    ax.fill_between(xs, bet, ys, where=(ys >= bet), color='green', alpha=0.15, label='利益ゾーン')

    ax.scatter([odds], [metrics.expected_value], color='black', zorder=5)
    ax.annotate(
        f'入力オッズ {odds:.1f}倍\n期待値 {metrics.expected_value:.1f}円',
        (odds, metrics.expected_value),
        textcoords='offset points',
        xytext=(10, 10),
        fontsize=8,
    )

    ax.set_xlabel('オッズ（倍）')
    ax.set_ylabel('期待値（円）')
    ax.set_title(f'{name} の損益分岐グラフ（{horses}頭・掛け金{bet}円）')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig, metrics


def render_guide() -> None:
    """使い方・計算方法・更新履歴を折りたたみで表示する。"""
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

            **計算方法**
            - 「全馬の実力が互角で着順は完全にランダム」と仮定し、
              買い目の組み合わせの数から的中確率を求めています。
            - 複勝は7頭以下のレースでは2着まで、8頭以上では3着までを的中としています。
            - 枠連は8つの枠への頭数の割り振りから買い目の数を数え、同じ枠の
              2頭が1着2着になる「ゾロ目」も買い目に含めています。
            - 出走頭数が少なく発売されない式別は表示されません。

            **注意**
            - 馬の特徴・馬場・距離・天気などの要素は考慮していませんので、
              参考程度にご利用ください。
            """
        )

    with st.expander('🆕 更新内容', expanded=False):
        st.markdown(
            """
            - **2026/08/18** 馬メモ（評価印・メモ）のタブを追加。1〜18番に◎◯△▲✕？を付けてCSV出力できます。
            - **2026/08/11** 的中確率の計算を見直しました。表示される確率・期待値・
              損益分岐オッズの値が以前と変わっています。
                - **ワイド** の的中確率が実際の2倍に表示されていた誤りを修正しました
                  （18頭立ての場合 3.92% → 1.96%）。ワイドは選んだ2頭がともに3着以内に
                  入れば的中で、着順は問わないため、当たりの組み合わせは3通りです。
                - **枠連** の的中確率を、出走頭数に応じた枠の割り振りから計算するよう
                  修正しました。以前は頭数によらず一定でした（10頭立ての場合
                  2.78% → 3.33%）。同じ枠の2頭が1着2着を占める「ゾロ目」も
                  買い目に含めています。
                - **複勝** は7頭以下のレースでは2着までが的中となるため、頭数に応じて
                  判定を切り替えるようにしました（7頭立ての場合 42.9% → 28.6%）。
                - 出走頭数が少なく発売されない馬券（5頭未満の複勝、9頭未満の枠連など）は
                  表示しないようにしました。以前は的中確率が100%を超えて表示されることが
                  ありました。
                - 入力できるオッズ・出走頭数・掛け金の範囲を実際のレースに合わせました。
            - **2026/06/17** 損益分岐グラフのタブを追加、アフィリエイトリンクを追加・更新
            - **2026/06/06** 妙味判定（損益分岐オッズ）と妙味ランキングを追加、使い方ガイドを整理
            - **2025/07/17** サイトURL、レイアウト更新
            """
        )


def render_inputs() -> tuple[float, int, int]:
    """オッズ・出走頭数・掛け金の入力欄を描画し、入力値を返す。"""
    odds = st.number_input(
        'オッズ', value=1.00, min_value=1.00, step=0.10,
        help='検討したい馬券のオッズ（払戻倍率）を入力してください。',
    )
    horses = st.number_input(
        '馬数', format='%d', value=baken.MAX_FIELD_SIZE,
        min_value=baken.MIN_FIELD_SIZE, max_value=baken.MAX_FIELD_SIZE,
        help='そのレースに出走する頭数です。',
    )
    bet = st.number_input(
        '掛け金', format='%d', value=100, min_value=100, step=100,
        help='1点あたりに賭ける金額（円）です。',
    )
    return odds, horses, bet


def render_ranking(results: list[baken.BakenMetrics]) -> None:
    """期待回収率の高い順に全式別を比較する。"""
    st.subheader('💡 妙味ランキング')
    ranked = sorted(results, key=lambda m: m.payout_rate, reverse=True)

    best = ranked[0]
    if best.is_value:
        st.success(
            f'最も妙味があるのは「{best.name}」です'
            f'（期待回収率 {best.payout_rate:.1f}%）。'
        )
    else:
        st.info(
            f'このオッズでは妙味のある馬券はありません。最も回収率が高いのは'
            f'「{best.name}」（{best.payout_rate:.1f}%）ですが、いずれも100%を下回ります。'
        )

    st.dataframe(ranking_table(ranked), hide_index=True, use_container_width=True)
    st.caption('※ 期待回収率 = 期待値 ÷ 掛け金 × 100。100%を超えるほど妙味があります。')


def render_chart_tab(odds: float, bet: int, horses: int) -> None:
    """損益分岐グラフのタブを描画する。"""
    st.subheader('📈 損益分岐グラフ')
    st.caption('馬券種を選ぶと、「オッズが何倍を超えれば利益（期待値プラス）になるか」を可視化します。')

    name = st.selectbox('馬券種を選択', baken.available_bet_types(horses), key='graph_baken')
    fig, metrics = breakeven_chart(name, odds, bet, horses)
    st.pyplot(fig)
    plt.close(fig)
    st.info(
        f'「{name}」（{horses}頭）の損益分岐オッズは {metrics.fair_odds:.2f}倍です。'
        f'入力オッズがこれを上回れば期待値プラス（妙味あり）になります。'
    )


def render_memo_tab() -> None:
    """1〜18番の各馬に評価印とメモを記入できるメモ機能のタブを描画する。"""
    st.subheader('📝 馬メモ')
    st.caption(
        '各馬（1〜18番）に評価印（◎◯△▲✕？）とメモを記入できます。'
        '印は選択式で自由入力はできません。「表をリセット」で全消去、「CSV出力」で書き出せます。'
    )

    # リセットは data_editor の key を作り直して中身を初期化することで実現する
    if 'memo_version' not in st.session_state:
        st.session_state.memo_version = 0
    if st.button('🗑 表をリセット', key='memo_reset'):
        st.session_state.memo_version += 1  # 以降で新しい key の editor が生成され空になる

    base = pd.DataFrame(
        {
            '馬番': list(range(1, baken.MAX_FIELD_SIZE + 1)),
            '印': [''] * baken.MAX_FIELD_SIZE,
            'メモ': [''] * baken.MAX_FIELD_SIZE,
        }
    )
    edited = st.data_editor(
        base,
        hide_index=True,
        num_rows='fixed',
        use_container_width=True,
        column_config={
            '馬番': st.column_config.NumberColumn(disabled=True, width='small'),
            '印': st.column_config.SelectboxColumn(options=MEMO_MARKS, width='small'),
            'メモ': st.column_config.TextColumn(width='large'),
        },
        key=f'memo_editor_{st.session_state.memo_version}',
    )

    csv = edited.to_csv(index=False).encode('utf-8-sig')  # Excel対応（BOM付きUTF-8）
    st.download_button(
        '⬇ CSV出力', data=csv, file_name='horse_memo.csv',
        mime='text/csv', key='memo_csv',
    )


def render_footer() -> None:
    """作成者情報とお問い合わせ先を表示する。"""
    st.text('作成者:eta')
    st.text('お問い合わせは下記まで')
    st.markdown(
        '<a target="_blank" rel="noopener" href="https://twitter.com/Psylibia_">Twitter</a>',
        unsafe_allow_html=True,
    )
    st.text('e-mail:shun.takinami.cr*gmail.com')
    st.text('「*」を[@]に読み換えてください。')


def main() -> None:
    st.set_page_config(
        page_title='競馬期待値カリキュレーター',
        page_icon='uma_icon.png',
        initial_sidebar_state='expanded',
        layout='wide',
    )

    st.title('競馬期待値計算機')
    st.caption(
        'オッズ・出馬数・掛け金を入力すると、馬券の種類ごとに期待値と'
        '「妙味（割安かどうか）」を計算します。'
    )

    render_guide()
    affiliates.render_text_links()

    st.write('---')
    odds, horses, bet = render_inputs()
    st.write('---')

    results = baken.calculate_all(odds, bet, horses)

    calc_tab, chart_tab, memo_tab = st.tabs(
        ['📊 期待値計算', '📈 損益分岐グラフ', '📝 馬メモ']
    )
    with calc_tab:
        render_metric_grid(results, bet)
        st.write('---')
        render_ranking(results)
    with chart_tab:
        render_chart_tab(odds, bet, horses)
    with memo_tab:
        render_memo_tab()

    st.write('---')
    affiliates.render_banners()

    st.write('---')
    render_footer()
    affiliates.render_closing_banner()


if __name__ == '__main__':
    main()
