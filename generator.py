import json
import os
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

element_ja = {
    'Anemo': '風',
    'Cryo': '氷',
    'Dendro': '草',
    'Electro': '雷',
    'Geo': '岩',
    'Hydro': '水',
    'Pyro': '炎'
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


def generate(character):
    element = character.element.name
    character_stats = {
        'HP': character.stats.FIGHT_PROP_HP.to_rounded(),
        "攻撃力": character.stats.FIGHT_PROP_ATTACK.to_rounded(),
        "防御力": character.stats.FIGHT_PROP_DEFENSE.to_rounded(),
        "元素熟知": character.stats.FIGHT_PROP_ELEMENT_MASTERY.to_rounded(),
        "会心率": character.stats.FIGHT_PROP_CRITICAL.to_percentage(),
        "会心ダメージ": character.stats.FIGHT_PROP_CRITICAL_HURT.to_percentage(),
        "元素チャージ効率": character.stats.FIGHT_PROP_CHARGE_EFFICIENCY.to_percentage()
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

    # base
    base = Image.open(f'{cwd}/assets/base/{element}.png')

    # character
    # TODO costume アルハイゼン 旅人
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
    weapon = [
        equip
        for equip in character.equipments
        if equip.type == EquipmentsType.WEAPON
    ][0]
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

    # 365

    return base


if __name__ == '__main__':
    from enkanetwork import EnkaNetworkAPI
    import asyncio

    async def test():
        client = EnkaNetworkAPI(lang='jp')
        async with client:
            data = await client.fetch_user(618285856)
            img = generate(data.characters[0])
            img.show()

    asyncio.run(test())
