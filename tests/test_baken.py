"""baken.py の確率・期待値ロジックのテスト。"""

from math import comb, isclose

import pytest

import baken


class TestFrameSizes:
    def test_8頭以下は1枠1頭(self):
        assert baken.frame_sizes(8) == [1] * 8
        assert baken.frame_sizes(5) == [1] * 5

    def test_18頭は6枠が2頭_7枠と8枠が3頭(self):
        assert baken.frame_sizes(18) == [2, 2, 2, 2, 2, 2, 3, 3]

    def test_16頭は全枠2頭(self):
        assert baken.frame_sizes(16) == [2] * 8

    def test_端数は8枠側から割り当てられる(self):
        assert baken.frame_sizes(9) == [1, 1, 1, 1, 1, 1, 1, 2]
        assert baken.frame_sizes(10) == [1, 1, 1, 1, 1, 1, 2, 2]

    @pytest.mark.parametrize('horses', range(baken.MIN_FIELD_SIZE, baken.MAX_FIELD_SIZE + 1))
    def test_枠の合計は常に出走頭数と一致する(self, horses):
        assert sum(baken.frame_sizes(horses)) == horses

    @pytest.mark.parametrize('horses', range(9, baken.MAX_FIELD_SIZE + 1))
    def test_9頭以上は必ず8枠(self, horses):
        assert len(baken.frame_sizes(horses)) == baken.FRAME_COUNT


class TestFrameQuinellaCombinations:
    def test_18頭の枠連は36通り(self):
        # 異なる枠どうし C(8,2)=28 通り + 全8枠がゾロ目可能 = 36 通り
        assert baken.frame_quinella_combinations(18) == 36

    def test_9頭の枠連は29通り(self):
        # C(8,2)=28 通り + 2頭入る8枠のゾロ目1通り
        assert baken.frame_quinella_combinations(9) == 29

    def test_枠連は8枠を前提とする(self):
        # 旧実装は9枠(comb(9,2)=36)を前提にしていたため、頭数によらず一定だった
        assert baken.frame_quinella_combinations(10) == 30
        assert baken.frame_quinella_combinations(16) == 36


class TestHitProbability:
    def test_単勝は頭数の逆数(self):
        assert isclose(baken.hit_probability('単勝', 18), 100 / 18)

    def test_複勝は8頭以上なら3着まで(self):
        assert isclose(baken.hit_probability('複勝', 18), 100 * 3 / 18)

    def test_複勝は7頭以下なら2着まで(self):
        # 5〜7頭立ては2着までが的中。3着まで数えると確率を過大評価してしまう。
        assert isclose(baken.hit_probability('複勝', 7), 100 * 2 / 7)
        assert isclose(baken.hit_probability('複勝', 5), 100 * 2 / 5)

    def test_ワイドは2頭がともに3着以内に入る確率(self):
        # 超幾何分布による検算: 18頭から3頭が3着以内に入るとき、
        # 指定した2頭がともに含まれる確率 = C(16,1) / C(18,3)
        expected = 100 * comb(16, 1) / comb(18, 3)
        assert isclose(baken.hit_probability('ワイド', 18), expected)
        assert isclose(baken.hit_probability('ワイド', 18), 100 * 3 / comb(18, 2))

    def test_ワイドは馬連のちょうど3倍(self):
        # 当たりの組み合わせが3通りあるだけで、母数は馬連と同じ。
        assert isclose(
            baken.hit_probability('ワイド', 18),
            3 * baken.hit_probability('馬連', 18),
        )

    def test_三連単は三連複の6分の1(self):
        assert isclose(
            baken.hit_probability('三連単', 18),
            baken.hit_probability('三連複', 18) / 6,
        )

    def test_馬単は馬連の2分の1(self):
        assert isclose(
            baken.hit_probability('馬単', 18),
            baken.hit_probability('馬連', 18) / 2,
        )

    def test_枠連は頭数によって変わる(self):
        assert baken.hit_probability('枠連', 10) != baken.hit_probability('枠連', 18)

    @pytest.mark.parametrize('name', baken.BET_TYPES)
    @pytest.mark.parametrize('horses', range(baken.MIN_FIELD_SIZE, baken.MAX_FIELD_SIZE + 1))
    def test_確率は0より大きく100以下に収まる(self, name, horses):
        probability = baken.hit_probability(name, horses)
        if probability is None:
            return
        assert 0 < probability <= 100

    @pytest.mark.parametrize('name', baken.BET_TYPES)
    def test_発売されない頭数ではNoneを返す(self, name):
        assert baken.hit_probability(name, baken.MIN_HORSES[name] - 1) is None

    def test_未知の式別はエラー(self):
        with pytest.raises(ValueError):
            baken.hit_probability('三連単ボックス', 18)


class TestCalculate:
    def test_期待値は掛け金かけるオッズかける確率(self):
        metrics = baken.calculate('単勝', odds=10.0, bet=100, horses=18)
        assert isclose(metrics.expected_value, 100 * 10.0 * (100 / 18) / 100)

    def test_損益分岐オッズで期待値は掛け金と等しくなる(self):
        fair = baken.calculate('三連複', odds=1.0, bet=100, horses=18).fair_odds
        metrics = baken.calculate('三連複', odds=fair, bet=100, horses=18)
        assert isclose(metrics.expected_value, 100)
        assert isclose(metrics.payout_rate, 100)

    def test_損益分岐オッズちょうどは妙味なし(self):
        fair = baken.calculate('馬連', odds=1.0, bet=100, horses=18).fair_odds
        assert not baken.calculate('馬連', odds=fair, bet=100, horses=18).is_value
        assert baken.calculate('馬連', odds=fair * 1.01, bet=100, horses=18).is_value

    def test_期待回収率は掛け金に依存しない(self):
        small = baken.calculate('馬単', odds=50.0, bet=100, horses=18)
        large = baken.calculate('馬単', odds=50.0, bet=10_000, horses=18)
        assert isclose(small.payout_rate, large.payout_rate)

    def test_発売されない式別はNone(self):
        assert baken.calculate('枠連', odds=10.0, bet=100, horses=8) is None


class TestAvailability:
    def test_8頭立てでは枠連が発売されない(self):
        available = baken.available_bet_types(8)
        assert '枠連' not in available
        assert '複勝' in available

    def test_4頭立てでは複勝も枠連も発売されない(self):
        available = baken.available_bet_types(4)
        assert '複勝' not in available
        assert '枠連' not in available
        assert '単勝' in available

    def test_18頭立ては全式別が発売される(self):
        assert baken.available_bet_types(18) == list(baken.BET_TYPES)

    def test_calculate_allは発売される式別だけを返す(self):
        results = baken.calculate_all(odds=10.0, bet=100, horses=8)
        assert [m.name for m in results] == baken.available_bet_types(8)

    def test_最小頭数では単勝のみ(self):
        assert baken.available_bet_types(baken.MIN_FIELD_SIZE) == ['単勝']
