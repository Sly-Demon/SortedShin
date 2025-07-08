import subprocess

commit_msg = input("📝 Commit message: ").strip()

if not commit_msg:
    print("❌ No commit message given. Aborting.")
else:
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", commit_msg],
        ["git", "push"]
    ]

    for cmd in commands:
        print(f"▶️ Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"❌ Command failed: {' '.join(cmd)}")
            break
    else:
        print("✅ All done!")
