"""Predeclared event-instance shuffle; preserves counts, not all sender information."""

import hashlib
import json
import random

ALGORITHM = "apart.sender-task.fisher-yates.v1"


def shuffle_block(symbols, *, episode_seed, sender, task_id):
    """Return delivered values and host-only original indices, without rejection sampling.

    The caller supplies a complete four-slot block. Fixed points and identical
    outputs are retained. The random stream is domain-separated from task/model
    randomness and depends on context identifiers, never symbol values/outcomes.
    """
    if len(symbols) != 4:
        raise ValueError("a complete four-slot block is required")
    if type(episode_seed) is not int or not isinstance(sender, str) or not isinstance(task_id, str):
        raise ValueError("invalid shuffle context")
    if any(type(symbol) is not int or symbol not in range(4) for symbol in symbols):
        raise ValueError("symbols must be integers 0..3")
    material = json.dumps(
        [ALGORITHM, episode_seed, sender, task_id], ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    seed_digest = hashlib.sha256(material).hexdigest()
    rng = random.Random(int(seed_digest, 16))
    indices = list(range(4))
    for index in range(3, 0, -1):
        other = rng.randrange(index + 1)
        indices[index], indices[other] = indices[other], indices[index]
    return {
        "algorithm": ALGORITHM,
        "seed_digest": seed_digest,
        "original_indices": indices,
        "received": [symbols[index] for index in indices],
        "fixed_points": sum(index == original for index, original in enumerate(indices)),
    }
