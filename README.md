# ArtifacterImageGen

[FuroBath/ArtifacterImageGen](https://github.com/FuroBath/ArtifacterImageGen) を基にした、
[enka.py](https://github.com/seriaati/enka-py) 用の原神ビルドカード生成ライブラリです。

## インストール

Python 3.10 以上が必要です。

```console
pip install .
```

## 使い方

enka.py v2 の `GenshinClient` から得た `Character` を `Generator` に渡します。

```python
import asyncio

import enka
from artifacter_image_gen import Generator


async def main() -> None:
    rates = {
        "FIGHT_PROP_CRITICAL": 2,
        "FIGHT_PROP_CRITICAL_HURT": 1,
        "FIGHT_PROP_ATTACK_PERCENT": 1,
    }

    async with enka.GenshinClient(enka.gi.Language.JAPANESE) as client:
        showcase = await client.fetch_showcase(UID)

    image = Generator(showcase.characters[0]).generate(rates, label="攻撃%")
    image.save("build.png")


asyncio.run(main())
```

### UIDを指定した実動作テスト

UIDと、プロフィールに表示しているキャラクターのindex（0始まり）を指定すると、
実際にEnkaから取得して生成画像を既定の画像ビューアーで表示できます。

```sh
python -m artifacter_image_gen 618285856 0
```

インストール後は次のコマンドでも同じように実行できます。

```sh
artifacter-image-gen 618285856 0
```

表示と同時にPNGを保存する場合:

```sh
python -m artifacter_image_gen 618285856 0 --output build.png
```

## キャッシュ

ダウンロードした画像と聖遺物のロール情報は、OS のユーザーキャッシュ領域へ保存します。

- Windows: `%LOCALAPPDATA%/artifacter-image-gen`
- macOS: `~/Library/Caches/artifacter-image-gen`
- Linux: `$XDG_CACHE_HOME/artifacter-image-gen`（未設定なら `~/.cache/...`）

保存先は環境変数 `ARTIFACTER_IMAGE_GEN_CACHE_DIR` から変更できます。

```python
from artifacter_image_gen import AssetCache, Generator

generator = Generator(character, cache=AssetCache("/path/to/cache"))
```

enka-py 本体のゲームアセットは、作業ディレクトリの`.enka_py/assets` に保存されます

## ライセンス

本リポジトリのコードは、特記のない限り[MIT License](LICENSE)で提供されます。

下記ライブラリはGPL-3.0で提供されており、結合したプログラム全体の配布にはGPL-3.0が適用されます。([COPYING.GPLv3](COPYING.GPLv3))
- [enka-py](https://github.com/seriaati/enka-py)

使用フォント：NotoSansJP ([font.ttf](artifacter_image_gen/assets/font.ttf)) / [SIL Open Font License 1.1](artifacter_image_gen/assets/NotoSansJP-LICENSE.txt)

## 免責事項

本プロジェクトは非公式のファンプロジェクトです。HoYoverseおよびCOGNOSPHEREとの提携、承認、後援その他の関係はありません。

「原神」および関連する名称、画像、その他の素材に関する権利は、それぞれの権利者に帰属します。

本リポジトリに含まれる第三者に帰属する名称、画像、その他の素材には、本リポジトリのソフトウェアライセンスは適用されません。

