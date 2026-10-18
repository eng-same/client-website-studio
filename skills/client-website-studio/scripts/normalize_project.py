#!/usr/bin/env python3
"""Safely fix an existing client project. Standard library only.

  normalize_project.py PROJECT            show what would change (changes nothing)
  normalize_project.py PROJECT --apply    do it, after making a full backup next to the project

Fixes two known problems:
  1. The website sits in a wrapper folder (site/, www/, dist/ ...) instead of the project root:
     its contents are moved up so index.html sits directly in the project folder.
  2. The skill kit was copied into the project (.studio-kit/, .claude/skills/client-website-studio, ...):
     those copies are removed. The skill belongs in the user-level skills folder, never in a project.

Never overwrites an existing file, never touches client/, brand/ or any other project file, and stops
without changing anything when it cannot be sure what to do.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from audit_site import audit, find_nested_site, find_skill_contamination, format_report, utf8_stdout  # noqa: E402

AGENT_DIRS = {'.claude', '.agents', '.codex'}


def plan(root: Path) -> tuple[list[tuple[str, Path]], list[str]]:
    """Return (actions, blockers). An action is ('remove', path) or ('move-up', wrapper_dir)."""
    actions: list[tuple[str, Path]] = []
    blockers: list[str] = []
    for item in find_skill_contamination(root):
        path = root / item.rstrip('/')
        name = path.name
        if name == 'skills' and path.parent.name in AGENT_DIRS:
            skill = path / 'client-website-studio'
            if skill.is_dir():
                actions.append(('remove', skill))
            else:
                blockers.append(f'{item} holds skills of its own; check it by hand')
        elif path.is_dir():
            actions.append(('remove', path))
        else:
            blockers.append(f'{item} looks like a skill file; check it by hand and remove it if it is not yours')
    nested = find_nested_site(root)
    if len(nested) > 1:
        blockers.append(f'More than one wrapper folder found ({", ".join(nested)}); a person must choose')
    elif nested:
        wrapper = root / nested[0]
        if (root / 'index.html').is_file():
            blockers.append(f'Both the project root and {nested[0]}/ contain an index.html; '
                            'a person must decide which copy is the current one')
        else:
            clashes = [c.name for c in wrapper.iterdir() if (root / c.name).exists()]
            if clashes:
                blockers.append(f'Cannot move {nested[0]}/ up: these names already exist in the project: '
                                f'{", ".join(sorted(clashes))}')
            else:
                actions.append(('move-up', wrapper))
    return actions, blockers


def force_remove(path: Path) -> None:
    def on_error(func, target, _exc):  # read-only files inside .git on Windows
        os.chmod(target, stat.S_IWRITE)
        func(target)
    shutil.rmtree(path, onerror=on_error)


def prune_empty(path: Path, stop: Path) -> None:
    while path != stop and path.is_dir() and not any(path.iterdir()):
        path.rmdir()
        path = path.parent


def main() -> None:
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project', type=Path)
    parser.add_argument('--apply', action='store_true', help='make the changes (a backup is made first)')
    args = parser.parse_args()
    root = args.project.resolve()
    if not root.is_dir():
        parser.error(f'project folder not found: {root}')

    actions, blockers = plan(root)
    if not actions and not blockers:
        print('Nothing to fix: the website is in the project root and no skill files are inside the project.')
        return
    for kind, path in actions:
        rel = path.relative_to(root).as_posix()
        print(f'  will {"remove the skill copy" if kind == "remove" else "move the website up out of"}: {rel}/')
    for item in blockers:
        print(f'  needs a person: {item}')
    if blockers:
        raise SystemExit('Nothing was changed. Resolve the points above first.')
    if not args.apply:
        print('Dry run only. Run again with --apply to make these changes (a backup is made first).')
        return

    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = root.parent / f'{root.name}-backup-{stamp}'
    shutil.copytree(root, backup)
    print(f'Backup made outside the project: {backup}')

    for kind, path in actions:
        if kind == 'remove':
            parent = path.parent
            force_remove(path)
            prune_empty(parent, root)
        else:
            for child in sorted(path.iterdir()):
                shutil.move(str(child), str(root / child.name))
            path.rmdir()
    print('Done. Checking the result:')
    result = audit(root, 'preview')
    print(format_report(result))
    raise SystemExit(1 if result['errors'] else 0)


if __name__ == '__main__':
    main()
