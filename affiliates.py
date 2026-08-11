"""アフィリエイト広告の定義と描画。

広告のHTMLは同じ形をした文字列の繰り返しなので、A8.netのバナーは
パラメータだけをデータとして持ち、HTMLは組み立てて生成する。
差し替えるときは BANNERS のリストを編集するだけでよい。
"""

from dataclasses import dataclass

import streamlit as st
import streamlit.components.v1 as stc

# バナー画像の下に置く余白。これがないとiframe内で画像が見切れる。
_IFRAME_PADDING = 10


@dataclass(frozen=True)
class A8Banner:
    """A8.netのバナー広告1つ分のパラメータ。"""

    a8mat: str  # 広告主・広告枠を識別するトラッキングID
    aid: str  # アフィリエイトID
    mid: str  # マーチャントID
    image_host: str  # バナー画像の配信ホスト(wwwXX)
    tracking_host: str  # 成果計測用1x1画像の配信ホスト(wwwXX)
    width: int = 300
    height: int = 250

    @property
    def html(self) -> str:
        return (
            f'<a href="https://px.a8.net/svt/ejp?a8mat={self.a8mat}" rel="nofollow">'
            f'<img border="0" width="{self.width}" height="{self.height}" alt=""'
            f' src="https://{self.image_host}.a8.net/svt/bgt'
            f'?aid={self.aid}&wid=006&eno=01&mid={self.mid}&mc=1"></a>'
            f'<img border="0" width="1" height="1"'
            f' src="https://{self.tracking_host}.a8.net/0.gif?a8mat={self.a8mat}" alt="">'
        )

    def render(self) -> None:
        stc.html(self.html, height=self.height + _IFRAME_PADDING)


# ページ下部に3列で並べるバナー
BANNERS = (
    A8Banner(
        a8mat='4B5YSD+5YC6EY+4JVQ+614CX',
        aid='260618845360',
        mid='s00000021239001013000',
        image_host='www25',
        tracking_host='www18',
    ),
    A8Banner(
        a8mat='45GG1D+2RFINU+4RKY+63H8H',
        aid='251030065167',
        mid='s00000022237001024000',
        image_host='www20',
        tracking_host='www17',
    ),
    A8Banner(
        a8mat='4B5YSD+5XQQT6+2Z0I+IHXRL',
        aid='260618845359',
        mid='s00000013869003107000',
        image_host='www23',
        tracking_host='www17',
    ),
    A8Banner(
        a8mat='3NF11N+2A5Y4A+2PEO+1I4AW1',
        aid='220730891138',
        mid='s00000012624009090000',
        image_host='www24',
        tracking_host='www10',
    ),
    A8Banner(
        a8mat='3TCR4P+3RQYKA+19NM+C03K1',
        aid='230702425228',
        mid='s00000005917002016000',
        image_host='www22',
        tracking_host='www10',
    ),
    A8Banner(
        a8mat='4B5YSD+4W8FP6+3IB8+609HT',
        aid='260618845296',
        mid='s00000016370001009000',
        image_host='www27',
        tracking_host='www12',
        width=250,
    ),
)

# ページ最下部に単独で置くバナー
CLOSING_BANNER = A8Banner(
    a8mat='3TCR4P+7YZ27U+47AY+601S1',
    aid='230702425482',
    mid='s00000019609001008000',
    image_host='www29',
    tracking_host='www19',
)

# 本文中に置くテキストリンク
TEXT_LINKS = (
    ('https://www.jra.go.jp/', 'JRA公式サイト'),
    ('https://amzn.to/4coJX86', 'ウマ娘を見るならAmazonPrimeVideo'),
)


def render_text_links() -> None:
    """本文中のテキストリンクを描画する。"""
    for url, label in TEXT_LINKS:
        st.markdown(
            f'<a target="_blank" rel="noopener" href="{url}">{label}</a>',
            unsafe_allow_html=True,
        )


def render_banners(columns: int = 3) -> None:
    """バナー広告を指定した列数に、左の列から順に詰めて描画する。"""
    per_column = -(-len(BANNERS) // columns)  # 切り上げ除算
    for col, start in zip(st.columns(columns), range(0, len(BANNERS), per_column)):
        with col:
            for banner in BANNERS[start:start + per_column]:
                banner.render()


def render_closing_banner() -> None:
    """ページ最下部のバナーを描画する。"""
    CLOSING_BANNER.render()
