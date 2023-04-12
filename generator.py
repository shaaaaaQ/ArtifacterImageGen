import json
import os
import itertools
from collections import Counter
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from enkanetwork import EquipmentsType
import requests

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

point_refer = {
    "Total": {
        "SS": 220,
        "S": 200,
        "A": 180
    },
    "EQUIP_BRACER": {
        "SS": 50,
        "S": 45,
        "A": 40
    },
    "EQUIP_NECKLACE": {
        "SS": 50,
        "S": 45,
        "A": 40
    },
    "EQUIP_SHOES": {
        "SS": 45,
        "S": 40,
        "A": 35
    },
    "EQUIP_RING": {
        "SS": 45,
        "S": 40,
        "A": 37
    },
    "EQUIP_DRESS": {
        "SS": 40,
        "S": 35,
        "A": 30
    }
}

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

cwd = os.path.abspath(os.path.dirname(__file__))


def font(size):
    return ImageFont.truetype(f'{cwd}/assets/ja-jp.ttf', size)


def read_json(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return json.load(f)


def fetch_image(name):
    filepath = f'{cwd}/cache/{name}.png'
    if not os.path.exists(filepath):
        url = f'https://enka.network/ui/{name}.png'
        print(f'fetch: {url}')
        res = requests.get(url)
        image = res.content
        with open(filepath, mode='wb') as f:
            f.write(image)
    return Image.open(filepath)


def calculate_op(data: dict):
    dup = read_json(f'{cwd}/assets/duplicate.json')
    mapping = read_json(f'{cwd}/assets/subopM.json')

    res = [None, None, None, None]
    keymap = list(map(str, data.keys()))

    is_dup = []
    # 重複するものがあるか判定
    for ctg, state in data.items():
        dup_value = dup[ctg]['ov']
        if str(state) in dup_value:
            is_dup.append((ctg, state))

    # フラグの設定
    counter_flag = 0
    dup_ctg = [i[0] for i in is_dup]
    maxium_state_ct = 9

    # 重複が 0 の時の処理
    if not len(is_dup):
        for ctg, state in data.items():
            idx = keymap.index(ctg)
            res[idx] = mapping[ctg][str(state)]
        return res

    # 重複するものが一つの場合

    if len(is_dup) == 1:
        # 重複のないもの
        single_state = {c: s for c, s in data.items() if c not in dup_ctg}
        for ctg, state in single_state.items():
            idx = keymap.index(ctg)
            res[idx] = mapping[ctg][str(state)]
            counter_flag += len(mapping[ctg][str(state)])

        # 重複するもの
        dup_state = {c: s for c, s in data.items() if c in dup_ctg}
        long = maxium_state_ct - counter_flag
        possiblity = []

        for ctg, state in dup_state.items():
            possiblity = dup[ctg][str(state)]
            for p in possiblity:
                if len(p) == long or len(p) == long-1:
                    idx = keymap.index(ctg)
                    res[idx] = p
                    return res

    # 重複するものが複数の場合
    if len(is_dup) == 2:
        single_state = {c: s for c, s in data.items() if c not in dup_ctg}
        for ctg, state in single_state.items():
            idx = keymap.index(ctg)
            res[idx] = mapping[ctg][str(state)]
            counter_flag += len(mapping[ctg][str(state)])

        dup_state = {c: s for c, s in data.items() if c in dup_ctg}
        long = maxium_state_ct - counter_flag

        sample = [[ctg, state]for ctg, state in dup_state.items()]

        possiblity1 = dup[sample[0][0]][str(sample[0][1])]
        possiblity2 = dup[sample[1][0]][str(sample[1][1])]

        p1 = [len(p) for p in possiblity1]
        p2 = [len(p) for p in possiblity2]

        p = itertools.product(p1, p2)
        for v in p:
            if sum(v) == long or sum(v) == long-1:
                break

        idx1 = keymap.index(sample[0][0])
        idx2 = keymap.index(sample[1][0])

        res[idx1] = possiblity1[p1.index(v[0])]
        res[idx2] = possiblity2[p2.index(v[1])]
        return res

    if len(is_dup) == 3:
        single_state = {c: s for c, s in data.items() if c not in dup_ctg}
        for ctg, state in single_state.items():
            idx = keymap.index(ctg)
            res[idx] = mapping[ctg][str(state)]
            counter_flag += len(mapping[ctg][str(state)])

        dup_state = {c: s for c, s in data.items() if c in dup_ctg}
        long = maxium_state_ct - counter_flag

        sample = [[ctg, state]for ctg, state in dup_state.items()]

        possiblity1 = dup[sample[0][0]][str(sample[0][1])]
        possiblity2 = dup[sample[1][0]][str(sample[1][1])]
        possiblity3 = dup[sample[2][0]][str(sample[2][1])]

        p1 = [len(p) for p in possiblity1]
        p2 = [len(p) for p in possiblity2]
        p3 = [len(p) for p in possiblity3]

        p = itertools.product(p1, p2, p3)
        for v in p:
            if sum(v) == long or sum(v) == long-1:
                break

        idx1 = keymap.index(sample[0][0])
        idx2 = keymap.index(sample[1][0])
        idx3 = keymap.index(sample[2][0])

        res[idx1] = possiblity1[p1.index(v[0])]
        res[idx2] = possiblity2[p2.index(v[1])]
        res[idx3] = possiblity3[p3.index(v[2])]

        return res

    if len(is_dup) == 4:
        dup_state = {c: s for c, s in data.items() if c in dup_ctg}
        long = maxium_state_ct - counter_flag

        sample = [[ctg, state]for ctg, state in dup_state.items()]

        possiblity1 = dup[sample[0][0]][str(sample[0][1])]
        possiblity2 = dup[sample[1][0]][str(sample[1][1])]
        possiblity3 = dup[sample[2][0]][str(sample[2][1])]
        possiblity4 = dup[sample[3][0]][str(sample[3][1])]

        p1 = [len(p) for p in possiblity1]
        p2 = [len(p) for p in possiblity2]
        p3 = [len(p) for p in possiblity3]
        p4 = [len(p) for p in possiblity4]

        p = itertools.product(p1, p2, p3, p4)
        for v in p:
            if sum(v) == long or sum(v) == long-1:
                break

        idx1 = keymap.index(sample[0][0])
        idx2 = keymap.index(sample[1][0])
        idx3 = keymap.index(sample[2][0])
        idx4 = keymap.index(sample[3][0])

        res[idx1] = possiblity1[p1.index(v[0])]
        res[idx2] = possiblity2[p2.index(v[1])]
        res[idx3] = possiblity3[p3.index(v[2])]
        res[idx4] = possiblity4[p4.index(v[3])]

        return res
    return


def generate(character):
    element = character.element.name
    character_stats = {
        'HP': character.stats.FIGHT_PROP_MAX_HP.to_rounded(),
        "攻撃力": character.stats.FIGHT_PROP_CUR_ATTACK.to_rounded(),
        "防御力": character.stats.FIGHT_PROP_CUR_DEFENSE.to_rounded(),
        "元素熟知": character.stats.FIGHT_PROP_ELEMENT_MASTERY.to_rounded(),
        "会心率": character.stats.FIGHT_PROP_CRITICAL.to_percentage(),
        "会心ダメージ": character.stats.FIGHT_PROP_CRITICAL_HURT.to_percentage(),
        "元素チャージ効率":
            character.stats.FIGHT_PROP_CHARGE_EFFICIENCY.to_percentage()
    }
    character_base_stats = {
        "HP": character.stats.BASE_HP.to_rounded(),
        "攻撃力": character.stats.FIGHT_PROP_BASE_ATTACK.to_rounded(),
        "防御力": character.stats.FIGHT_PROP_BASE_DEFENSE.to_rounded()
    }
    character_add_stats = {
        '与える治癒効果': character.stats.FIGHT_PROP_HEAL_ADD.to_percentage(),
        '物理ダメージ': character.stats.FIGHT_PROP_PHYSICAL_ADD_HURT.to_percentage(),
        '炎元素ダメージ': character.stats.FIGHT_PROP_FIRE_ADD_HURT.to_percentage(),
        '雷元素ダメージ': character.stats.FIGHT_PROP_ELEC_ADD_HURT.to_percentage(),
        '水元素ダメージ': character.stats.FIGHT_PROP_WATER_ADD_HURT.to_percentage(),
        '風元素ダメージ': character.stats.FIGHT_PROP_WIND_ADD_HURT.to_percentage(),
        '氷元素ダメージ': character.stats.FIGHT_PROP_ICE_ADD_HURT.to_percentage(),
        '岩元素ダメージ': character.stats.FIGHT_PROP_ROCK_ADD_HURT.to_percentage(),
        '草元素ダメージ': character.stats.FIGHT_PROP_GRASS_ADD_HURT.to_percentage()
    }
    add_stat = max(character_add_stats, key=character_add_stats.get)
    if character_add_stats[add_stat] == 0:
        add_stat = f'{element_ja[element]}元素ダメージ'
    character_stats[add_stat] = character_add_stats[add_stat]

    artifacts = {
        'EQUIP_BRACER': None,
        "EQUIP_NECKLACE": None,
        "EQUIP_SHOES": None,
        "EQUIP_RING": None,
        "EQUIP_DRESS": None
    }

    for equip in character.equipments:
        if equip.type == EquipmentsType.WEAPON:
            weapon = equip
        elif equip.type == EquipmentsType.ARTIFACT:
            artifacts[equip.detail.artifact_type.value] = equip

    # スコア
    score = {
        'State': 'HP',
        'Total': 0,
        "EQUIP_BRACER": 0,
        "EQUIP_NECKLACE": 0,
        "EQUIP_SHOES": 0,
        "EQUIP_RING": 0,
        "EQUIP_DRESS": 0
    }

    # base
    base = Image.open(f'{cwd}/assets/base/{element}.png')

    # character
    character_image = fetch_image(
        character.image.banner.filename).convert('RGBA')
    character_image = character_image.crop((289, 0, 1728, 1024))
    character_image = character_image.resize(
        (int(character_image.width*0.75), int(character_image.height*0.75)))
    character_mask = character_image.copy()
    character_mask2 = Image.open(
        f'{cwd}/assets/character_mask.png'
    ).convert('L').resize(character_image.size)
    character_image.putalpha(character_mask2)
    character_shadow = Image.open(f'{cwd}/assets/shadow.png').resize(base.size)
    character_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
    character_paste.paste(
        character_image,
        (-160, -45),
        mask=character_mask
    )
    base = Image.alpha_composite(base, character_paste)
    base = Image.alpha_composite(base, character_shadow)

    # weapon
    weapon_rarity = weapon.detail.rarity
    weapon_image = fetch_image(weapon.detail.icon.filename).convert(
        'RGBA').resize((128, 128))
    weapon_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
    weapon_mask = weapon_image.copy()
    weapon_paste.paste(weapon_image, (1430, 50), mask=weapon_mask)
    base = Image.alpha_composite(base, weapon_paste)

    weapon_r_image = Image.open(
        f'{cwd}/assets/rarity/{weapon_rarity}.png').convert('RGBA')
    weapon_r_image = weapon_r_image.resize(
        (int(weapon_r_image.width*0.97), int(weapon_r_image.height*0.97)))
    weapon_r_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
    weapon_r_mask = weapon_r_image.copy()
    weapon_r_paste.paste(weapon_r_image, (1422, 173), mask=weapon_r_mask)
    base = Image.alpha_composite(base, weapon_r_paste)

    # skill
    skill_base = Image.open(f'{cwd}/assets/skill_back.png')
    skill_base_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
    skill_base = skill_base.resize(
        (int(skill_base.width/1.5), int(skill_base.height/1.5)))

    for i in range(3):
        skill = character.skills[i]
        skill_paste = Image.new('RGBA', skill_base.size, (255, 255, 255, 0))
        skill_image = fetch_image(skill.icon.filename).resize(
            (50, 50)).convert('RGBA')
        skill_mask = skill_image.copy()
        skill_paste.paste(skill_image, (skill_paste.width//2-25,
                          skill_paste.height//2-25), mask=skill_mask)

        skill_object = Image.alpha_composite(skill_base, skill_paste)
        skill_base_paste.paste(skill_object, (15, 330+i*105))

    base = Image.alpha_composite(base, skill_base_paste)

    # constellation
    c_base = Image.open(
        f'{cwd}/assets/constellation/{element}.png'
    ).resize((90, 90)).convert('RGBA')
    c_lock = Image.open(
        f'{cwd}/assets/constellation/{element}_lock.png'
    ).resize((90, 90)).convert('RGBA')
    c_lock_mask = c_lock.copy()

    c_base_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
    for i, c in enumerate(character.constellations, 1):
        if not c.unlocked:
            c_base_paste.paste(c_lock, (666, -10+i*93), mask=c_lock_mask)
        else:
            c_image = fetch_image(c.icon.filename).convert(
                'RGBA').resize((45, 45))
            c_paste = Image.new('RGBA', c_base.size, (255, 255, 255, 0))
            c_mask = c_image.copy()
            c_paste.paste(c_image, (int(c_paste.width/2)-25,
                                    int(c_paste.height/2)-23), mask=c_mask)

            c_object = Image.alpha_composite(c_base, c_paste)
            c_base_paste.paste(c_object, (666, -10+i*93))

    base = Image.alpha_composite(base, c_base_paste)

    # 文字
    draw = ImageDraw.Draw(base)

    draw.text((30, 20), character.name, font=font(48))
    level_length = draw.textlength('Lv.'+str(character.level), font=font(25))
    friendship_length = draw.textlength(
        str(character.friendship_level), font=font(25))
    draw.text((35, 75), 'Lv.'+str(character.level), font=font(25))
    draw.rounded_rectangle((35+level_length+5, 74, 77+level_length +
                            friendship_length, 102), radius=2, fill='black')
    friendship_icon = Image.open(
        f'{cwd}/assets/friendship.png').convert('RGBA')
    friendship_icon = friendship_icon.resize(
        (int(friendship_icon.width*(24/friendship_icon.height)), 24))
    friendship_icon_mask = friendship_icon.copy()
    base.paste(friendship_icon, (42+int(level_length), 76),
               mask=friendship_icon_mask)
    draw.text((73+level_length, 74),
              str(character.friendship_level), font=font(25))

    # 天賦レベル
    for i in range(3):
        draw.text(
            (42, 397+i*105),
            f'Lv.{character.skills[i].level}',
            font=font(17),
            fill='aqua' if character.skills[i].level >= 10 else None
        )

    # キャラのステータス
    def generate_base_text(stat):
        stats = character_stats
        base_stats = character_base_stats
        sumv = stats[stat]
        plusv = sumv - base_stats[stat]
        basev = base_stats[stat]
        return (
            f"+{format(plusv,',')}",
            f"{format(basev,',')}",
            draw.textlength(f"+{format(plusv,',')}", font=font(12)),
            draw.textlength(f"{format(basev,',')}", font=font(12))
        )

    for k, v in character_stats.items():
        try:
            i = state_op.index(k)
        except Exception:
            i = 7
            draw.text((844, 67+i*70), k, font=font(26))
            op_icon = Image.open(
                f'{cwd}/assets/emotes/{k}.png').resize((40, 40))
            op_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
            # opmask = opicon.copy()
            op_paste.paste(op_icon, (789, 65+i*70))
            base = Image.alpha_composite(base, op_paste)
            draw = ImageDraw.Draw(base)

        if k not in disper:
            state_len = draw.textlength(format(v, ","), font(26))
            draw.text((1360-state_len, 67+i*70), format(v, ","), font=font(26))
        else:
            state_len = draw.textlength(f'{float(v)}%', font(26))
            draw.text((1360-state_len, 67+i*70), f'{float(v)}%', font=font(26))

        if k in ['HP', '防御力', '攻撃力']:
            hp_pls, hp_base, hp_size, hp_b_size = generate_base_text(k)
            draw.text((1360-hp_size, 97+i*70), hp_pls,
                      fill=(0, 255, 0, 180), font=font(12))
            draw.text((1360-hp_size-hp_b_size-1, 97+i*70), hp_base,
                      font=font(12), fill=(255, 255, 255, 180))

    draw.text((1582, 47), weapon.detail.name, font=font(26))
    weapon_level_len = draw.textlength(f'Lv.{weapon.level}', font=font(24))
    draw.rounded_rectangle((1582, 80, 1582+weapon_level_len+4, 108),
                           radius=1, fill='black')
    draw.text((1584, 82), f'Lv.{weapon.level}', font=font(24))

    base_atk_image = Image.open(
        f'{cwd}/assets/emotes/基礎攻撃力.png').resize((23, 23))
    base_atk_mask = base_atk_image.copy()
    base.paste(base_atk_image, (1600, 120), mask=base_atk_mask)
    draw.text(
        (1623, 120), f'基礎攻撃力  {weapon.detail.mainstats.value}', font=font(23))

    option_map = {
        "攻撃パーセンテージ": "攻撃%",
        "防御パーセンテージ": "防御%",
        "元素チャージ効率": "元チャ効率",
        "HPパーセンテージ": "HP%",
    }
    if weapon.detail.substats:
        weapon_substat = weapon.detail.substats[0]
        weapon_substat_name = prop_id_ja[weapon_substat.prop_id]
        weapon_substat_image = Image.open(
            f'{cwd}/assets/emotes/{weapon_substat_name}.png').resize((23, 23))
        weapon_substat_mask = weapon_substat_image.copy()
        base.paste(weapon_substat_image, (1600, 155), mask=weapon_substat_mask)

        draw.text(
            (1623, 155),
            f'''{
                option_map.get(weapon_substat_name) or weapon_substat_name
            }  {
                str(weapon_substat.value)+"%"
                if weapon_substat_name in disper
                else format(weapon_substat.value,",")
            }''', font=font(23))

    draw.rounded_rectangle((1430, 45, 1470, 70), radius=1, fill='black')
    draw.text((1433, 46), f'R{weapon.refinement}', font=font(24))

    score_len = draw.textlength(f'{score["Total"]}', font(75))
    draw.text((1652-score_len//2, 420), str(score["Total"]), font=font(75))
    b_len = draw.textlength(f'{score["State"]}換算', font=font(24))
    draw.text((1867-b_len, 585), f'{score["State"]}換算', font=font(24))

    if score["Total"] >= 220:
        score_ev = Image.open(f'{cwd}/assets/grade/SS.png')
    elif score["Total"] >= 200:
        score_ev = Image.open(f'{cwd}/assets/grade/S.png')
    elif score["Total"] >= 180:
        score_ev = Image.open(f'{cwd}/assets/grade/A.png')
    else:
        score_ev = Image.open(f'{cwd}/assets/grade/B.png')

    score_ev = score_ev.resize((score_ev.width//8, score_ev.height//8))
    score_ev_mask = score_ev.copy()

    base.paste(score_ev, (1806, 345), mask=score_ev_mask)

    # 聖遺物
    artifact_type = []
    for i, parts in enumerate(artifacts.keys()):
        artifact = artifacts.get(parts)

        if not artifact:
            continue
        artifact_type.append(artifact.detail.artifact_name_set)
        artifact_paste = Image.new('RGBA', base.size, (255, 255, 255, 0))
        artifact_image = fetch_image(
            artifact.detail.icon.filename).resize((256, 256))
        artifact_enhancer = ImageEnhance.Brightness(artifact_image)
        artifact_image = artifact_enhancer.enhance(0.6)
        artifact_image = artifact_image.resize(
            (int(artifact_image.width*1.3), int(artifact_image.height*1.3)))
        artifact_mask2 = artifact_image.copy()

        artifact_mask = Image.open(
            f'{cwd}/assets/artifact_mask.png'
        ).convert('L').resize(artifact_image.size)
        artifact_image.putalpha(artifact_mask)
        if parts in ['EQUIP_BRACER', 'EQUIP_DRESS']:
            artifact_paste.paste(
                artifact_image, (-37+373*i, 570), mask=artifact_mask2)
        elif parts in ['EQUIP_NECKLACE', 'EQUIP_RING']:
            artifact_paste.paste(
                artifact_image, (-36+373*i, 570), mask=artifact_mask2)
        else:
            artifact_paste.paste(
                artifact_image, (-35+373*i, 570), mask=artifact_mask2)
        base = Image.alpha_composite(base, artifact_paste)
        draw = ImageDraw.Draw(base)

        mainstat = artifact.detail.mainstats

        mainstat_len = draw.textlength(
            option_map.get(
                prop_id_ja[mainstat.prop_id]) or prop_id_ja[mainstat.prop_id],
            font=font(29)
        )
        draw.text(
            (375+i*373-int(mainstat_len), 655),
            option_map.get(prop_id_ja[mainstat.prop_id]
                           ) or prop_id_ja[mainstat.prop_id],
            font=font(29)
        )
        mainstat_icon = Image.open(
            f'{cwd}/assets/emotes/{prop_id_ja[mainstat.prop_id]}.png'
        ).convert("RGBA").resize((35, 35))
        mainstat_mask = mainstat_icon.copy()
        base.paste(mainstat_icon, (340+i*373 -
                   int(mainstat_len), 655), mask=mainstat_mask)

        if mainstat in disper:
            mainstat_value_size = draw.textlength(
                f'{float(mainstat.value)}%', font(49))
            draw.text((375+i*373-mainstat_value_size, 690),
                      f'{float(mainstat.value)}%', font=font(49))
        else:
            mainstat_value_size = draw.textlength(
                format(mainstat.value, ","), font(49))
            draw.text((375+i*373-mainstat_value_size, 690),
                      format(mainstat.value, ","), font=font(49))

        level_len = draw.textlength(f'+{artifact.level}', font(21))
        draw.rounded_rectangle((373+i*373-int(level_len), 748,
                                375+i*373, 771), fill='black', radius=2)
        draw.text((374+i*373-level_len, 749),
                  f'+{artifact.level}', font=font(21))

        substats = artifact.detail.substats
        if artifact.level == 20 and artifact.detail.rarity == 5:
            c_data = {}
            for stat in substats:
                stat_name = prop_id_ja[stat.prop_id]
                if stat_name in disper:
                    c_data[stat_name] = str(float(stat.value))
                else:
                    c_data[stat_name] = str(stat.value)
            psb = calculate_op(c_data)

        if len(substats) == 0:
            continue

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
                f'{cwd}/assets/emotes/{stat_name}.png').resize((30, 30))
            substat_mask = substat_icon.copy()
            base.paste(substat_icon, (44+373*i, 811+50*a), mask=substat_mask)
            if stat_name in disper:
                substat_size = draw.textlength(
                    f'{float(stat.value)}%', font(25))
                draw.text((375+i*373-substat_size, 811+50*a),
                          f'{float(stat.value)}%', font=font(25))
            else:
                substat_size = draw.textlength(
                    format(stat.value, ","), font(25))
                if stat_name in ['防御力', '攻撃力', 'HP']:
                    draw.text(
                        (375+i*373-substat_size, 811+50*a),
                        format(stat.value, ","),
                        font=font(25),
                        fill=(255, 255, 255, 190)
                    )
                else:
                    draw.text(
                        (375+i*373-substat_size, 811+50*a),
                        format(stat.value, ","),
                        font=font(25),
                        fill=(255, 255, 255)
                    )

            if artifact.level == 20 and artifact.detail.rarity == 5:
                nobi = draw.textlength(
                    "+".join(map(str, psb[a])), font=font(11))
                draw.text(
                    (375+i*373-nobi, 840+50*a),
                    "+".join(map(str, psb[a])),
                    fill=(255, 255, 255, 160),
                    font=font(11)
                )

        artifact_score = float(score[parts])
        score_len = draw.textlength(str(artifact_score), font(36))
        draw.text((380+i*373-score_len, 1016),
                  str(artifact_score), font=font(36))
        draw.text((295+i*373-score_len, 1025), 'Score',
                  font=font(27), fill=(160, 160, 160))

        if artifact_score >= point_refer[parts]['SS']:
            grade_image = Image.open(f'{cwd}/assets/grade/SS.png')
        elif artifact_score >= point_refer[parts]['S']:
            grade_image = Image.open(f'{cwd}/assets/grade/S.png')
        elif artifact_score >= point_refer[parts]['A']:
            grade_image = Image.open(f'{cwd}/assets/grade/A.png')
        else:
            grade_image = Image.open(f'{cwd}/assets/grade/B.png')

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


ja = {
    'Anemo': '風',
    'Cryo': '氷',
    'Dendro': '草',
    'Electro': '雷',
    'Geo': '岩',
    'Hydro': '水',
    'Pyro': '炎'
}


class Generator:
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
            bonus = f'{ja[self.element]}元素ダメージ'
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

    def calc_score(self, calc_type):
        result = {
            'TOTAL': 0,
            'EQUIP_BRACER': 0,
            'EQUIP_NECKLACE': 0,
            'EQUIP_SHOES': 0,
            'EQUIP_RING': 0,
            'EQUIP_DRESS': 0
        }
        for artifact_type, artifact in self.artifacts.items():
            v = {
                'FIGHT_PROP_CRITICAL': 0,
                'FIGHT_PROP_CRITICAL_HURT': 0,
                'FIGHT_PROP_ATTACK_PERCENT': 0,
                'FIGHT_PROP_HP_PERCENT': 0,
                # 'FIGHT_PROP_DEFENSE_PERCENT': 0,
                # 'FIGHT_PROP_CHARGE_EFFICIENCY': 0
            }
            for stat in artifact.detail.substats:
                v[stat.prop_id] = stat.value
            if calc_type == 'CRIT_ONLY':
                score = v['FIGHT_PROP_CRITICAL'] * \
                    2 + v['FIGHT_PROP_CRITICAL_HURT']
            elif calc_type == 'RATED_ATK':
                score = v['FIGHT_PROP_CRITICAL'] * \
                    2 + v['FIGHT_PROP_CRITICAL_HURT'] + \
                    v['FIGHT_PROP_ATTACK_PERCENT']
            elif calc_type == 'RATED_HP':
                score = v['FIGHT_PROP_CRITICAL'] * \
                    2 + v['FIGHT_PROP_CRITICAL_HURT'] + \
                    v['FIGHT_PROP_HP_PERCENT']
            result[artifact_type] = score
            result['TOTAL'] += score
        return result


if __name__ == '__main__':
    from enkanetwork import EnkaNetworkAPI
    import asyncio

    async def test():
        client = EnkaNetworkAPI(lang='jp')
        async with client:
            data = await client.fetch_user(618285856)
            score = Generator(data.characters[0]).calc_score('CRIT_ONLY')
            print(score)
            # img.show()

    asyncio.run(test())
