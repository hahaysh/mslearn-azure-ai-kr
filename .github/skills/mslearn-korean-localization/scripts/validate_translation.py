#!/usr/bin/env python3
"""Validate a Korean translation of MicrosoftLearning-style lab Markdown."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


FENCE_START = re.compile(r"^\s*(`{3,})([\w+-]*)\s*$")
HEADING = re.compile(r"^(#+)\s+", re.MULTILINE)
IMAGE = re.compile(r"!\[[^\]]*]\(([^)]+)\)")
LINK = re.compile(r"(?<!!)\[[^\]]+]\(([^)]+)\)")
INLINE_CODE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
KOREAN = re.compile(r"[가-힣]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Korean Microsoft Learn lab translations."
    )
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument(
        "--source", default="Instructions", help="English instruction root"
    )
    parser.add_argument(
        "--target", default="Instructions-kr", help="Korean instruction root"
    )
    parser.add_argument(
        "--readme",
        help="Translation README path; defaults to <target>/README.md",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fenced_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        match = FENCE_START.match(lines[index])
        if not match:
            index += 1
            continue

        ticks, language = match.groups()
        index += 1
        body: list[str] = []
        closing = re.compile(r"^\s*" + re.escape(ticks) + r"\s*$")
        while index < len(lines) and not closing.match(lines[index]):
            body.append(lines[index])
            index += 1
        if index == len(lines):
            raise ValueError("unclosed fenced code block")
        normalized_body = "\n".join(line.rstrip() for line in body).rstrip()
        blocks.append((language, normalized_body))
        index += 1
    return blocks


def outside_fences(text: str) -> str:
    output: list[str] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        match = FENCE_START.match(lines[index])
        if not match:
            output.append(lines[index])
            index += 1
            continue

        ticks = match.group(1)
        closing = re.compile(r"^\s*" + re.escape(ticks) + r"\s*$")
        index += 1
        while index < len(lines) and not closing.match(lines[index]):
            index += 1
        index += 1
    return "\n".join(output)


def is_subsequence(source: list[object], target: list[object]) -> bool:
    position = 0
    for item in source:
        try:
            position = target.index(item, position) + 1
        except ValueError:
            return False
    return True


def ordered_markers(text: str) -> list[tuple[int, str]]:
    markers: list[tuple[int, str]] = []
    for line in outside_fences(text).splitlines():
        match = re.match(r"^(\s*)(\d+)\.\s", line)
        if match:
            markers.append((len(match.group(1)), match.group(2)))
    return markers


def local_targets(text: str) -> list[str]:
    targets = IMAGE.findall(text) + LINK.findall(text)
    return [
        target
        for target in targets
        if not re.match(r"^(?:https?|mailto):", target)
        and not target.startswith("/")
        and not target.startswith("{{")
    ]


def resolve_local(source_file: Path, target: str) -> Path:
    clean = unquote(target.split("#", 1)[0])
    return (source_file.parent / Path(clean)).resolve()


def is_localized_relative_path(path: Path) -> bool:
    return any(part.lower().endswith("-kr") for part in path.parts)


def markdown_files(root: Path, *, source: bool) -> dict[Path, Path]:
    files: dict[Path, Path] = {}
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if source and is_localized_relative_path(relative):
            continue
        if relative == Path("README.md"):
            continue
        files[relative] = path
    return files


def validate(
    repo: Path, source_dir: Path, target_dir: Path, readme: Path
) -> list[str]:
    errors: list[str] = []

    if not source_dir.is_dir():
        return [f"Source directory does not exist: {source_dir}"]
    if not target_dir.is_dir():
        return [f"Target directory does not exist: {target_dir}"]

    source_files = markdown_files(source_dir, source=True)
    target_files = markdown_files(target_dir, source=False)
    source_paths = sorted(source_files)
    target_paths = sorted(target_files)
    if source_paths != target_paths:
        errors.append(
            "Markdown relative paths differ. "
            f"Source={[str(path) for path in source_paths]!r}; "
            f"target={[str(path) for path in target_paths]!r}"
        )

    if not readme.is_file():
        errors.append(f"Missing translation README: {readme}")
    elif read_text(readme).startswith("---"):
        errors.append("Translation README must not have YAML front matter")

    for relative_path, source_file in sorted(source_files.items()):
        target_file = target_dir / relative_path
        if not target_file.is_file():
            continue

        source = read_text(source_file)
        target = read_text(target_file)
        label = relative_path.as_posix()

        if not source.startswith("---") or not target.startswith("---"):
            errors.append(f"{label}: missing YAML front matter")
        if not KOREAN.search(target):
            errors.append(f"{label}: no Korean text found")
        if HEADING.findall(source) != HEADING.findall(target):
            errors.append(f"{label}: heading-level sequence differs")
        if ordered_markers(source) != ordered_markers(target):
            errors.append(f"{label}: ordered-step structure differs")
        if IMAGE.findall(source) != IMAGE.findall(target):
            errors.append(f"{label}: image targets differ")
        if LINK.findall(source) != LINK.findall(target):
            errors.append(f"{label}: link targets differ")
        if source.count("> [!NOTE]") != target.count("> [!NOTE]"):
            errors.append(f"{label}: NOTE callout count differs")
        if source.count("> [!IMPORTANT]") != target.count("> [!IMPORTANT]"):
            errors.append(f"{label}: IMPORTANT callout count differs")

        try:
            source_blocks = fenced_blocks(source)
            target_blocks = fenced_blocks(target)
        except ValueError as error:
            errors.append(f"{label}: {error}")
            continue

        if not is_subsequence(source_blocks, target_blocks):
            errors.append(f"{label}: an original fenced block changed or moved")

        source_inline = INLINE_CODE.findall(outside_fences(source))
        target_inline = INLINE_CODE.findall(outside_fences(target))
        if not is_subsequence(source_inline, target_inline):
            errors.append(f"{label}: an original inline-code value changed or moved")

        korean_prompts = [
            body
            for language, body in target_blocks
            if language == "prompt" and KOREAN.search(body)
        ]
        for prompt in korean_prompts:
            if "**" in prompt or "`" in prompt:
                errors.append(
                    f"{label}: Korean prompt contains Markdown decoration"
                )

        if "한국어 의미" in target:
            errors.append(f"{label}: obsolete Korean-meaning label remains")

        source_local_targets = local_targets(source)
        target_local_targets = local_targets(target)
        for source_target, target_value in zip(
            source_local_targets, target_local_targets
        ):
            source_asset = resolve_local(source_file, source_target)
            target_asset = resolve_local(target_file, target_value)
            if not target_asset.exists():
                errors.append(f"{label}: broken local target: {target_value}")
                continue

            try:
                source_asset_relative = source_asset.relative_to(source_dir)
            except ValueError:
                continue

            mirrored_asset = target_dir / source_asset_relative
            if source_asset.exists() and not mirrored_asset.exists():
                errors.append(
                    f"{label}: missing mirrored asset: "
                    f"{source_asset_relative.as_posix()}"
                )

    return errors


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    source_dir = (repo / Path(args.source)).resolve()
    target_dir = (repo / Path(args.target)).resolve()
    readme = (
        (repo / Path(args.readme)).resolve()
        if args.readme
        else target_dir / "README.md"
    )

    errors = validate(repo, source_dir, target_dir, readme)
    if errors:
        print("Translation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    count = len(markdown_files(source_dir, source=True))
    print(f"Translation validation passed for {count} Markdown file(s).")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print(f"README: {readme}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
