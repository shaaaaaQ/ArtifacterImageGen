ELEMENT_NAMES = {
    "Anemo": "風",
    "Cryo": "氷",
    "Dendro": "草",
    "Electro": "雷",
    "Geo": "岩",
    "Hydro": "水",
    "Pyro": "炎",
}

PROP_NAMES = {
    "FIGHT_PROP_BASE_ATTACK": "基礎攻撃力",
    "FIGHT_PROP_HP": "HP",
    "FIGHT_PROP_ATTACK": "攻撃力",
    "FIGHT_PROP_DEFENSE": "防御力",
    "FIGHT_PROP_HP_PERCENT": "HPパーセンテージ",
    "FIGHT_PROP_ATTACK_PERCENT": "攻撃パーセンテージ",
    "FIGHT_PROP_DEFENSE_PERCENT": "防御パーセンテージ",
    "FIGHT_PROP_CRITICAL": "会心率",
    "FIGHT_PROP_CRITICAL_HURT": "会心ダメージ",
    "FIGHT_PROP_CHARGE_EFFICIENCY": "元素チャージ効率",
    "FIGHT_PROP_HEAL_ADD": "与える治療効果",
    "FIGHT_PROP_ELEMENT_MASTERY": "元素熟知",
    "FIGHT_PROP_PHYSICAL_ADD_HURT": "物理ダメージ",
    "FIGHT_PROP_FIRE_ADD_HURT": "炎元素ダメージ",
    "FIGHT_PROP_ELEC_ADD_HURT": "雷元素ダメージ",
    "FIGHT_PROP_WATER_ADD_HURT": "水元素ダメージ",
    "FIGHT_PROP_WIND_ADD_HURT": "風元素ダメージ",
    "FIGHT_PROP_ICE_ADD_HURT": "氷元素ダメージ",
    "FIGHT_PROP_ROCK_ADD_HURT": "岩元素ダメージ",
    "FIGHT_PROP_GRASS_ADD_HURT": "草元素ダメージ",
}

# Enka API's numeric FightProp IDs, used by store/gi/affixes.json.
FIGHT_PROP_NAMES_BY_ID = {
    2: "FIGHT_PROP_HP",
    3: "FIGHT_PROP_HP_PERCENT",
    5: "FIGHT_PROP_ATTACK",
    6: "FIGHT_PROP_ATTACK_PERCENT",
    8: "FIGHT_PROP_DEFENSE",
    9: "FIGHT_PROP_DEFENSE_PERCENT",
    20: "FIGHT_PROP_CRITICAL",
    22: "FIGHT_PROP_CRITICAL_HURT",
    23: "FIGHT_PROP_CHARGE_EFFICIENCY",
    28: "FIGHT_PROP_ELEMENT_MASTERY",
}

PERCENTAGE_NAMES = {
    "会心率",
    "会心ダメージ",
    "攻撃パーセンテージ",
    "防御パーセンテージ",
    "HPパーセンテージ",
    "水元素ダメージ",
    "物理ダメージ",
    "風元素ダメージ",
    "岩元素ダメージ",
    "炎元素ダメージ",
    "与える治療効果",
    "雷元素ダメージ",
    "氷元素ダメージ",
    "草元素ダメージ",
    "元素チャージ効率",
}

STAT_ORDER = (
    "HP",
    "攻撃力",
    "防御力",
    "元素熟知",
    "会心率",
    "会心ダメージ",
    "元素チャージ効率",
)

SHORT_NAMES = {
    "攻撃パーセンテージ": "攻撃%",
    "防御パーセンテージ": "防御%",
    "元素チャージ効率": "元チャ効率",
    "HPパーセンテージ": "HP%",
}

ARTIFACT_SLOTS = (
    "EQUIP_BRACER",
    "EQUIP_NECKLACE",
    "EQUIP_SHOES",
    "EQUIP_RING",
    "EQUIP_DRESS",
)

DEFAULT_GRADE_THRESHOLDS = {
    "Total": {"SS": 220, "S": 200, "A": 180},
    "EQUIP_BRACER": {"SS": 50, "S": 45, "A": 40},
    "EQUIP_NECKLACE": {"SS": 50, "S": 45, "A": 40},
    "EQUIP_SHOES": {"SS": 45, "S": 40, "A": 35},
    "EQUIP_RING": {"SS": 45, "S": 40, "A": 37},
    "EQUIP_DRESS": {"SS": 40, "S": 35, "A": 30},
}
