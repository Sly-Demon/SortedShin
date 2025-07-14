import subprocess
import os

# Go to repo root (one level up from this script)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("..")

commit_msg = input("📝 Commit message: ").strip()

if not commit_msg:
    print("❌ No commit message given. Aborting.")
else:
    commands = [
        ["git", "add", "--all"],  # Tracks deletions + additions
        ["git", "commit", "-m", commit_msg],
        ["git", "push", "force"]
    ]

    for cmd in commands:
        print(f"▶️ Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"❌ Command failed: {' '.join(cmd)}")
            break
    else:
        print("✅ All done!")
