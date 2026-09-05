from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import enka

from .generator import Generator

DEFAULT_RATES = {
    "FIGHT_PROP_CRITICAL": 2,
    "FIGHT_PROP_CRITICAL_HURT": 1,
    "FIGHT_PROP_ATTACK_PERCENT": 1,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch an Enka showcase character and display its build card."
    )
    parser.add_argument("uid", type=int, help="Genshin Impact UID")
    parser.add_argument("index", type=int, help="Zero-based character index")
    parser.add_argument("--label", default="攻撃%", help="Score label shown on the card")
    parser.add_argument("--output", type=Path, help="Also save the generated PNG here")
    return parser.parse_args()


async def generate_from_uid(args: argparse.Namespace) -> None:
    async with enka.GenshinClient(enka.gi.Language.JAPANESE) as client:
        showcase = await client.fetch_showcase(args.uid)

    characters = showcase.characters
    if not 0 <= args.index < len(characters):
        available = ", ".join(
            f"{index}: {character.name}" for index, character in enumerate(characters)
        )
        raise SystemExit(
            f"index {args.index} is out of range (0..{len(characters) - 1}). "
            f"Available characters: {available or 'none'}"
        )

    character = characters[args.index]
    image = Generator(character).generate(DEFAULT_RATES, label=args.label)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        image.save(args.output, format="PNG")
        print(f"Saved: {args.output.resolve()}")
    image.show(title=f"{character.name} ({args.uid})")


def main() -> None:
    asyncio.run(generate_from_uid(parse_args()))


if __name__ == "__main__":
    main()
