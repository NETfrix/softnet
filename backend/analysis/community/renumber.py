from __future__ import annotations

from collections import Counter


def renumber_by_size(membership: list[int]) -> list[int]:
    """
    Renumber communities so the largest is 1, second largest is 2, etc.

    Original community IDs are replaced with size-based ranks.
    """
    counts = Counter(membership)
    # Sort by size descending, then by original ID for tie-breaking
    ranked = sorted(counts.keys(), key=lambda c: (-counts[c], c))
    # Map: original_id -> new_id (1-based)
    mapping = {old: new for new, old in enumerate(ranked, 1)}
    return [mapping[m] for m in membership]
