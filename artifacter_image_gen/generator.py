import os
import json
import logging
from collections import Counter
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from enkanetwork import EquipmentsType
import requests

logger = logging.getLogger(__name__)

element_ja = {
    'Anemo': '風',
    'Cryo': '氷',
    'Dendro': '草',
    'Electro': '雷',
    'Geo': '岩',
    'Hydro': '水',
    'Pyro': '炎'
}

prop_id_ja = {
    'FIGHT_PROP_BASE_ATTACK': '基礎攻撃力',
    'FIGHT_PROP_HP': 'HP',
    'FIGHT_PROP_ATTACK': '攻撃力',
    'FIGHT_PROP_DEFENSE': '防御力',
    'FIGHT_PROP_HP_PERCENT': 'HPパーセンテージ',
    'FIGHT_PROP_ATTACK_PERCENT': '攻撃パーセンテージ',
    'FIGHT_PROP_DEFENSE_PERCENT': '防御パーセンテージ',
    'FIGHT_PROP_CRITICAL': '会心率',
    'FIGHT_PROP_CRITICAL_HURT': '会心ダメージ',
    'FIGHT_PROP_CHARGE_EFFICIENCY': '元素チャージ効率',
    'FIGHT_PROP_HEAL_ADD': '与える治癒効果',
    'FIGHT_PROP_ELEMENT_MASTERY': '元素熟知',
    'FIGHT_PROP_PHYSICAL_ADD_HURT': '物理ダメージ',
    'FIGHT_PROP_FIRE_ADD_HURT': '炎元素ダメージ',
    'FIGHT_PROP_ELEC_ADD_HURT': '雷元素ダメージ',
    'FIGHT_PROP_WATER_ADD_HURT': '水元素ダメージ',
    'FIGHT_PROP_WIND_ADD_HURT': '風元素ダメージ',
    'FIGHT_PROP_ICE_ADD_HURT': '氷元素ダメージ',
    'FIGHT_PROP_ROCK_ADD_HURT': '岩元素ダメージ',
    'FIGHT_PROP_GRASS_ADD_HURT': '草元素ダメージ',
}

disper = [
    '会心率', '会心ダメージ', '攻撃パーセンテージ',
    '防御パーセンテージ', 'HPパーセンテージ', '水元素ダメージ',
    '物理ダメージ', '風元素ダメージ', '岩元素ダメージ',
    '炎元素ダメージ', '与える治癒効果', '与える治療効果',
    '雷元素ダメージ', '氷元素ダメージ', '草元素ダメージ',
    '与える治癒効果', '元素チャージ効率'
]

state_op = (
    'HP', '攻撃力', '防御力',
    '元素熟知', '会心率', '会心ダメージ',
    '元素チャージ効率'
)

option_map = {
    '攻撃パーセンテージ': '攻撃%',
    '防御パーセンテージ': '防御%',
    '元素チャージ効率': '元チャ効率',
    'HPパーセンテージ': 'HP%',
}

point_refer = {
    'Total': {
        'SS': 220,
        'S': 200,
        'A': 180
    },
    'EQUIP_BRACER': {
        'SS': 50,
        'S': 45,
        'A': 40
    },
    'EQUIP_NECKLACE': {
        'SS': 50,
        'S': 45,
        'A': 40
    },
    'EQUIP_SHOES': {
        'SS': 45,
        'S': 40,
        'A': 35
    },
    'EQUIP_RING': {
        'SS': 45,
        'S': 40,
        'A': 37
    },
    'EQUIP_DRESS': {
        'SS': 40,
        'S': 35,
        'A': 30
    }
}

dirname = os.path.abspath(os.path.dirname(__file__))


def font(size):
    return ImageFont.truetype(f'{dirname}/assets/font.ttf', size)


def fetch_artifact_props_data():
    filepath = f'{dirname}/cache/artifact_props.json'
    if not os.path.exists(filepath):
        url = ('https://raw.githubusercontent.com/mrwan200/'
               'EnkaNetwork.py/master/enkanetwork/'
               'assets/data/artifact_props.json')
        logger.debug(f'fetch: {url}')
        res = requests.get(url)
        with open(filepath, mode='w') as f:
            f.write(res.text)
    with open(filepath, mode='r') as f:
        return json.loads(f.read())


