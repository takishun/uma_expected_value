"""馬券の的中確率・期待値を計算するドメインロジック。

このモジュールはUI(Streamlit)に依存せず、標準ライブラリだけで完結する。

確率モデルは「全馬の実力が互角で、着順は完全にランダム」という単純化された
前提に立つ。したがって各式別の1点あたりの的中確率は

    的中確率 = 的中する組み合わせの数 / 全組み合わせの数

で求まる。実際のレースでは人気・馬場・展開によって確率は大きく変わるため、
あくまで「オッズが理論値より割安か割高か」を測るための基準値として使う。
"""

from dataclasses import dataclass
from math import comb, perm

# 表示する馬券の種類(表示順)
BET_TYPES = ('単勝', '複勝', '三連単', '三連複', '馬単', '馬連', 'ワイド', '枠連')

# JRAの枠番は1〜8枠。9頭以上のレースでは1つの枠に複数頭が入る。
FRAME_COUNT = 8

# 式別ごとの発売可能な最小出走頭数。これを下回る頭数では馬券が発売されない
# (または的中確率が100%になり計算する意味がない)。
MIN_HORSES = {
    '単勝': 2,
    '複勝': 5,
    '三連単': 4,
    '三連複': 4,
    '馬単': 3,
    '馬連': 3,
    'ワイド': 4,
    '枠連': 9,
}

# 出馬表として現実的な範囲(JRAの最大出走頭数は18頭)
MIN_FIELD_SIZE = 2
MAX_FIELD_SIZE = 18


def place_slots(horses: int) -> int:
    """複勝の的中となる着順の数を返す。

    JRAでは出走7頭以下のレースは2着まで、8頭以上は3着までが複勝の対象。
    """
    return 2 if horses < 8 else 3


def frame_sizes(horses: int) -> list[int]:
    """各枠に入る頭数を枠番順(1枠→8枠)に返す。

    8頭以下は1枠1頭ずつ。9頭以上は8枠に振り分け、割り切れない端数は
    8枠側から1頭ずつ多く割り当てられる(例: 18頭なら 2,2,2,2,2,2,3,3)。
    """
    if horses <= FRAME_COUNT:
        return [1] * horses
    base, extra = divmod(horses, FRAME_COUNT)
    return [base] * (FRAME_COUNT - extra) + [base + 1] * extra


def frame_quinella_combinations(horses: int) -> int:
    """枠連の買い目の総数を返す。

    異なる枠どうしの組み合わせに加えて、同じ枠の2頭が1着2着を占める
    「ゾロ目」も買い目として成立するため、複数頭が入る枠の数を足す。
    """
    sizes = frame_sizes(horses)
    return comb(len(sizes), 2) + sum(1 for size in sizes if size >= 2)


def is_available(name: str, horses: int) -> bool:
    """その頭数でこの式別の馬券が発売されるかどうか。"""
    if name not in MIN_HORSES:
        raise ValueError(f'未知の馬券種です: {name}')
    return horses >= MIN_HORSES[name]


def hit_probability(name: str, horses: int) -> float | None:
    """馬券1点あたりの的中確率(%)。発売されない頭数の場合はNoneを返す。"""
    if not is_available(name, horses):
        return None

    if name == '単勝':
        # 1着を当てる。n頭のうち1頭。
        return 100 / horses
    if name == '複勝':
        # 選んだ1頭が2着(または3着)以内に入る。
        return 100 * place_slots(horses) / horses
    if name == '三連単':
        # 1〜3着を着順どおりに当てる。
        return 100 / perm(horses, 3)
    if name == '三連複':
        # 1〜3着を着順不問で当てる。
        return 100 / comb(horses, 3)
    if name == '馬単':
        # 1着2着を着順どおりに当てる。
        return 100 / perm(horses, 2)
    if name == '馬連':
        # 1着2着を着順不問で当てる。
        return 100 / comb(horses, 2)
    if name == 'ワイド':
        # 選んだ2頭がともに3着以内。3頭の中から2頭を選ぶ組み合わせ(=3通り)が当たり。
        return 100 * comb(3, 2) / comb(horses, 2)
    if name == '枠連':
        # 1着2着の馬が入る枠の組み合わせを当てる(ゾロ目を含む)。
        return 100 / frame_quinella_combinations(horses)

    raise ValueError(f'未知の馬券種です: {name}')


@dataclass(frozen=True)
class BakenMetrics:
    """1つの式別についての計算結果。"""

    name: str
    probability: float  # 的中確率(%)
    expected_value: float  # 期待値(円)
    fair_odds: float  # 損益分岐(公正)オッズ(倍)
    payout_rate: float  # 期待回収率(%)

    @property
    def is_value(self) -> bool:
        """入力オッズが損益分岐オッズを上回る(=妙味がある)か。

        ちょうど等しい場合は収支トントンなので妙味ありとはしない。
        """
        return self.payout_rate > 100


def calculate(name: str, odds: float, bet: int, horses: int) -> BakenMetrics | None:
    """式別ごとの期待値・損益分岐オッズ・期待回収率をまとめて算出する。

    発売されない頭数の場合はNoneを返す。
    """
    probability = hit_probability(name, horses)
    if probability is None:
        return None
    return BakenMetrics(
        name=name,
        probability=probability,
        # 期待値 = 掛け金 × オッズ × 的中確率
        expected_value=bet * odds * probability / 100,
        # 期待値が掛け金と等しくなるオッズ
        fair_odds=100 / probability,
        # 期待回収率 = 期待値 ÷ 掛け金 × 100
        payout_rate=odds * probability,
    )


def calculate_all(odds: float, bet: int, horses: int) -> list[BakenMetrics]:
    """発売される全式別の計算結果を BET_TYPES の順に返す。"""
    results = (calculate(name, odds, bet, horses) for name in BET_TYPES)
    return [metrics for metrics in results if metrics is not None]


def available_bet_types(horses: int) -> list[str]:
    """その頭数で発売される式別を BET_TYPES の順に返す。"""
    return [name for name in BET_TYPES if is_available(name, horses)]
