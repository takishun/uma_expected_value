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
    assert app.title[0].value == '競馬期待値計算機'


@pytest.mark.parametrize('horses', range(baken.MIN_FIELD_SIZE, baken.MAX_FIELD_SIZE + 1))
def test_どの頭数でも例外が出ない(horses):
    run_app(horses=horses)


def test_発売される式別の数だけ期待値カードが並ぶ():
    app = run_app(horses=8)
    expected = baken.available_bet_types(8)
    headers = [h.value for h in app.subheader]
    for name in expected:
        assert name in headers
    assert '枠連' not in headers


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


def test_グラフタブの選択肢は発売される式別だけ():
    app = run_app(horses=8)
    assert app.selectbox[0].options == baken.available_bet_types(8)