def fetch_image(name):
    filepath = f'{dirname}/cache/{name}.png'
    if not os.path.exists(filepath):
        url = f'https://enka.network/ui/{name}.png'
        logger.debug(f'fetch: {url}')
        res = requests.get(url)
        image = res.content
        with open(filepath, mode='wb') as f:
            f.write(image)
    return Image.open(filepath)


class Generator:
    artifact_props_data = fetch_artifact_props_data()

    def __init__(self, character) -> None:
        self.character = character
        self.element = character.element.name
        self.artifacts = self.get_artifacts()
        self.weapon = self.get_weapon()

    def get_character_stats(self):
        stats = self.character.stats
        result = {
            'HP': stats.FIGHT_PROP_MAX_HP.to_rounded(),
            '攻撃力': stats.FIGHT_PROP_CUR_ATTACK.to_rounded(),
            '防御力': stats.FIGHT_PROP_CUR_DEFENSE.to_rounded(),
            '元素熟知': stats.FIGHT_PROP_ELEMENT_MASTERY.to_rounded(),
            '会心率': stats.FIGHT_PROP_CRITICAL.to_percentage(),
            '会心ダメージ': stats.FIGHT_PROP_CRITICAL_HURT.to_percentage(),
            '元素チャージ効率': stats.FIGHT_PROP_CHARGE_EFFICIENCY.to_percentage()
        }
        bonuses = {
            '与える治癒効果': stats.FIGHT_PROP_HEAL_ADD.to_percentage(),
            '物理ダメージ': stats.FIGHT_PROP_PHYSICAL_ADD_HURT.to_percentage(),
            '炎元素ダメージ': stats.FIGHT_PROP_FIRE_ADD_HURT.to_percentage(),
            '雷元素ダメージ': stats.FIGHT_PROP_ELEC_ADD_HURT.to_percentage(),
            '水元素ダメージ': stats.FIGHT_PROP_WATER_ADD_HURT.to_percentage(),
            '風元素ダメージ': stats.FIGHT_PROP_WIND_ADD_HURT.to_percentage(),
            '氷元素ダメージ': stats.FIGHT_PROP_ICE_ADD_HURT.to_percentage(),
            '岩元素ダメージ': stats.FIGHT_PROP_ROCK_ADD_HURT.to_percentage(),
            '草元素ダメージ': stats.FIGHT_PROP_GRASS_ADD_HURT.to_percentage()
        }
        bonus = max(bonuses, key=bonuses.get)
        if bonuses[bonus] == 0:
            bonus = f'{element_ja[self.element]}元素ダメージ'
        result[bonus] = bonuses[bonus]

        return result

    def get_character_base_stats(self):
        stats = self.character.stats
        return {
            'HP': stats.BASE_HP.to_rounded(),
            '攻撃力': stats.FIGHT_PROP_BASE_ATTACK.to_rounded(),
            '防御力': stats.FIGHT_PROP_BASE_DEFENSE.to_rounded()
        }

    def get_artifacts(self):
        artifacts = {
            'EQUIP_BRACER': None,
            'EQUIP_NECKLACE': None,
            'EQUIP_SHOES': None,
            'EQUIP_RING': None,
            'EQUIP_DRESS': None
        }
        for equip in self.character.equipments:
            if equip.type == EquipmentsType.ARTIFACT:
                artifacts[equip.detail.artifact_type.value] = equip
        return artifacts

    def get_weapon(self):
        for equip in self.character.equipments:
            if equip.type == EquipmentsType.WEAPON:
                return equip

    def calc_score(self, rates):
        result = {
            'Total': 0,
            'EQUIP_BRACER': 0,
            'EQUIP_NECKLACE': 0,
            'EQUIP_SHOES': 0,
            'EQUIP_RING': 0,
            'EQUIP_DRESS': 0
        }
        for artifact_type, artifact in self.artifacts.items():
            if not artifact:
                continue
            v = {}
            for i in prop_id_ja.keys():
                v[i] = 0
            score = 0
            for stat in artifact.detail.substats:
                v[stat.prop_id] = stat.value
            for prop_id, rate in rates.items():
                score += v[prop_id] * rate
            result[artifact_type] = score
            result['Total'] += score
        return result

    def generate(
            self,
            rates,
            point_refer=point_refer,
            label=''
    ):
        score = self.calc_score(rates)
        base = Image.open(f'{dirname}/assets/base/{self.element}.png')
        base = self._draw_character(base)
        base = self._draw_weapon(base)
        base = self._draw_weapon_rarity(base)
        base = self._draw_skills(base)
        base = self._draw_constellation(base)
        base = self._draw_level(base)   # level, friendship_level
        base = self._draw_skill_level(base)
        base = self._draw_character_stats(base)
        base = self._draw_weapon_stats(base)
        base = self._draw_total_score(base, score, label)
        base = self._draw_artifacts(base, score, point_refer)

        return base

    def _draw_character(self, base):
        character = self.character
        image = fetch_image(character.image.banner.filename)
        image = image.convert('RGBA')
        if character.id == 10000005:
            # 空
            tmp = Image.new('RGBA', (2048, 1024), (255, 255, 255, 0))
            image = image.resize((909, 1024))
            tmp.paste(image, (570, 0))
            image = tmp
        elif character.id == 10000007:
            # 蛍
            tmp = Image.new('RGBA', (2048, 1024), (255, 255, 255, 0))
            image = image.resize((880, 1024))
            tmp.paste(image, (584, 0))
            image = tmp
        image = image.crop((289, 0, 1728, 1024))
        image = image.resize(
            (int(image.width * 0.75), int(image.height * 0.75)))
        mask1 = image.copy()
        if character.id == 10000078:
            # アルハイゼン
            mask2 = Image.open(f'{dirname}/assets/alhaitham_mask.png')
        else:
            mask2 = Image.open(f'{dirname}/assets/character_mask.png')
        mask2 = mask2.convert('L')
        mask2 = mask2.resize(image.size)
        shadow = Image.open(f'{dirname}/assets/shadow.png')
        shadow = shadow.resize(base.size)
        image.putalpha(mask2)
        paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
        paste.paste(image, (-160, -45), mask=mask1)
        base = Image.alpha_composite(base, paste)
        base = Image.alpha_composite(base, shadow)
        return base

    def _draw_weapon(self, base):
        weapon = self.weapon
        image = fetch_image(weapon.detail.icon.filename)
        image = image.convert('RGBA')
        image = image.resize((128, 128))
        mask = image.copy()
        paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
        paste.paste(image, (1430, 50), mask=mask)
        base = Image.alpha_composite(base, paste)
        return base

    def _draw_weapon_rarity(self, base):
        rarity = self.weapon.detail.rarity
        image = Image.open(f'{dirname}/assets/rarity/{rarity}.png')
        image = image.convert('RGBA')
        image = image.resize(
            (int(image.width * 0.97), int(image.height * 0.97)))
        paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
        mask = image.copy()
        paste.paste(image, (1422, 173), mask=mask)
        base = Image.alpha_composite(base, paste)
        return base

    def _draw_skills(self, base):
        skills = self.character.skills
        bg = Image.open(f'{dirname}/assets/skill_back.png')
        bg = bg.resize((int(bg.width/1.5), int(bg.height/1.5)))
        bg_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
        for i in range(3):
            skill = skills[i]
            image = fetch_image(skill.icon.filename)
            image = image.resize((50, 50))
            image = image.convert('RGBA')
            mask = image.copy()
            paste = Image.new('RGBA', bg.size, (255, 255, 255, 0))
            paste.paste(image, (paste.width//2-25,
                        paste.height//2-25), mask=mask)
            bg_paste.paste(Image.alpha_composite(bg, paste), (15, 330+i*105))
        base = Image.alpha_composite(base, bg_paste)
        return base

    def _draw_constellation(self, base):
        bg = Image.open(f'{dirname}/assets/constellation/{self.element}.png')
        bg = bg.resize((90, 90))
        bg = bg.convert('RGBA')
        lock = Image.open(
            f'{dirname}/assets/constellation/{self.element}_lock.png')
        lock = lock.resize((90, 90))
        lock = lock.convert('RGBA')
        lock_mask = lock.copy()
        bg_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
        for i, c in enumerate(self.character.constellations, 1):
            if not c.unlocked:
                bg_paste.paste(lock, (666, -10+i*93), mask=lock_mask)
            else:
                image = fetch_image(c.icon.filename)
                image = image.convert('RGBA')
                image = image.resize((45, 45))
                paste = Image.new('RGBA', bg.size, (255, 255, 255, 0))
                mask = image.copy()
                paste.paste(image, (int(paste.width/2)-25,
                                    int(paste.height/2)-23), mask=mask)
                bg_paste.paste(Image.alpha_composite(
                    bg, paste), (666, -10+i*93))
        base = Image.alpha_composite(base, bg_paste)
        return base

    def _draw_level(self, base):
        draw = ImageDraw.Draw(base)
        character = self.character

        draw.text((30, 20), character.name, font=font(48))
        level_length = draw.textlength(
            'Lv.'+str(character.level), font=font(25))
        friendship_length = draw.textlength(
            str(character.friendship_level), font=font(25))
        draw.text((35, 75), 'Lv.'+str(character.level), font=font(25))
        draw.rounded_rectangle(
            (
                35+level_length+5,
                74,
                77+level_length + friendship_length,
                102
            ), radius=2, fill='black')
        friendship_icon = Image.open(
            f'{dirname}/assets/friendship.png').convert('RGBA')
        friendship_icon = friendship_icon.resize(
            (int(friendship_icon.width*(24/friendship_icon.height)), 24))
        friendship_icon_mask = friendship_icon.copy()
        base.paste(friendship_icon, (42+int(level_length), 76),
                   mask=friendship_icon_mask)
        draw.text((73+level_length, 74),
                  str(character.friendship_level), font=font(25))
        return base

    def _draw_skill_level(self, base):
        draw = ImageDraw.Draw(base)
        skills = self.character.skills

        for i in range(3):
            draw.text(
                (42, 397+i*105),
                f'Lv.{skills[i].level}',
                font=font(17),
                fill='aqua' if skills[i].level >= 10 else None
            )
        return base

    def _draw_character_stats(self, base):
        draw = ImageDraw.Draw(base)
        stats = self.get_character_stats()
        base_stats = self.get_character_base_stats()
        for name, value in stats.items():
            try:
                i = state_op.index(name)
            except Exception:
                i = 7
                draw.text((844, 67+i*70), name, font=font(26))
                icon = Image.open(f'{dirname}/assets/emotes/{name}.png')
                icon = icon.resize((40, 40))
                icon_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
                icon_paste.paste(icon, (789, 65+i*70))
                base = Image.alpha_composite(base, icon_paste)
                draw = ImageDraw.Draw(base)

            if name not in disper:
                state_len = draw.textlength(format(value, ','), font(26))
                draw.text((1360-state_len, 67+i*70),
                          format(value, ','), font=font(26))
            else:
                state_len = draw.textlength(f'{float(value)}%', font(26))
                draw.text((1360-state_len, 67+i*70),
                          f'{float(value)}%', font=font(26))

            if name in ['HP', '防御力', '攻撃力']:
                base_value = base_stats[name]
                diff = value - base_value
                diff_len = draw.textlength(
                    f'+{format(diff,",")}', font=font(12))
                base_value_len = draw.textlength(
                    f'{format(base_value,",")}', font=font(12))
                draw.text(
                    (1360-diff_len, 97+i*70),
                    f'+{format(diff,",")}',
                    fill=(0, 255, 0, 180),
                    font=font(12)
                )
                draw.text(
                    (1360-diff_len-base_value_len-1, 97+i*70),
                    f'{format(base_value,",")}',
                    font=font(12),
                    fill=(255, 255, 255, 180)
                )
        return base

    def _draw_weapon_stats(self, base):
        draw = ImageDraw.Draw(base)
        weapon = self.weapon
        level = weapon.level
        draw.text((1582, 47), weapon.detail.name, font=font(26))
        level_len = draw.textlength(f'Lv.{level}', font=font(24))
        draw.rounded_rectangle((1582, 80, 1582+level_len+4, 108),
                               radius=1, fill='black')
        draw.text((1584, 82), f'Lv.{level}', font=font(24))

        base_atk_image = Image.open(f'{dirname}/assets/emotes/基礎攻撃力.png')
        base_atk_image = base_atk_image.resize((23, 23))
        base_atk_mask = base_atk_image.copy()
        base.paste(base_atk_image, (1600, 120), mask=base_atk_mask)
        draw.text(
            (1623, 120),
            f'基礎攻撃力  {weapon.detail.mainstats.value}',
            font=font(23)
        )

        if weapon.detail.substats:
            substat = weapon.detail.substats[0]
            substat_name = prop_id_ja[substat.prop_id]
            substat_image = Image.open(
                f'{dirname}/assets/emotes/{substat_name}.png').resize((23, 23))
            weapon_substat_mask = substat_image.copy()
            base.paste(substat_image, (1600, 155),
                       mask=weapon_substat_mask)

            draw.text(
                (1623, 155),
                f'''{
                    option_map.get(substat_name) or substat_name
                }  {
                    str(substat.value)+'%'
                    if substat_name in disper
                    else format(substat.value,',')
                }''', font=font(23))

        draw.rounded_rectangle((1430, 45, 1470, 70), radius=1, fill='black')
        draw.text((1433, 46), f'R{weapon.refinement}', font=font(24))
        return base

    def _draw_total_score(self, base, score, label):
        draw = ImageDraw.Draw(base)
        total_score = float(format(score["Total"], '.1f'))
        score_len = draw.textlength(str(total_score), font(75))
        draw.text(
            (1652-score_len//2, 420),
            str(total_score),
            font=font(75)
        )
        text_len = draw.textlength(label, font=font(24))
        draw.text((1867-text_len, 585), label, font=font(24))

        if score['Total'] >= 220:
            grade = Image.open(f'{dirname}/assets/grade/SS.png')
        elif score['Total'] >= 200:
            grade = Image.open(f'{dirname}/assets/grade/S.png')
        elif score['Total'] >= 180:
            grade = Image.open(f'{dirname}/assets/grade/A.png')
        else:
            grade = Image.open(f'{dirname}/assets/grade/B.png')

        grade = grade.resize((grade.width//8, grade.height//8))
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
            artifact_type.append(artifact.detail.artifact_name_set)
            paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
            image = fetch_image(artifact.detail.icon.filename)
            image = image.resize((256, 256))
            image = ImageEnhance.Brightness(image).enhance(0.6)
            image = image.resize((int(image.width*1.3), int(image.height*1.3)))
            mask1 = Image.open(f'{dirname}/assets/artifact_mask.png')
            mask1 = mask1.convert('L')
            mask1 = mask1.resize(image.size)
            mask2 = image.copy()
            image.putalpha(mask1)
            if parts in ['EQUIP_BRACER', 'EQUIP_DRESS']:
                paste.paste(image, (-37+373*i, 570), mask=mask2)
            elif parts in ['EQUIP_NECKLACE', 'EQUIP_RING']:
                paste.paste(image, (-36+373*i, 570), mask=mask2)
            else:
                paste.paste(image, (-35+373*i, 570), mask=mask2)
            base = Image.alpha_composite(base, paste)
            draw = ImageDraw.Draw(base)

            mainstat = artifact.detail.mainstats

            mainstat_len = draw.textlength(
                option_map.get(prop_id_ja[mainstat.prop_id]) or
                prop_id_ja[mainstat.prop_id],
                font=font(29)
            )
            draw.text(
                (375+i*373-int(mainstat_len), 655),
                option_map.get(prop_id_ja[mainstat.prop_id]
                               ) or prop_id_ja[mainstat.prop_id],
                font=font(29)
            )
            mainstat_icon = Image.open(
                f'{dirname}/assets/emotes/{prop_id_ja[mainstat.prop_id]}.png'
            ).convert('RGBA').resize((35, 35))
            mainstat_mask = mainstat_icon.copy()
            base.paste(
                mainstat_icon,
                (340+i*373 - int(mainstat_len), 655),
                mask=mainstat_mask
            )

            if mainstat in disper:
                mainstat_value_size = draw.textlength(
                    f'{float(mainstat.value)}%', font(49))
                draw.text((375+i*373-mainstat_value_size, 690),
                          f'{float(mainstat.value)}%', font=font(49))
            else:
                mainstat_value_size = draw.textlength(
                    format(mainstat.value, ','), font(49))
                draw.text((375+i*373-mainstat_value_size, 690),
                          format(mainstat.value, ','), font=font(49))

            level_len = draw.textlength(f'+{artifact.level}', font(21))
            draw.rounded_rectangle((373+i*373-int(level_len), 748,
                                    375+i*373, 771), fill='black', radius=2)
            draw.text((374+i*373-level_len, 749),
                      f'+{artifact.level}', font=font(21))

            affix = {}
            for prop in artifact.props:
                stat_name = prop_id_ja[prop.prop_id]
                if stat_name not in affix.keys():
                    affix[stat_name] = []
                affix[stat_name].append(
                    self.artifact_props_data[str(prop.id)]['propValue'])

            substats = artifact.detail.substats

            for a, stat in enumerate(substats):
                stat_name = prop_id_ja[stat.prop_id]
                if stat_name in ['HP', '攻撃力', '防御力']:
                    draw.text(
                        (79+373*i, 811+50*a),
                        option_map.get(stat_name) or stat_name,
                        font=font(25), fill=(255, 255, 255, 190)
                    )
                else:
                    draw.text((79+373*i, 811+50*a), option_map.get(stat_name)
                              or stat_name, font=font(25))
                substat_icon = Image.open(
                    f'{dirname}/assets/emotes/{stat_name}.png')
                substat_icon = substat_icon.resize((30, 30))
                substat_mask = substat_icon.copy()
                base.paste(substat_icon, (44+373*i, 811+50*a),
                           mask=substat_mask)
                if stat_name in disper:
                    substat_size = draw.textlength(
                        f'{float(stat.value)}%', font(25))
                    draw.text((375+i*373-substat_size, 811+50*a),
                              f'{float(stat.value)}%', font=font(25))
                else:
                    substat_size = draw.textlength(
                        format(stat.value, ','), font(25))
                    if stat_name in ['防御力', '攻撃力', 'HP']:
                        draw.text(
                            (375+i*373-substat_size, 811+50*a),
                            format(stat.value, ','),
                            font=font(25),
                            fill=(255, 255, 255, 190)
                        )
                    else:
                        draw.text(
                            (375+i*373-substat_size, 811+50*a),
                            format(stat.value, ','),
                            font=font(25),
                            fill=(255, 255, 255)
                        )

                affix_len = draw.textlength(
                    '+'.join(map(str, affix[stat_name])), font=font(11))
                draw.text(
                    (375+i*373-affix_len, 840+50*a),
                    '+'.join(map(str, affix[stat_name])),
                    fill=(255, 255, 255, 160),
                    font=font(11)
                )

            artifact_score = float(format(score[parts], '.1f'))
            score_len = draw.textlength(str(artifact_score), font(36))
            draw.text((380+i*373-score_len, 1016),
                      str(artifact_score), font=font(36))
            draw.text((295+i*373-score_len, 1025), 'Score',
                      font=font(27), fill=(160, 160, 160))

            if artifact_score >= point_refer[parts]['SS']:
                grade_image = Image.open(f'{dirname}/assets/grade/SS.png')
            elif artifact_score >= point_refer[parts]['S']:
                grade_image = Image.open(f'{dirname}/assets/grade/S.png')
            elif artifact_score >= point_refer[parts]['A']:
                grade_image = Image.open(f'{dirname}/assets/grade/A.png')
            else:
                grade_image = Image.open(f'{dirname}/assets/grade/B.png')

            grade_image = grade_image.resize(
                (grade_image.width//11, grade_image.height//11))
            grade_mask = grade_image.copy()

            base.paste(grade_image, (85+373*i, 1013), mask=grade_mask)

        set_bonus = Counter([
            x
            for x in artifact_type
            if artifact_type.count(x) >= 2
        ])
        for i, (n, q) in enumerate(set_bonus.items()):
            if len(set_bonus) == 2:
                draw.text((1536, 243+i*35), n, fill=(0, 255, 0), font=font(23))
                draw.rounded_rectangle(
                    (1818, 243+i*35, 1862, 266+i*35), 1, 'black')
                draw.text((1835, 243+i*35), str(q), font=font(19))
            if len(set_bonus) == 1:
                draw.text((1536, 263), n, fill=(0, 255, 0), font=font(23))
                draw.rounded_rectangle((1818, 263, 1862, 288), 1, 'black')
                draw.text((1831, 265), str(q), font=font(19))
        return base


if __name__ == '__main__':
    from enkanetwork import EnkaNetworkAPI
    import asyncio

    async def test():
        rates = {
            'FIGHT_PROP_CRITICAL': 2,
            'FIGHT_PROP_CRITICAL_HURT': 1,
            'FIGHT_PROP_ATTACK_PERCENT': 1
        }
        client = EnkaNetworkAPI(lang='jp')
        async with client:
            data = await client.fetch_user(618285856)
            img = Generator(data.characters[0]).generate(
                rates=rates,
                label='攻撃%!!'
            )
            img.show()

    asyncio.run(test())
