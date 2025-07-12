import subprocess
import os

def run_cmd(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR] {e.cmd}\n{e.stderr.strip()}"

def check_git_setup():
    cwd = os.getcwd()
    print(f"📁 Checking repo in: {cwd}\n")

    print("🔍 Git Status:")
    print(run_cmd(["git", "status", "-sb"]))

    print("\n🌿 Current Branch:")
    print(run_cmd(["git", "branch", "--show-current"]))

    print("\n🔗 Git Remotes:")
    print(run_cmd(["git", "remote", "-v"]))

    print("\n📤 Local HEAD SHA:")
    print(run_cmd(["git", "rev-parse", "HEAD"]))

    print("\n📥 Remote HEAD SHA (origin):")
    print(run_cmd(["git", "ls-remote", "origin", "HEAD"]))

    print("\n📜 Recent Commits (local):")
    print(run_cmd(["git", "log", "--oneline", "-n", "5"]))

    print("\n🌐 Recent Commits (remote origin):")
    print(run_cmd(["git", "fetch", "origin"]))
    print(run_cmd(["git", "log", "origin/HEAD", "--oneline", "-n", "5"]))

    print("\n📁 Tracked/Untracked Files:")
    print(run_cmd(["git", "ls-files"]))
    print("\n❓ Untracked Files:")
    print(run_cmd(["git", "ls-files", "--others", "--exclude-standard"]))

    print("\n📦 Stash List:")
    print(run_cmd(["git", "stash", "list"]))

    print("\n⚠️ Merge Conflicts (if any):")
    print(run_cmd(["git", "diff", "--name-only", "--diff-filter=U"]))

    print("\n✅ Push default:")
    print(run_cmd(["git", "config", "--get", "push.default"]))

    print("\n🚀 Origin Push URL:")
    print(run_cmd(["git", "remote", "get-url", "--push", "origin"]))

if __name__ == "__main__":
    check_git_setup()
