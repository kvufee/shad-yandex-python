import os
import subprocess

from pathlib import Path


def get_changed_dirs(git_path: Path, from_commit_hash: str, to_commit_hash: str) -> set[Path]:
    """
    Get directories which content was changed between two specified commits
    :param git_path: path to git repo directory
    :param from_commit_hash: hash of commit to do diff from
    :param to_commit_hash: hash of commit to do diff to
    :return: sequence of changed directories between specified commits
    """
    os.chdir(git_path)
    git_command = ["git", "diff", "--name-only", from_commit_hash, to_commit_hash]
    result = subprocess.run(git_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        changed_files = result.stdout.splitlines()
    else:
        raise RuntimeError(f"Git command failed: {result.stderr}")

    changed_dirs = set()

    for file_path in changed_files:
        file_res: Path = Path(str(git_path) + '/' + file_path)
        changed_dirs.add(file_res.parent)
    return changed_dirs
