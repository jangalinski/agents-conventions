#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys

import yaml


def run(cmd: list[str], *, check: bool = True, capture_output: bool = False, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=capture_output, text=text)


def create_pull_request(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return
    stderr = (result.stderr or "").strip()
    if "createPullRequest" in stderr or "not permitted to create or approve pull requests" in stderr:
        message = (
            "pull request creation was rejected by GitHub Actions permissions.\n"
            "Enable 'Allow GitHub Actions to create and approve pull requests' for the repository or its organization,\n"
            "or use a token with PR creation rights."
        )
        if stderr:
            message = f"{message}\n\nOriginal error:\n{stderr}"
        raise SystemExit(message)
    raise subprocess.CalledProcessError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)


def get_open_pull_request_number(repo: str, head_branch: str) -> int | None:
    result = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            repo,
            "--head",
            head_branch,
            "--state",
            "open",
            "--json",
            "number",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=result.stderr)
    prs = json.loads(result.stdout or "[]")
    if not prs:
        return None
    return int(prs[0]["number"])


def parse_frontmatter(path: pathlib.Path) -> dict:
    # We only care about the YAML frontmatter block at the top of each convention file.
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        return {}
    frontmatter_text = parts[0][4:]
    data = yaml.safe_load(frontmatter_text) or {}
    return data if isinstance(data, dict) else {}


source_repo = os.environ["SOURCE_REPOSITORY"]
source_ref = os.environ["SOURCE_REF"]
repository = os.environ["REPOSITORY"]
config_path = os.environ["CONFIG_PATH"]
destination_dir = os.environ["DESTINATION_DIR"]
branch_name = os.environ["BRANCH_NAME"]
commit_message = os.environ["COMMIT_MESSAGE"]
pr_title = os.environ["PR_TITLE"]
source_dir = pathlib.Path(os.environ["SOURCE_DIR"])
workspace = pathlib.Path(os.environ.get("GITHUB_WORKSPACE", os.getcwd()))

config_candidates = [
    workspace / config_path,
    workspace / config_path.replace(".yml", ".yaml"),
    workspace / config_path.replace(".yaml", ".yml"),
]

config_file = next((path for path in config_candidates if path.is_file()), None)
if config_file is None:
    print(f"No shared config file found at {config_candidates[0]}. Skipping import.")
    raise SystemExit(0)

shared_config = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
selected_ids = [str(item).strip() for item in shared_config.get("ids", []) if str(item).strip()]
selected_tags = [str(item).strip() for item in shared_config.get("tags", []) if str(item).strip()]
if not selected_ids and not selected_tags:
    raise SystemExit(f"no ids or tags configured in {config_file}")

source_conventions_dir = source_dir / ".agents" / "conventions"
if not source_conventions_dir.is_dir():
    raise SystemExit(f"source conventions directory not found: {source_conventions_dir}")

source_by_id: dict[str, pathlib.Path] = {}
source_by_tag: dict[str, list[pathlib.Path]] = {}
# Build an index so we can resolve ids to source files quickly and detect duplicates early.
for path in sorted(source_conventions_dir.rglob("*.md")):
    frontmatter = parse_frontmatter(path)
    convention_id = str(frontmatter.get("id", "")).strip()
    if not convention_id:
        continue
    if convention_id in source_by_id:
        raise SystemExit(
            f"duplicate convention id {convention_id} in {source_by_id[convention_id]} and {path}"
        )
    source_by_id[convention_id] = path
    for tag in frontmatter.get("tags", []) or []:
        tag_name = str(tag).strip()
        if not tag_name:
            continue
        source_by_tag.setdefault(tag_name, []).append(path)

unknown_ids = [convention_id for convention_id in selected_ids if convention_id not in source_by_id]
if unknown_ids:
    allowed_ids = ", ".join(sorted(source_by_id))
    raise SystemExit(
        "unknown convention ids in selector file: "
        f"{', '.join(unknown_ids)}\n"
        f"Allowed ids: {allowed_ids}"
    )

unknown_tags = [tag_name for tag_name in selected_tags if tag_name not in source_by_tag]
if unknown_tags:
    allowed_tags = ", ".join(sorted(source_by_tag))
    raise SystemExit(
        "unknown convention tags in selector file: "
        f"{', '.join(unknown_tags)}\n"
        f"Allowed tags: {allowed_tags}"
    )

