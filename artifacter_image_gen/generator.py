import logging
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from .cache import AssetCache
from .constants import (
    ARTIFACT_SLOTS,
    DEFAULT_GRADE_THRESHOLDS,
    ELEMENT_NAMES,
    FIGHT_PROP_NAMES_BY_ID,
    PERCENTAGE_NAMES,
    PROP_NAMES,
    SHORT_NAMES,
    STAT_ORDER,
)

if TYPE_CHECKING:
    from enka.gi import Character

logger = logging.getLogger(__name__)

ASSET_DIR = Path(__file__).parent / "assets"


def font(size):
    return ImageFont.truetype(ASSET_DIR / "font.ttf", size)


def _enum_name(value) -> str:
    """Return the stable name/value exposed by enka.py enums."""
    return getattr(value, "name", None) or getattr(value, "value", value)


def _stat_type(stat) -> str:
    value = getattr(stat.type, "value", stat.type)
    return value if isinstance(value, str) else getattr(stat.type, "name", str(value))


def _grade(score: float, thresholds: Mapping[str, float]) -> str:
    for grade in ("SS", "S", "A"):
        if score >= thresholds[grade]:
            return grade
    return "B"


class Generator:
    def __init__(
        self,
        character: "Character",
        *,
        cache: AssetCache | None = None,
        affixes: Mapping[str, Mapping[str, float | int]] | None = None,
    ) -> None:
        self.character = character
        self.cache = cache or AssetCache()
        self._affixes = affixes
        self.element = _enum_name(character.element).title()
        self.artifacts = self.get_artifacts()
        self.weapon = character.weapon

    def _character_stat(self, prop_name: str):
        for stat in self.character.stats.values():
            if _stat_type(stat) == prop_name:
                return stat
        raise KeyError(f"Character stat is missing: {prop_name}")

    def _image(self, url: str) -> Image.Image:
        logger.debug("fetch image: %s", url)
        return self.cache.image(url)

    def _artifact_rolls(self, artifact) -> dict[str, list[float | int]]:
        if self._affixes is None:
            try:
                self._affixes = self.cache.affixes()
            except (OSError, ValueError) as error:
                logger.warning("could not load artifact affixes: %s", error)
                self._affixes = {}

        rolls: dict[str, list[float | int]] = {}
        for affix_id in artifact.sub_stat_ids:
            data = self._affixes.get(str(affix_id))
            if not data:
                continue
            prop_name = FIGHT_PROP_NAMES_BY_ID.get(int(data["PropType"]))
            if prop_name is None:
                continue
            display_name = PROP_NAMES[prop_name]
            value = float(data["Value"])
            if display_name in PERCENTAGE_NAMES:
                value = round(value * 100, 1)
            else:
                value = round(value)
            rolls.setdefault(display_name, []).append(value)
        return rolls

    def get_character_stats(self):
        result = {
            "HP": round(self._character_stat("FIGHT_PROP_MAX_HP").value),
            "攻撃力": round(self._character_stat("FIGHT_PROP_CUR_ATTACK").value),
            "防御力": round(self._character_stat("FIGHT_PROP_CUR_DEFENSE").value),
            "元素熟知": round(self._character_stat("FIGHT_PROP_ELEMENT_MASTERY").value),
            "会心率": round(self._character_stat("FIGHT_PROP_CRITICAL").value * 100, 1),
            "会心ダメージ": round(
                self._character_stat("FIGHT_PROP_CRITICAL_HURT").value * 100, 1
            ),
            "元素チャージ効率": round(
                self._character_stat("FIGHT_PROP_CHARGE_EFFICIENCY").value * 100, 1
            ),
        }
        bonus_props = (
            "FIGHT_PROP_HEAL_ADD",
            "FIGHT_PROP_PHYSICAL_ADD_HURT",
            "FIGHT_PROP_FIRE_ADD_HURT",
            "FIGHT_PROP_ELEC_ADD_HURT",
            "FIGHT_PROP_WATER_ADD_HURT",
            "FIGHT_PROP_WIND_ADD_HURT",
            "FIGHT_PROP_ICE_ADD_HURT",
            "FIGHT_PROP_ROCK_ADD_HURT",
            "FIGHT_PROP_GRASS_ADD_HURT",
        )
        bonuses = {
            PROP_NAMES[prop]: round(self._character_stat(prop).value * 100, 1)
            for prop in bonus_props
        }
        bonus = max(bonuses, key=bonuses.get)
        if bonuses[bonus] == 0:
            bonus = f"{ELEMENT_NAMES[self.element]}元素ダメージ"
        result[bonus] = bonuses[bonus]

        return result

    def get_character_base_stats(self):
        return {
            "HP": round(self._character_stat("FIGHT_PROP_BASE_HP").value),
            "攻撃力": round(self._character_stat("FIGHT_PROP_BASE_ATTACK").value),
            "防御力": round(self._character_stat("FIGHT_PROP_BASE_DEFENSE").value),
        }

    def get_artifacts(self):
        artifacts = dict.fromkeys(ARTIFACT_SLOTS)
        for artifact in self.character.artifacts:
            artifacts[artifact.equip_type.value] = artifact
        return artifacts

    def calc_score(self, rates):
        result = {
            "Total": 0,
            "EQUIP_BRACER": 0,
            "EQUIP_NECKLACE": 0,
            "EQUIP_SHOES": 0,
            "EQUIP_RING": 0,
            "EQUIP_DRESS": 0,
        }
        for artifact_type, artifact in self.artifacts.items():
            if not artifact:
                continue
            values = {_stat_type(stat): stat.value for stat in artifact.sub_stats}
            score = sum(values.get(prop_id, 0) * rate for prop_id, rate in rates.items())
            result[artifact_type] = score
            result["Total"] += score
        return result

    def generate(self, rates, point_refer=DEFAULT_GRADE_THRESHOLDS, label=""):
        score = self.calc_score(rates)
        base = Image.open(ASSET_DIR / "base" / f"{self.element}.png")
        base = self._draw_character(base)
        base = self._draw_weapon(base)
        base = self._draw_weapon_rarity(base)
        base = self._draw_skills(base)
        base = self._draw_constellation(base)
        base = self._draw_level(base)  # level, friendship_level
        base = self._draw_skill_level(base)
        base = self._draw_character_stats(base)
        base = self._draw_weapon_stats(base)
        base = self._draw_total_score(base, score, label, point_refer["Total"])
        base = self._draw_artifacts(base, score, point_refer)

        return base

    def _draw_character(self, base):
        character = self.character
        character_icon = character.costume.icon if character.costume else character.icon
        image = self._image(character_icon.gacha)
        image = image.convert("RGBA")
        if character.id == 10000005:
            # 空
            tmp = Image.new("RGBA", (2048, 1024), (255, 255, 255, 0))
            image = image.resize((909, 1024))
            tmp.paste(image, (570, 0))
            image = tmp
        elif character.id == 10000007:
            # 蛍
            tmp = Image.new("RGBA", (2048, 1024), (255, 255, 255, 0))
            image = image.resize((880, 1024))
            tmp.paste(image, (584, 0))
            image = tmp
        image = image.crop((289, 0, 1728, 1024))
        image = image.resize((int(image.width * 0.75), int(image.height * 0.75)))
        mask1 = image.copy()
        if character.id == 10000078:
            # アルハイゼン
            mask2 = Image.open(ASSET_DIR / "alhaitham_mask.png")
        else:
            mask2 = Image.open(ASSET_DIR / "character_mask.png")
        mask2 = mask2.convert("L")
        mask2 = mask2.resize(image.size)
        shadow = Image.open(ASSET_DIR / "shadow.png")
        shadow = shadow.resize(base.size)
        image.putalpha(mask2)
        paste = Image.new("RGBA", base.size, (255, 255, 255, 0))
        paste.paste(image, (-160, -45), mask=mask1)
        base = Image.alpha_composite(base, paste)
        base = Image.alpha_composite(base, shadow)
        return base

    def _draw_weapon(self, base):
        weapon = self.weapon
        image = self._image(weapon.icon)
        image = image.convert("RGBA")
        image = image.resize((128, 128))
        mask = image.copy()
        paste = Image.new("RGBA", base.size, (255, 255, 255, 0))
        paste.paste(image, (1430, 50), mask=mask)
        base = Image.alpha_composite(base, paste)
        return base

    def _draw_weapon_rarity(self, base):
        rarity = self.weapon.rarity
        image = Image.open(ASSET_DIR / "rarity" / f"{rarity}.png")
        image = image.convert("RGBA")
        image = image.resize((int(image.width * 0.97), int(image.height * 0.97)))
        paste = Image.new("RGBA", base.size, (255, 255, 255, 0))
        mask = image.copy()
        paste.paste(image, (1422, 173), mask=mask)
        base = Image.alpha_composite(base, paste)
        return base

    def _draw_skills(self, base):
        skills = self.character.talents
        bg = Image.open(ASSET_DIR / "skill_back.png")
        bg = bg.resize((int(bg.width / 1.5), int(bg.height / 1.5)))
        bg_paste = Image.new("RGBA", base.size, (255, 255, 255, 0))
        for i in range(3):
            skill = skills[i]
            image = self._image(skill.icon)
            image = image.resize((50, 50))
            image = image.convert("RGBA")
            mask = image.copy()
            paste = Image.new("RGBA", bg.size, (255, 255, 255, 0))
            paste.paste(image, (paste.width // 2 - 25, paste.height // 2 - 25), mask)
            bg_paste.paste(Image.alpha_composite(bg, paste), (15, 330 + i * 105))
        base = Image.alpha_composite(base, bg_paste)
        return base

    def _draw_constellation(self, base):
        bg = Image.open(ASSET_DIR / "constellation" / f"{self.element}.png")
        bg = bg.resize((90, 90))
        bg = bg.convert("RGBA")
        lock = Image.open(
            ASSET_DIR / "constellation" / f"{self.element}_lock.png"
        )
        lock = lock.resize((90, 90))
        lock = lock.convert("RGBA")
        lock_mask = lock.copy()
        bg_paste = Image.new("RGBA", base.size, (255, 255, 255, 0))
        for i, c in enumerate(self.character.constellations, 1):
            if not c.unlocked:
                bg_paste.paste(lock, (666, -10 + i * 93), mask=lock_mask)
            else:
                image = self._image(c.icon)
                image = image.convert("RGBA")
                image = image.resize((45, 45))
                paste = Image.new("RGBA", bg.size, (255, 255, 255, 0))
                mask = image.copy()
                paste.paste(
                    image,
                    (int(paste.width / 2) - 25, int(paste.height / 2) - 23),
                    mask=mask,
                )
                bg_paste.paste(Image.alpha_composite(bg, paste), (666, -10 + i * 93))
        base = Image.alpha_composite(base, bg_paste)
        return base

    def _draw_level(self, base):
        draw = ImageDraw.Draw(base)
        character = self.character

        draw.text((30, 20), character.name, font=font(48))
        level_length = draw.textlength("Lv." + str(character.level), font=font(25))
        friendship_length = draw.textlength(
            str(character.friendship_level), font=font(25)
        )
        draw.text((35, 75), "Lv." + str(character.level), font=font(25))
        draw.rounded_rectangle(
            (35 + level_length + 5, 74, 77 + level_length + friendship_length, 102),
            radius=2,
            fill="black",
        )
        friendship_icon = Image.open(ASSET_DIR / "friendship.png").convert("RGBA")
        friendship_icon = friendship_icon.resize(
            (int(friendship_icon.width * (24 / friendship_icon.height)), 24)
        )
        friendship_icon_mask = friendship_icon.copy()
        base.paste(friendship_icon, (42 + int(level_length), 76), friendship_icon_mask)
        draw.text(
            (73 + level_length, 74), str(character.friendship_level), font=font(25)
        )
        return base

    def _draw_skill_level(self, base):
        draw = ImageDraw.Draw(base)
        skills = self.character.talents

        for i in range(3):
            draw.text(
                (42, 397 + i * 105),
                f"Lv.{skills[i].level}",
                font=font(17),
                fill="aqua" if skills[i].level >= 10 else None,
            )
        return base

    def _draw_character_stats(self, base):
        draw = ImageDraw.Draw(base)
        stats = self.get_character_stats()
        base_stats = self.get_character_base_stats()
        for name, value in stats.items():
            try:
                i = STAT_ORDER.index(name)
            except ValueError:
                i = 7
                draw.text((844, 67 + i * 70), name, font=font(26))
                icon = Image.open(ASSET_DIR / "emotes" / f"{name}.png")
                icon = icon.resize((40, 40))
                icon_paste = Image.new("RGBA", base.size, (255, 255, 255, 0))
                icon_paste.paste(icon, (789, 65 + i * 70))
                base = Image.alpha_composite(base, icon_paste)
                draw = ImageDraw.Draw(base)

            if name not in PERCENTAGE_NAMES:
                state_len = draw.textlength(format(value, ","), font=font(26))
                draw.text(
                    (1360 - state_len, 67 + i * 70), format(value, ","), font=font(26)
                )
            else:
                state_len = draw.textlength(f"{float(value)}%", font=font(26))
                draw.text(
                    (1360 - state_len, 67 + i * 70), f"{float(value)}%", font=font(26)
                )

            if name in ["HP", "防御力", "攻撃力"]:
                base_value = base_stats[name]
                diff = value - base_value
                diff_len = draw.textlength(f'+{format(diff,",")}', font=font(12))
                base_value_len = draw.textlength(
                    f'{format(base_value,",")}', font=font(12)
                )
                draw.text(
                    (1360 - diff_len, 97 + i * 70),
                    f'+{format(diff,",")}',
                    fill=(0, 255, 0, 180),
                    font=font(12),
                )
                draw.text(
                    (1360 - diff_len - base_value_len - 1, 97 + i * 70),
                    f'{format(base_value,",")}',
                    font=font(12),
                    fill=(255, 255, 255, 180),
                )
        return base

    def _draw_weapon_stats(self, base):
        draw = ImageDraw.Draw(base)
        weapon = self.weapon
        level = weapon.level
        draw.text((1582, 47), weapon.name, font=font(26))
        level_len = draw.textlength(f"Lv.{level}", font=font(24))
        draw.rounded_rectangle(
            (1582, 80, 1582 + level_len + 4, 108), radius=1, fill="black"
        )
        draw.text((1584, 82), f"Lv.{level}", font=font(24))

        base_atk_image = Image.open(ASSET_DIR / "emotes" / "基礎攻撃力.png")
        base_atk_image = base_atk_image.resize((23, 23))
        base_atk_mask = base_atk_image.copy()
        base.paste(base_atk_image, (1600, 120), mask=base_atk_mask)
        draw.text(
            (1623, 120), f"基礎攻撃力  {round(weapon.stats[0].value)}", font=font(23)
        )

        if len(weapon.stats) > 1:
            substat = weapon.stats[1]
            substat_name = PROP_NAMES[_stat_type(substat)]
            substat_image = Image.open(
                ASSET_DIR / "emotes" / f"{substat_name}.png"
            ).resize((23, 23))
            weapon_substat_mask = substat_image.copy()
            base.paste(substat_image, (1600, 155), mask=weapon_substat_mask)

            draw.text(
                (1623, 155),
                f"""{
                    SHORT_NAMES.get(substat_name) or substat_name
                }  {
                    str(substat.value)+'%'
                    if substat_name in PERCENTAGE_NAMES
                    else format(substat.value,',')
                }""",
                font=font(23),
            )

        draw.rounded_rectangle((1430, 45, 1470, 70), radius=1, fill="black")
        draw.text((1433, 46), f"R{weapon.refinement}", font=font(24))
        return base

    def _draw_total_score(self, base, score, label, thresholds):
        draw = ImageDraw.Draw(base)
        total_score = float(format(score["Total"], ".1f"))
        score_len = draw.textlength(str(total_score), font(75))
        draw.text((1652 - score_len // 2, 420), str(total_score), font=font(75))
        text_len = draw.textlength(label, font=font(24))
        draw.text((1867 - text_len, 585), label, font=font(24))

        grade = Image.open(ASSET_DIR / "grade" / f"{_grade(total_score, thresholds)}.png")

        grade = grade.resize((grade.width // 8, grade.height // 8))
        grade_mask = grade.copy()

        base.paste(grade, (1806, 345), mask=grade_mask)
        return base

    def _draw_artifacts(self, base, score, point_refer):
        draw = ImageDraw.Draw(base)
        artifacts = self.artifacts
        artifact_type = []
        for i, parts in enumerate(artifacts.keys()):
            artifact = artifacts.get(parts)
            if not artifact:
                continue
            artifact_type.append(artifact.set_name)
            paste = Image.new("RGBA", base.size, (255, 255, 255, 0))
            image = self._image(artifact.icon)
            image = image.resize((256, 256))
            image = ImageEnhance.Brightness(image).enhance(0.6)
            image = image.resize((int(image.width * 1.3), int(image.height * 1.3)))
            mask1 = Image.open(ASSET_DIR / "artifact_mask.png")
            mask1 = mask1.convert("L")
            mask1 = mask1.resize(image.size)
            mask2 = image.copy()
            image.putalpha(mask1)
            if parts in ["EQUIP_BRACER", "EQUIP_DRESS"]:
                paste.paste(image, (-37 + 373 * i, 570), mask=mask2)
            elif parts in ["EQUIP_NECKLACE", "EQUIP_RING"]:
                paste.paste(image, (-36 + 373 * i, 570), mask=mask2)
            else:
                paste.paste(image, (-35 + 373 * i, 570), mask=mask2)
            base = Image.alpha_composite(base, paste)
            draw = ImageDraw.Draw(base)

            mainstat = artifact.main_stat
            mainstat_name = PROP_NAMES[_stat_type(mainstat)]

            mainstat_len = draw.textlength(
                SHORT_NAMES.get(mainstat_name) or mainstat_name,
                font=font(29),
            )
            draw.text(
                (375 + i * 373 - int(mainstat_len), 655),
                SHORT_NAMES.get(mainstat_name) or mainstat_name,
                font=font(29),
            )
            mainstat_icon = (
                Image.open(ASSET_DIR / "emotes" / f"{mainstat_name}.png")
                .convert("RGBA")
                .resize((35, 35))
            )
            mainstat_mask = mainstat_icon.copy()
            base.paste(
                mainstat_icon,
                (340 + i * 373 - int(mainstat_len), 655),
                mask=mainstat_mask,
            )

            if mainstat_name in PERCENTAGE_NAMES:
                mainstat_value_size = draw.textlength(
                    f"{float(mainstat.value)}%", font(49)
                )
                draw.text(
                    (375 + i * 373 - mainstat_value_size, 690),
                    f"{float(mainstat.value)}%",
                    font=font(49),
                )
            else:
                mainstat_value_size = draw.textlength(
                    format(mainstat.value, ","), font(49)
                )
                draw.text(
                    (375 + i * 373 - mainstat_value_size, 690),
                    format(mainstat.value, ","),
                    font=font(49),
                )

            level_len = draw.textlength(f"+{artifact.level}", font(21))
            draw.rounded_rectangle(
                (373 + i * 373 - int(level_len), 748, 375 + i * 373, 771),
                fill="black",
                radius=2,
            )
            draw.text(
                (374 + i * 373 - level_len, 749), f"+{artifact.level}", font=font(21)
            )

            affix = self._artifact_rolls(artifact)
            substats = artifact.sub_stats

            for a, stat in enumerate(substats):
                stat_name = PROP_NAMES[_stat_type(stat)]
                if stat_name in ["HP", "攻撃力", "防御力"]:
                    draw.text(
                        (79 + 373 * i, 811 + 50 * a),
                        SHORT_NAMES.get(stat_name) or stat_name,
                        font=font(25),
                        fill=(255, 255, 255, 190),
                    )
                else:
                    draw.text(
                        (79 + 373 * i, 811 + 50 * a),
                        SHORT_NAMES.get(stat_name) or stat_name,
                        font=font(25),
                    )
                substat_icon = Image.open(ASSET_DIR / "emotes" / f"{stat_name}.png")
                substat_icon = substat_icon.resize((30, 30))
                substat_mask = substat_icon.copy()
                base.paste(
                    substat_icon, (44 + 373 * i, 811 + 50 * a), mask=substat_mask
                )
                if stat_name in PERCENTAGE_NAMES:
                    substat_size = draw.textlength(f"{float(stat.value)}%", font(25))
                    draw.text(
                        (375 + i * 373 - substat_size, 811 + 50 * a),
                        f"{float(stat.value)}%",
                        font=font(25),
                    )
                else:
                    substat_size = draw.textlength(format(stat.value, ","), font(25))
                    if stat_name in ["防御力", "攻撃力", "HP"]:
                        draw.text(
                            (375 + i * 373 - substat_size, 811 + 50 * a),
                            format(stat.value, ","),
                            font=font(25),
                            fill=(255, 255, 255, 190),
                        )
                    else:
                        draw.text(
                            (375 + i * 373 - substat_size, 811 + 50 * a),
                            format(stat.value, ","),
                            font=font(25),
                            fill=(255, 255, 255),
                        )

                affix_len = draw.textlength(
                    "+".join(map(str, affix.get(stat_name, ()))), font=font(11)
                )
                draw.text(
                    (375 + i * 373 - affix_len, 840 + 50 * a),
                    "+".join(map(str, affix.get(stat_name, ()))),
                    fill=(255, 255, 255, 160),
                    font=font(11),
                )

            artifact_score = float(format(score[parts], ".1f"))
            score_len = draw.textlength(str(artifact_score), font(36))
            draw.text(
                (380 + i * 373 - score_len, 1016), str(artifact_score), font=font(36)
            )
            draw.text(
                (295 + i * 373 - score_len, 1025),
                "Score",
                font=font(27),
                fill=(160, 160, 160),
            )

            grade_name = _grade(artifact_score, point_refer[parts])
            grade_image = Image.open(ASSET_DIR / "grade" / f"{grade_name}.png")

            grade_image = grade_image.resize(
                (grade_image.width // 11, grade_image.height // 11)
            )
            grade_mask = grade_image.copy()

            base.paste(grade_image, (85 + 373 * i, 1013), mask=grade_mask)

        set_bonus = {
            name: count for name, count in Counter(artifact_type).items() if count >= 2
        }
        for i, (n, q) in enumerate(set_bonus.items()):
            if len(set_bonus) == 2:
                draw.text((1536, 243 + i * 35), n, fill=(0, 255, 0), font=font(23))
                draw.rounded_rectangle(
                    (1818, 243 + i * 35, 1862, 266 + i * 35), 1, "black"
                )
                draw.text((1835, 243 + i * 35), str(q), font=font(19))
            if len(set_bonus) == 1:
                draw.text((1536, 263), n, fill=(0, 255, 0), font=font(23))
                draw.rounded_rectangle((1818, 263, 1862, 288), 1, "black")
                draw.text((1831, 265), str(q), font=font(19))
        return base
