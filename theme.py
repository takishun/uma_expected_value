"""スマートフォン向け「オッズ掲示板」レイアウトの配色とスタイル。

design/mobile-layout-proposals.html の案A（Odds Board）を実装したもの。
競馬場のオッズ表示板を模したダーク基調で、1行=1式別のカードを縦に積む。

Streamlitの標準部品だけでは行カードを表現できないため、CSSと一部のHTMLを
このモジュールに集約し、oz_cal.py は画面の組み立てに専念できるようにする。
"""

import streamlit as st

# 案Aの配色。値を変えるときは .streamlit/config.toml のテーマも合わせて更新する。
PALETTE = {
    'bg': '#0D110C',  # 画面全体の地
    'surface': '#171E16',  # 入力欄・補助パネル
    'card': '#141A13',  # 式別カード（妙味なし）
    'card_good': '#131E16',  # 式別カード（妙味あり）
    'line': '#212A20',  # 罫線
    'line_strong': '#263024',  # やや強い罫線
    'muted': '#7C8A76',  # 補助テキスト
    'text': '#E3E8DE',  # 本文
    'amber': '#F2C755',  # 入力値（オッズ表示板の琥珀色）
    'green': '#7FD09B',  # 妙味ありの数値
    'bar': '#4FA96F',  # 妙味ありのバー
    'bar_dim': '#47604A',  # 妙味なしのバー
    'track': '#232C21',  # バーの下地
}

# 期待回収率をバーの長さに変換するときの上限(%)。
# トラックの中央(50%)がちょうど回収率100%＝損益分岐になる。
BAR_FULL_SCALE = 200.0

