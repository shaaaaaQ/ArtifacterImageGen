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

```console
python -m artifacter_image_gen 618285856 0
```

インストール後は次のコマンドでも同じように実行できます。

```console
artifacter-image-gen 618285856 0
```

表示と同時にPNGを保存する場合:

```console
python -m artifacter_image_gen 618285856 0 --output build.png
```

## キャッシュ

ダウンロードした画像と聖遺物のロール情報は、インストール済みパッケージ内ではなく、
OS のユーザーキャッシュ領域へ保存します。

- Windows: `%LOCALAPPDATA%/artifacter-image-gen`
- macOS: `~/Library/Caches/artifacter-image-gen`
- Linux: `$XDG_CACHE_HOME/artifacter-image-gen`（未設定なら `~/.cache/...`）

保存先は環境変数 `ARTIFACTER_IMAGE_GEN_CACHE_DIR`、またはコードから変更できます。

```python
from artifacter_image_gen import AssetCache, Generator

generator = Generator(character, cache=AssetCache("/path/to/cache"))
```

この分離により、仮想環境を作り直してもキャッシュを再利用でき、読み取り専用環境へ
インストールした場合にも動作します。複数プロセスで共有する場合は、ユーザー単位の
同じディレクトリを指定してください。

なお enka.py 本体のゲームアセットは、現行の v2.5 系では作業ディレクトリの
`.enka_py/assets` に保存されます。アプリケーション側の作業ディレクトリを固定し、
`.enka_py` は Git 管理から外してください。
