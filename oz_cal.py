#!/usr/bin/env python
# coding: utf-8
"""馬券バリューチェッカー(Streamlitアプリ)のエントリポイント。

    streamlit run oz_cal.py

確率・期待値の計算は baken.py、広告の描画は affiliates.py、
スマートフォン向けの配色とスタイルは theme.py が担当し、
このファイルは画面の組み立てに専念する。

画面はスマートフォンを基準に組んでいる(design/mobile-layout-proposals.html の案A)。
1行=1式別のカードを期待回収率の高い順に縦へ積み、入力欄は画面上部に固定する。
"""

import html

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import affiliates
import baken
import theme

try:
    # matplotlibに日本語フォントを設定する。グラフのラベル表示にしか関わらないので、
    # 導入されていない環境でもアプリ自体は動くようにしておく。
    import japanize_matplotlib  # noqa: F401
except ImportError:
    pass

MEMO_MARKS = ['', '◎', '◯', '△', '▲', '✕', '？']  # 馬メモの評価印（先頭の空欄＝未評価）

DEFAULT_ODDS = 20.00  # 初期表示で妙味あり・なしが混ざり、見方が伝わる値にしておく


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


def ranking_rows_html(results: list[baken.BakenMetrics]) -> str:
    """式別カードを縦に積んだ一覧のHTMLを組み立てる。

    Streamlitの標準部品では1行に「式別名・内訳・期待回収率・バー」を
    収めきれないため、この一覧だけHTMLを直接書き出している。
    """
    rows = []
    for metrics in results:
        modifier = ' is-value' if metrics.is_value else ''
        judgement = '◎ 割安' if metrics.is_value else '× 割高'
        # 狭い画面でも1行に収まるよう、左側は的中確率と損益分岐オッズだけにする
        meta = f'的中 {metrics.probability:.2f}%・分岐 {metrics.fair_odds:.1f}倍'
        rows.append(
            f'<li class="ev-row{modifier}">'
            f'<span class="ev-name">{html.escape(metrics.name)}</span>'
            f'<span class="ev-meta">{html.escape(meta)}</span>'
            f'<span class="ev-value">'
            f'<b>{metrics.payout_rate:.1f}<em>%</em></b>'
            f'<i>{judgement}</i>'
            f'<u>期待値 {metrics.expected_value:.0f}円</u>'
            f'</span>'
            f'<span class="ev-track">'
            f'<span style="width:{theme.bar_width(metrics.payout_rate):.1f}%"></span>'
            f'</span>'
            f'</li>'
        )
    return f'<ul class="ev-list">{"".join(rows)}</ul>'


def summary_html(results: list[baken.BakenMetrics]) -> str:
    """「妙味あり N / M 券種」のサマリー行のHTMLを組み立てる。"""
    hits = sum(1 for metrics in results if metrics.is_value)
    css_class = '' if hits else ' class="ev-summary-flat"'
    return (
        f'<div class="ev-summary">妙味あり '
        f'<strong{css_class}>{hits} / {len(results)}</strong> 券種</div>'
    )


