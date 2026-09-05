import unittest

from enka.gi import (
    Artifact,
    Character,
    Constellation,
    Element,
    EquipmentType,
    FightProp,
    FightPropType,
    Icon,
    Stat,
    StatType,
    Talent,
    Weapon,
)
from PIL import Image

from artifacter_image_gen import Generator


class FakeCache:
    def image(self, _url):
        return Image.new("RGBA", (2048, 1024), "white")


class EnkaModelIntegrationTests(unittest.TestCase):
    def test_generator_accepts_enka_v2_models(self):
        artifact = Artifact.model_construct(
            id=15001,
            equip_type=EquipmentType.FLOWER,
            icon="https://enka.network/ui/artifact.png",
            level=20,
            main_stat=Stat(type=StatType.FIGHT_PROP_HP, value=4780),
            set_name="Test Set",
            sub_stats=[
                Stat(type=StatType.FIGHT_PROP_CRITICAL, value=3.9),
                Stat(type=StatType.FIGHT_PROP_CRITICAL_HURT, value=7.8),
            ],
            sub_stat_ids=[],
        )
        stats = {
            stat_type: FightProp(type=stat_type, value=value)
            for stat_type, value in {
                FightPropType.FIGHT_PROP_MAX_HP: 15000,
                FightPropType.FIGHT_PROP_CUR_ATTACK: 2000,
                FightPropType.FIGHT_PROP_CUR_DEFENSE: 800,
                FightPropType.FIGHT_PROP_ELEMENT_MASTERY: 100,
                FightPropType.FIGHT_PROP_CRITICAL: 0.7,
                FightPropType.FIGHT_PROP_CRITICAL_HURT: 1.4,
                FightPropType.FIGHT_PROP_CHARGE_EFFICIENCY: 1.25,
                FightPropType.FIGHT_PROP_BASE_HP: 10000,
                FightPropType.FIGHT_PROP_BASE_ATTACK: 800,
                FightPropType.FIGHT_PROP_BASE_DEFENSE: 500,
                FightPropType.FIGHT_PROP_HEAL_ADD: 0,
                FightPropType.FIGHT_PROP_PHYSICAL_ADD_HURT: 0,
                FightPropType.FIGHT_PROP_FIRE_ADD_HURT: 0.466,
                FightPropType.FIGHT_PROP_ELEC_ADD_HURT: 0,
                FightPropType.FIGHT_PROP_WATER_ADD_HURT: 0,
                FightPropType.FIGHT_PROP_WIND_ADD_HURT: 0,
                FightPropType.FIGHT_PROP_ICE_ADD_HURT: 0,
                FightPropType.FIGHT_PROP_ROCK_ADD_HURT: 0,
                FightPropType.FIGHT_PROP_GRASS_ADD_HURT: 0,
            }.items()
        }
        character = Character.model_construct(
            id=10000001,
            name="Test Character",
            level=90,
            element=Element.PYRO,
            stats=stats,
            artifacts=[artifact],
            weapon=Weapon.model_construct(
                name="Test Weapon",
                level=90,
                refinement=1,
                rarity=5,
                icon="https://enka.network/ui/weapon.png",
                stats=[
                    Stat(type=StatType.FIGHT_PROP_BASE_ATTACK, value=608),
                    Stat(type=StatType.FIGHT_PROP_ATTACK_PERCENT, value=49.6),
                ],
            ),
            icon=Icon(side_icon_ui_path="UI_AvatarIcon_Side_Test"),
            friendship_level=10,
            talents=[
                Talent(id=index, level=10, icon=f"https://enka.network/ui/talent{index}.png")
                for index in range(3)
            ],
            constellations=[
                Constellation(
                    id=index,
                    unlocked=index < 2,
                    icon=f"https://enka.network/ui/constellation{index}.png",
                )
                for index in range(6)
            ],
        )

        generator = Generator(character, cache=FakeCache(), affixes={})
        score = generator.calc_score(
            {"FIGHT_PROP_CRITICAL": 2, "FIGHT_PROP_CRITICAL_HURT": 1}
        )

        self.assertEqual(generator.element, "Pyro")
        self.assertAlmostEqual(score["Total"], 15.6)
        self.assertEqual(generator.get_character_stats()["炎元素ダメージ"], 46.6)

        image = generator.generate(
            {"FIGHT_PROP_CRITICAL": 2, "FIGHT_PROP_CRITICAL_HURT": 1}
        )
        self.assertEqual(image.size, (1920, 1080))


if __name__ == "__main__":
    unittest.main()
