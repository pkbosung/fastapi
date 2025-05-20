# services/filter_utils.py

# 유사 기호 그룹
conflict_groups = [
    ["iron_low", "iron_medium", "iron_high"],
    ["tumble_dry_low", "tumble_dry_medium", "tumble_dry"],
]

# 위험도 우선순위
conflict_priority = {
    "iron_low": 1, "iron_medium": 2, "iron_high": 3,
    "tumble_dry_low": 1, "tumble_dry_medium": 2, "tumble_dry": 3
}


def remove_duplicate_labels(detected: list[tuple[str, float]]) -> list[tuple[str, float]]:
    unique = {}
    for label, confidence in detected:
        if label not in unique or confidence > unique[label][1]:
            unique[label] = (label, confidence)
    return list(unique.values())


def resolve_conflict_groups(detected: list[tuple[str, float]]) -> list[tuple[str, float]]:
    label_map = {label: (label, conf) for label, conf in detected}
    labels = set(label_map.keys())
    final_labels = set(labels)

    for group in conflict_groups:
        overlapping = list(set(group) & labels)
        if len(overlapping) > 1:
            best = max(overlapping, key=lambda l: conflict_priority.get(l, 0))
            for label in overlapping:
                if label != best:
                    final_labels.discard(label)

    return [label_map[label] for label in final_labels]


def filter_detections(detected: list[tuple[str, float]]) -> list[tuple[str, float]]:
    step1 = remove_duplicate_labels(detected)
    return resolve_conflict_groups(step1)
