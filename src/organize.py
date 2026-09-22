"""Move flat `<leader>*.txt` files from the project root into `data/original/<leader>/`.

Usage:
    python -m src.organize --dry-run     # show what would move
    python -m src.organize               # move

Safety rules:
  * files are moved, never copied-then-edited, never overwritten (an existing target aborts that file);
  * by default the run aborts if any candidate is 0 bytes — an editor holding an unsaved buffer would
    write the text back to the OLD path after the move. Save everything first, or pass --allow-empty.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from .config import PROJECT_ROOT, leader_slugs, load_config, path_for


def plan_moves(source: Path, target_root: Path, leaders: list[str]) -> tuple[list[tuple[Path, Path]], list[Path]]:
    moves, unmatched = [], []
    for p in sorted(source.glob("*.txt")):
        m = re.match(r"^([A-Za-z]+)", p.stem)
        leader = m.group(1).lower() if m else ""
        if leader in leaders:
            moves.append((p, target_root / leader / p.name))
        else:
            unmatched.append(p)
    return moves, unmatched


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Move root-level speech files into data/original/<leader>/.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--source", default=str(PROJECT_ROOT))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-empty", action="store_true", help="move 0-byte files too (normally a sign of unsaved editor buffers)")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    source = Path(args.source).resolve()
    target_root = path_for(cfg, "data_original")
    moves, unmatched = plan_moves(source, target_root, leader_slugs(cfg))

    if not moves:
        print(f"[organize] no <leader>*.txt files found in {source}")
        return 0

    empties = [src for src, _ in moves if src.stat().st_size == 0]
    if empties and not args.allow_empty:
        print(f"[organize] ABORT: {len(empties)} file(s) are 0 bytes — save them in your editor first (or pass --allow-empty):")
        for e in empties:
            print(f"    {e.name}")
        return 2

    rc = 0
    for src, dst in moves:
        if dst.exists():
            print(f"[organize] SKIP (target exists): {src.name} -> {dst.relative_to(PROJECT_ROOT)}")
            rc = 1
            continue
        print(f"[organize] {'would move' if args.dry_run else 'move'}: {src.name} -> {dst.relative_to(PROJECT_ROOT)}  ({src.stat().st_size} bytes)")
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
    for u in unmatched:
        print(f"[organize] left in place (no leader prefix): {u.name}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
