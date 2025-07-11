from pathlib import Path

# --- Config ---
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_FILE = SCRIPT_DIR / "Minerals (and flora) list .txt"
MINERAL_OUT = SCRIPT_DIR / "minerals_raw.txt"
FLORA_OUT = SCRIPT_DIR / "flora_raw.txt"
# --------------

def split_by_known_lines():
    lines = INPUT_FILE.read_text(encoding="utf-8").splitlines()

    # Split based on confirmed positions
    mineral_section = lines[1:1112]
    flora_section = lines[1113:]

    MINERAL_OUT.write_text("\n".join(mineral_section), encoding="utf-8")
    FLORA_OUT.write_text("\n".join(flora_section), encoding="utf-8")

    print(f"✅ Minerals: {len(mineral_section)} lines → {MINERAL_OUT.name}")
    print(f"✅ Flora: {len(flora_section)} lines → {FLORA_OUT.name}")

if __name__ == "__main__":
    split_by_known_lines()