_CSS = """
<style>
:root {
  --ev-bg: #0D110C;
  --ev-surface: #171E16;
  --ev-card: #141A13;
  --ev-card-good: #131E16;
  --ev-line: #212A20;
  --ev-line-strong: #263024;
  --ev-muted: #7C8A76;
  --ev-text: #E3E8DE;
  --ev-amber: #F2C755;
  --ev-green: #7FD09B;
  --ev-bar: #4FA96F;
  --ev-bar-dim: #47604A;
  --ev-track: #232C21;
  --ev-mono: ui-monospace, "SF Mono", "SFMono-Regular", Menlo, "DejaVu Sans Mono", monospace;
}

/* Streamlit標準のヘッダーは公開アプリでは使わない。
   隠すことで入力バーを画面最上部にぴたりと固定できる。 */
header[data-testid="stHeader"] { display: none; }

/* スマホ幅を基準に、本文の余白を詰めて1画面の情報量を増やす */
.block-container {
  max-width: 46rem;
  padding-top: 1.1rem;
  padding-bottom: 2.5rem;
}
@media (max-width: 640px) {
  .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
}

h1 {
  font-size: 1.4rem !important;
  letter-spacing: 0.04em;
  padding-top: 0 !important;
  padding-bottom: 0.2rem !important;
}

/* ---------- 入力バー（画面上部に固定） ---------- */
/* 目印のspanを含む横並びブロックだけを対象にする。:has()が効かない
   ブラウザでは通常の入力欄として表示されるだけで、機能は損なわれない。 */
div[data-testid="stHorizontalBlock"]:has(span.ev-sticky-anchor) {
  position: sticky;
  top: 0;
  z-index: 100;
  flex-wrap: nowrap;
  gap: 0.5rem;
  background: var(--ev-bg);
  border-bottom: 1px solid var(--ev-line);
  padding: 0.5rem 0 0.65rem;
  margin-bottom: 0.4rem;
}
/* 目印そのものは高さを持たせない */
div[data-testid="stElementContainer"]:has(span.ev-sticky-anchor),
div[data-testid="element-container"]:has(span.ev-sticky-anchor) {
  display: none;
}
/* Streamlitはスマホ幅で列に min-width:100% を与えて縦積みにする。
   入力バーは3項目を横に並べたいので、その指定だけを打ち消す。 */
div[data-testid="stHorizontalBlock"]:has(span.ev-sticky-anchor) > div[data-testid="stColumn"] {
  min-width: 0 !important;
  flex: 1 1 0 !important;
}
/* 幅が狭いので増減ボタンは省き、数値の入力に絞る */
div[data-testid="stHorizontalBlock"]:has(span.ev-sticky-anchor)
  [data-testid="stNumberInputStepUp"],
div[data-testid="stHorizontalBlock"]:has(span.ev-sticky-anchor)
  [data-testid="stNumberInputStepDown"] {
  display: none;
}
div[data-testid="stHorizontalBlock"]:has(span.ev-sticky-anchor) label p {
  font-size: 0.72rem !important;
  letter-spacing: 0.08em;
  color: var(--ev-muted) !important;
}
div[data-testid="stHorizontalBlock"]:has(span.ev-sticky-anchor) input {
  font-family: var(--ev-mono);
  font-variant-numeric: tabular-nums;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ev-amber) !important;
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
}

/* ---------- 妙味サマリー ---------- */
.ev-summary {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  color: var(--ev-muted);
  margin: 0.2rem 0 0.7rem;
}
.ev-summary strong {
  font-family: var(--ev-mono);
  font-size: 0.95rem;
  color: var(--ev-green);
}
.ev-summary .ev-summary-flat { color: var(--ev-muted); }

/* ---------- 式別カード（1行=1式別） ---------- */
.ev-list {
  list-style: none;
  margin: 0 0 0.6rem;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.ev-row {
  background: var(--ev-card);
  border: 1px solid var(--ev-line);
  border-left: 3px solid #33402F;
  border-radius: 7px;
  padding: 10px 12px 11px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 2px 10px;
  align-items: center;
}
.ev-row.is-value {
  background: var(--ev-card-good);
  border-left-color: var(--ev-bar);
}
.ev-name {
  grid-column: 1;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--ev-text);
}
.ev-meta {
  grid-column: 1;
  font-family: var(--ev-mono);
  font-variant-numeric: tabular-nums;
  font-size: 0.66rem;
  color: var(--ev-muted);
}
.ev-value {
  grid-column: 2;
  grid-row: 1 / span 2;
  text-align: right;
}
.ev-value b {
  display: block;
  font-family: var(--ev-mono);
  font-variant-numeric: tabular-nums;
  font-size: 1.32rem;
  font-weight: 600;
  line-height: 1.1;
  color: #C9D3C2;
}
.ev-row.is-value .ev-value b { color: var(--ev-green); }
.ev-value b em { font-style: normal; font-size: 0.68rem; opacity: 0.6; margin-left: 1px; }
.ev-value i {
  display: block;
  font-style: normal;
  font-size: 0.63rem;
  letter-spacing: 0.1em;
  color: var(--ev-muted);
}
.ev-row.is-value .ev-value i { color: var(--ev-green); }
.ev-value u {
  display: block;
  text-decoration: none;
  font-family: var(--ev-mono);
  font-variant-numeric: tabular-nums;
  font-size: 0.6rem;
  color: var(--ev-muted);
}

/* 期待回収率のバー。中央の縦線が回収率100%（損益分岐）を表す */
.ev-track {
  grid-column: 1 / -1;
  margin-top: 8px;
  height: 4px;
  border-radius: 2px;
  background: var(--ev-track);
  position: relative;
  overflow: hidden;
}
.ev-track > span {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  background: var(--ev-bar-dim);
  border-radius: 2px;
}
.ev-row.is-value .ev-track > span { background: var(--ev-bar); }
.ev-track::after {
  content: "";
  position: absolute;
  left: 50%;
  top: -2px;
  bottom: -2px;
  width: 1px;
  background: #6E7C68;
}

/* ---------- タブ ---------- */
button[data-baseweb="tab"] { padding-left: 0.6rem; padding-right: 0.6rem; }
button[data-baseweb="tab"] p { font-size: 0.85rem !important; }
@media (max-width: 360px) {
  button[data-baseweb="tab"] { padding-left: 0.35rem; padding-right: 0.35rem; }
  button[data-baseweb="tab"] p { font-size: 0.76rem !important; }
  .ev-meta { font-size: 0.62rem; }
}

/* 数値の桁を揃える */
[data-testid="stDataFrame"] { font-variant-numeric: tabular-nums; }
</style>
"""


def inject() -> None:
    """案Aのスタイルをページに読み込む。"""
    st.markdown(_CSS, unsafe_allow_html=True)


def sticky_anchor() -> None:
    """入力バーを固定するための目印を置く。CSSからこの要素を探して使う。"""
    st.markdown('<span class="ev-sticky-anchor"></span>', unsafe_allow_html=True)


def bar_width(payout_rate: float) -> float:
    """期待回収率(%)をバーの長さ(%)に変換する。"""
    return min(100.0, max(0.0, payout_rate / BAR_FULL_SCALE * 100))
