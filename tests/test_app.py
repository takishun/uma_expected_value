"""Streamlitアプリが例外なく描画できることを確認するテスト。"""

import pytest
from streamlit.testing.v1 import AppTest

import baken

APP = 'oz_cal.py'
TIMEOUT = 30


def run_app(odds=None, horses=None, bet=None) -> AppTest:
    """アプリを起動し、必要なら入力値を変えて再実行した結果を返す。"""
    app = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    if odds is not None:
        app.number_input[0].set_value(odds)
    if horses is not None:
        app.number_input[1].set_value(horses)
    if bet is not None:
        app.number_input[2].set_value(bet)
    if any(value is not None for value in (odds, horses, bet)):
        app = app.run()
    assert not app.exception
    return app


def test_初期表示で例外が出ない():
    app = run_app()
    assert app.title[0].value == '競馬期待値計算サイト'


@pytest.mark.parametrize('horses', range(baken.MIN_FIELD_SIZE, baken.MAX_FIELD_SIZE + 1))
def test_どの頭数でも例外が出ない(horses):
    run_app(horses=horses)


def ranking_markup(app: AppTest) -> str:
    """式別一覧として書き出されたHTMLを1つの文字列にまとめて返す。"""
    return '\n'.join(md.value for md in app.markdown)


def test_発売される式別の数だけカードが並ぶ():
    app = run_app(horses=8)
    markup = ranking_markup(app)
    for name in baken.available_bet_types(8):
        assert f'class="ev-name">{name}<' in markup
    # 8頭立てでは枠連は発売されないのでカードも出ない
    assert 'class="ev-name">枠連<' not in markup


def test_妙味のある式別だけが強調される():
    app = run_app(horses=18, odds=5000.0)
    markup = ranking_markup(app)
    # 妙味ありのカードは is-value が付き、判定も「割安」になる
    assert 'ev-row is-value' in markup
    assert '◎ 割安' in markup


def test_妙味ランキングは期待回収率の高い順に並ぶ():
    app = run_app(horses=18, odds=100.0)
    table = app.dataframe[0].value
    rates = list(table['期待回収率(%)'])
    assert rates == sorted(rates, reverse=True)
    assert len(table) == len(baken.BET_TYPES)


def test_高オッズなら妙味ありと判定される():
    app = run_app(horses=18, odds=5000.0)
    assert any('最も妙味があるのは' in msg.value for msg in app.success)


def test_低オッズなら妙味なしと案内される():
    app = run_app(horses=18, odds=1.0)
    assert any('妙味のある馬券はありません' in msg.value for msg in app.info)


def test_期待値計算だけの1画面でタブはない():
    app = run_app()
    assert len(app.tabs) == 0
    assert len(app.selectbox) == 0  # 損益分岐グラフの式別選択
    assert len(app.button) == 0  # 馬メモのリセットボタン


def test_PR欄は更新内容のすぐ下に並ぶ():
    app = run_app()
    # 間にテキストリンクなどが挟まらないよう、ページ直下の全要素の並びで確かめる
    labels = [getattr(node, 'label', None) for node in app.main.children.values()]
    assert labels.index('🎁 PR・関連サービス') == labels.index('🆕 更新内容') + 1


def test_テキストリンクはPR欄の中にある():
    app = run_app()
    pr_section = next(e for e in app.expander if e.label == '🎁 PR・関連サービス')
    links = '\n'.join(md.value for md in pr_section.markdown)
    assert 'JRA公式サイト' in links
