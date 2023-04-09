import json
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import requests

cwd = os.path.abspath(os.path.dirname(__file__))


def font(size):
    return ImageFont.truetype(f'{cwd}/assets/ja-jp.ttf', size)


def read_json(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return json.load(f)


def fetch_image(name):
    # TODO 非同期
    filepath = f'{cwd}/cache/{name}.png'
    if not os.path.exists(filepath):
        url = f'https://enka.network/ui/{name}.png'
        print(f'fetch: {url}')
        res = requests.get(url)
        image = res.content
        with open(filepath, mode='wb') as f:
            f.write(image)
    return Image.open(filepath).convert('RGBA')


def generate(character):
    element = character.element.name

    # base
    base = Image.open(f'{cwd}/assets/base/{element}.png')

    # character
    # TODO costume アルハイゼン？
    character_image = fetch_image(character.image.banner.filename)
    character_image = character_image.crop((289, 0, 1728, 1024))
    character_image = character_image.resize(
        (int(character_image.width*0.75), int(character_image.height*0.75)))
    character_mask = character_image.copy()
    character_mask2 = Image.open(
        f'{cwd}/assets/character_mask.png'
    ).convert('L').resize(character_image.size)
    character_image.putalpha(character_mask2)
    character_shadow = Image.open(f'{cwd}/assets/shadow.png').resize(base.size)
    character_paste = Image.new("RGBA", base.size, (255, 255, 255, 0))
    character_paste.paste(
        character_image,
        (-160, -45),
        mask=character_mask
    )
    base = Image.alpha_composite(base, character_paste)
    base = Image.alpha_composite(base, character_shadow)

    return base


async def test():
    client = EnkaNetworkAPI()
    async with client:
        data = await client.fetch_user(618285856)
        img = generate(data.characters[0])
        img.show()


if __name__ == '__main__':
    from enkanetwork import EnkaNetworkAPI
    import asyncio
    uid = 618285856
    asyncio.run(test())
