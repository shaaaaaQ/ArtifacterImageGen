import unittest
from types import SimpleNamespace

from PIL import Image

from artifacter_image_gen.generator import (
    Generator,
    _format_stat_value,
    _normalize_character_art,
)


def typed_stat(name, value):
    return SimpleNamespace(type=SimpleNamespace(name=name, value=name), value=value)


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        stat_values = {
            "FIGHT_PROP_MAX_HP": 15000.4,
            "FIGHT_PROP_CUR_ATTACK": 2000.1,
            "FIGHT_PROP_CUR_DEFENSE": 800.2,
            "FIGHT_PROP_ELEMENT_MASTERY": 100.0,
            "FIGHT_PROP_CRITICAL": 0.701,
            "FIGHT_PROP_CRITICAL_HURT": 1.402,
            "FIGHT_PROP_CHARGE_EFFICIENCY": 1.25,
            "FIGHT_PROP_BASE_HP": 10000.0,
            "FIGHT_PROP_BASE_ATTACK": 800.0,
            "FIGHT_PROP_BASE_DEFENSE": 500.0,
            "FIGHT_PROP_HEAL_ADD": 0.0,
            "FIGHT_PROP_PHYSICAL_ADD_HURT": 0.0,
            "FIGHT_PROP_FIRE_ADD_HURT": 0.466,
            "FIGHT_PROP_ELEC_ADD_HURT": 0.0,
            "FIGHT_PROP_WATER_ADD_HURT": 0.0,
            "FIGHT_PROP_WIND_ADD_HURT": 0.0,
            "FIGHT_PROP_ICE_ADD_HURT": 0.0,
            "FIGHT_PROP_ROCK_ADD_HURT": 0.0,
            "FIGHT_PROP_GRASS_ADD_HURT": 0.0,
        }
        stats = {
            index: typed_stat(name, value)
            for index, (name, value) in enumerate(stat_values.items())
        }
        artifact = SimpleNamespace(
            equip_type=SimpleNamespace(value="EQUIP_BRACER"),
            sub_stats=[
                typed_stat("FIGHT_PROP_CRITICAL", 3.9),
                typed_stat("FIGHT_PROP_CRITICAL_HURT", 7.8),
            ],
            sub_stat_ids=[501204, 501221],
        )
        character = SimpleNamespace(
            element=SimpleNamespace(name="PYRO"),
            stats=stats,
            artifacts=[artifact],
            weapon=SimpleNamespace(),
        )
        self.artifact = artifact
        self.generator = Generator(
            character,
            affixes={
                "501204": {"PropType": 20, "Value": 0.0389},
                "501221": {"PropType": 22, "Value": 0.0544},
            },
        )

    def test_reads_enka_py_character_stats(self):
        stats = self.generator.get_character_stats()
        self.assertEqual(stats["HP"], 15000)
        self.assertEqual(stats["会心率"], 70.1)
        self.assertEqual(stats["炎元素ダメージ"], 46.6)

    def test_scores_enka_py_artifacts(self):
        score = self.generator.calc_score(
            {"FIGHT_PROP_CRITICAL": 2, "FIGHT_PROP_CRITICAL_HURT": 1}
        )
        self.assertAlmostEqual(score["EQUIP_BRACER"], 15.6)
        self.assertAlmostEqual(score["Total"], 15.6)

    def test_resolves_roll_values_from_official_affix_data(self):
        rolls = self.generator._artifact_rolls(self.artifact)
        self.assertEqual(rolls["会心率"], [3.9])
        self.assertEqual(rolls["会心ダメージ"], [5.4])

    def test_centers_non_standard_character_art(self):
        image = Image.new("RGBA", (1125, 900), "white")

        normalized = _normalize_character_art(image)

        self.assertEqual(normalized.size, (2048, 1024))
        self.assertEqual(normalized.getbbox(), (384, 0, 1664, 1024))

    def test_omits_zero_decimal_from_percentage(self):
        self.assertEqual(_format_stat_value("会心率", 70.0), "70%")
        self.assertEqual(_format_stat_value("会心率", 70.1), "70.1%")

    def test_omits_zero_decimal_from_flat_stat(self):
        self.assertEqual(_format_stat_value("HP", 4780.0), "4,780")
        self.assertEqual(_format_stat_value("HP", 4780.5), "4,780.5")


if __name__ == "__main__":
    unittest.main()
