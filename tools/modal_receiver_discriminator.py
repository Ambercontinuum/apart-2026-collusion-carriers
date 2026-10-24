"""Modal entry point for the X-1 receiver discriminator; all logic is in receiver_discriminator.py."""

import json
from pathlib import Path
import sys

from modal_shakedown import Server, app


@app.local_entrypoint()
def discriminator():
    root = Path(__file__).resolve().parents[1]
    sys.path.append(str(root / ".venv/Lib/site-packages"))
    sys.path.insert(0, str(root / "tools"))
    from receiver_discriminator import run

    server = Server()
    result = run(server.request.remote,
                 root / "evidence/calibration/receiver-discriminator-20261024",
                 close=server.close.remote)
    print(json.dumps({key: result.get(key) for key in (
        "complete", "failure", "requests_attempted", "sender_pass", "classification", "overall_pass")}))
