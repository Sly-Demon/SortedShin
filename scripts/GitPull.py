import subprocess
from pathlib import Path

def find_git_root(start_path: Path) -> Path | None:
    current = start_path.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return None

REPO_DIR = find_git_root(Path(__file__))

def pull_from_github():
    if not REPO_DIR:
        print("❌ Could not find a Git repo in parent directories.")
        return

    try:
        print(f"📁 Repo directory: {REPO_DIR}")
        subprocess.run(["git", "pull", "origin", "main"], cwd=REPO_DIR, check=True)
        print("✅ Pull successful.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git pull failed: {e}")

if __name__ == "__main__":
    pull_from_github()