selected_paths: list[pathlib.Path] = []
selected_ids_seen: set[str] = set()

for convention_id in selected_ids:
    source_path = source_by_id.get(convention_id)
    if source_path is None:
        raise SystemExit(f"convention id not found in source repo: {convention_id}")
    if convention_id not in selected_ids_seen:
        selected_paths.append(source_path)
        selected_ids_seen.add(convention_id)

for tag_name in selected_tags:
    for source_path in source_by_tag[tag_name]:
        frontmatter = parse_frontmatter(source_path)
        convention_id = str(frontmatter.get("id", "")).strip()
        if convention_id and convention_id not in selected_ids_seen:
            selected_paths.append(source_path)
            selected_ids_seen.add(convention_id)

general_path = source_by_id.get("general")
if general_path is None:
    raise SystemExit("required shared convention id not found in source repo: general")
if general_path not in selected_paths:
    selected_paths.insert(0, general_path)

destination_root = workspace / destination_dir
destination_root.mkdir(parents=True, exist_ok=True)
expected_targets: set[pathlib.Path] = set()

# Copy the selected conventions into the consumer repo using the id as the filename.
for source_path in selected_paths:
    frontmatter = parse_frontmatter(source_path)
    convention_id = str(frontmatter.get("id", "")).strip()
    target_path = destination_root / f"{convention_id}.md"
    expected_targets.add(target_path)
    shutil.copy2(source_path, target_path)

# Remove files that are no longer selected so the destination mirrors the current config.
for path in destination_root.glob("*.md"):
    if path not in expected_targets:
        path.unlink()

# If nothing changed, stop early instead of creating an empty branch and PR.
status = run(["git", "-C", str(workspace), "status", "--porcelain", destination_dir], capture_output=True).stdout.strip()
if not status:
    print("No shared convention changes detected. Nothing to commit.")
    raise SystemExit(0)

remote_show = run(["git", "-C", str(workspace), "remote", "show", "origin"], capture_output=True).stdout
base_branch = next((line.split(":", 1)[1].strip() for line in remote_show.splitlines() if line.startswith("  HEAD branch:")), "main") or "main"

# Create or reset the feature branch, stage the imported files, and commit them with a bot identity.
run(["git", "-C", str(workspace), "checkout", "-B", branch_name])
run(["git", "-C", str(workspace), "config", "user.name", "github-actions[bot]"])
run(["git", "-C", str(workspace), "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
run(["git", "-C", str(workspace), "add", destination_dir])
run(["git", "-C", str(workspace), "commit", "-m", commit_message])

gh_token = os.environ["GH_TOKEN"]
# Re-point origin to the consumer repo with token auth so git push works in CI.
run(
    [
        "git",
        "-C",
        str(workspace),
        "remote",
        "set-url",
        "origin",
        f"https://x-access-token:{gh_token}@github.com/{repository}.git",
    ]
)
run(["git", "-C", str(workspace), "push", "-u", "--force", "origin", branch_name])

pr_body = "\n".join(
    [
        f"Import shared conventions from `{source_repo}@{source_ref}`.",
        "",
        f"Config: `{config_file.name}`",
        "Selected ids:",
        *[f"- `{convention_id}`" for convention_id in selected_ids],
        "",
        "Selected tags:",
        *[f"- `{tag_name}`" for tag_name in selected_tags],
        "",
        "Always included:",
        "- `general`",
    ]
)

open_pr_number = get_open_pull_request_number(repository, branch_name)
if open_pr_number is None:
    # Open the pull request back to the consumer's default branch.
    create_pull_request(
        [
            "gh",
            "pr",
            "create",
            "--base",
            base_branch,
            "--head",
            branch_name,
            "--repo",
            repository,
            "--title",
            pr_title,
            "--body",
            pr_body,
        ]
    )
    print(f"Created pull request for {branch_name} against {base_branch}")
else:
    run(
        [
            "gh",
            "pr",
            "edit",
            str(open_pr_number),
            "--repo",
            repository,
            "--title",
            pr_title,
            "--body",
            pr_body,
        ]
    )
    print(f"Updated pull request #{open_pr_number} for {branch_name}")
