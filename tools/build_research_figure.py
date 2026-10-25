"""Export a descriptive figure from committed run records, no model calls."""

from pathlib import Path
import json
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "apart.receiver-checks.v1"
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
final = json.loads((ROOT / "evidence/experiment2/final-attempt-v1/record.json").read_text())
assert "shutdown" in final
old = json.loads((ROOT / "evidence/experiment2/v1_2/record.json").read_text())
probe = json.loads((ROOT / "evidence/experiment2/xor-diagnostic-v1/record.json").read_text())
context = json.loads((ROOT / "evidence/experiment2/context-diagnostic-v1/record.json").read_text())
rows = [
    ("Original allocation calibration", old["calibration_screen"]["correct"], 8),
    ("Direct XOR text", probe["summary"]["xor_text"]["correct"], 4),
    ("Direct XOR reporting tool", probe["summary"]["xor_tool"]["correct"], 4),
    ("Allocation with supplied answer", probe["summary"]["allocation_oracle"]["correct"], 4),
    ("Full-context input extraction", context["summary"]["extract_bits"]["correct"], 4),
    ("Full-context XOR report", context["summary"]["xor_report"]["correct"], 4),
    ("Final compact calibration", final["calibration_screen"]["correct"], 8),
]
fig, ax = plt.subplots(figsize=(8.0, 3.6), layout="constrained")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
y = list(range(len(rows)))
heights = [x[1] / x[2] for x in rows]
ax.barh(y, heights, color="#276878", height=0.62)
ax.set_yticks(y, [x[0] for x in rows], fontsize=9)
ax.invert_yaxis()
ax.set_xlim(0, 1.14)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"], fontsize=9)
ax.set_xlabel("Correct outcomes / evaluated cases", fontsize=10)
for i, (_, c, n) in enumerate(rows):
    ax.text(c / n + 0.02, i, f"{c}/{n}", va="center", fontsize=9)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", alpha=0.15)
ax.set_axisbelow(True)
fig.suptitle("Receiver checks across separate protocols", fontsize=12, fontweight="bold")
folder = ROOT / "docs/figures"
folder.mkdir(parents=True, exist_ok=True)
fig.savefig(folder / "receiver_checks.png", dpi=220, bbox_inches="tight")
fig.savefig(folder / "receiver_checks.svg", bbox_inches="tight", metadata={"Date": None})
print("Figure exported; different prompts/tasks, descriptive only, no significance claim.")

svg_path = folder / "receiver_checks.svg"
svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8", newline="\n")