def breakeven_chart(name: str, odds: float, bet: int, horses: int):
    """期待値 vs オッズ を描画し、損益分岐オッズと利益ゾーンを示す。"""
    metrics = baken.calculate(name, odds, bet, horses)
    probability, fair_odds = metrics.probability, metrics.fair_odds

    x_max = max(fair_odds * 2, odds * 1.2, 1.0)
    xs = np.linspace(0, x_max, 200)
    ys = bet * xs * probability / 100  # 各オッズでの期待値(円)

    palette = theme.PALETTE
    # スマートフォンの画面幅に収まる比率にし、暗い背景になじむ配色にする
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    fig.patch.set_facecolor(palette['card'])
    ax.set_facecolor(palette['card'])

    ax.plot(xs, ys, color=palette['green'], linewidth=2, label='期待値')
    ax.axhline(bet, color=palette['muted'], linestyle='--', linewidth=1,
               label=f'掛け金 {bet}円（損益分岐）')
    ax.axvline(fair_odds, color=palette['amber'], linestyle=':', linewidth=1.2,
               label=f'損益分岐オッズ {fair_odds:.1f}倍')
    ax.fill_between(xs, bet, ys, where=(ys >= bet), color=palette['green'], alpha=0.18,
                    label='利益ゾーン')

    ax.scatter([odds], [metrics.expected_value], color=palette['text'],
               edgecolors=palette['card'], linewidths=1.5, zorder=5)
    ax.annotate(
        f'入力オッズ {odds:.1f}倍\n期待値 {metrics.expected_value:.1f}円',
        (odds, metrics.expected_value),
        textcoords='offset points',
        xytext=(8, 8),
        fontsize=8,
        color=palette['text'],
    )

    ax.set_xlabel('オッズ（倍）', color=palette['muted'], fontsize=9)
    ax.set_ylabel('期待値（円）', color=palette['muted'], fontsize=9)
    ax.set_title(f'{name}（{horses}頭・掛け金{bet}円）', color=palette['text'], fontsize=11)
    ax.tick_params(colors=palette['muted'], labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(palette['line_strong'])
    legend = ax.legend(loc='upper left', fontsize=7.5, framealpha=0.85,
                       facecolor=palette['surface'], edgecolor=palette['line_strong'])
    for text in legend.get_texts():
        text.set_color(palette['text'])
    ax.grid(color=palette['line_strong'], alpha=0.6)
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
            - **期待回収率** … 期待値 ÷ 掛け金 × 100。一覧はこの高い順に並びます。
              バーの中央の縦線が100%（損益分岐）で、これを超えると緑色になります。
            - **期待値** … 掛け金 × オッズ × 的中確率。掛け金を上回れば期待値プラスです。
            - **損益分岐オッズ** … 期待値が掛け金とちょうど等しくなる理論上の公正オッズ。
            - **妙味判定** … 入力オッズが損益分岐オッズを上回れば「◎ 割安」と判定します。

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
            - **2026/08/24** スマートフォン向けにレイアウトを刷新しました。式別を
              期待回収率の高い順に縦1列で並べ、オッズなどの入力欄を画面上部に
              固定しています（従来は3列表示のため、スマホでは数値が折り返していました）。
            - **2026/08/19** アプリ名を「馬券バリューチェッカー」に変更しました。
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
    """オッズ・出走頭数・掛け金の入力欄を、画面上部に固定した3列で描画する。

    列の1つ目に置いた目印をCSSが見つけて、この横並びブロックだけを固定する。
    """
    odds_col, horses_col, bet_col = st.columns(3)

    with odds_col:
        theme.sticky_anchor()
        odds = st.number_input(
            'オッズ', value=DEFAULT_ODDS, min_value=1.00, step=0.10,
            help='検討したい馬券のオッズ（払戻倍率）を入力してください。',
        )
    with horses_col:
        horses = st.number_input(
            '頭数', format='%d', value=baken.MAX_FIELD_SIZE,
            min_value=baken.MIN_FIELD_SIZE, max_value=baken.MAX_FIELD_SIZE,
            help='そのレースに出走する頭数です。',
        )
    with bet_col:
        bet = st.number_input(
            '掛け金', format='%d', value=100, min_value=100, step=100,
            help='1点あたりに賭ける金額（円）です。',
        )
    return odds, horses, bet


def render_ranking(results: list[baken.BakenMetrics]) -> None:
    """期待回収率の高い順に全式別を縦1列で比較する。"""
    ranked = sorted(results, key=lambda m: m.payout_rate, reverse=True)

    st.markdown(summary_html(ranked), unsafe_allow_html=True)

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

    st.markdown(ranking_rows_html(ranked), unsafe_allow_html=True)
    st.caption('※ バーの中央の縦線が期待回収率100%（損益分岐）です。')

    with st.expander('📋 数値を表で見る', expanded=False):
        st.dataframe(ranking_table(ranked), hide_index=True, use_container_width=True)


def render_chart_tab(odds: float, bet: int, horses: int) -> None:
    """損益分岐グラフのタブを描画する。"""
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
        page_title='馬券バリューチェッカー',
        page_icon='uma_icon.png',
        initial_sidebar_state='collapsed',
        layout='centered',
    )
    theme.inject()

    st.title('馬券バリューチェッカー')
    st.caption('オッズ・頭数・掛け金を入れると、どの馬券が割安かを期待回収率の順に並べます。')

    odds, horses, bet = render_inputs()
    results = baken.calculate_all(odds, bet, horses)

    calc_tab, chart_tab, memo_tab = st.tabs(
        ['📊 期待値計算', '📈 損益分岐グラフ', '📝 馬メモ']
    )
    with calc_tab:
        render_ranking(results)
    with chart_tab:
        render_chart_tab(odds, bet, horses)
    with memo_tab:
        render_memo_tab()

    st.write('---')
    render_guide()
    affiliates.render_text_links()

    # 広告はスマホでは横に3列並べられないため、1列にして折りたたむ
    with st.expander('🎁 PR・関連サービス', expanded=False):
        affiliates.render_banners(columns=1)
        affiliates.render_closing_banner()

    st.write('---')
    render_footer()


if __name__ == '__main__':
    main()
