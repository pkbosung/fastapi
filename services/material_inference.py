# services/material_inference.py

MATERIAL_LABEL_MAP = {
    "면": {"machine_wash_normal", "iron_medium", "tumble_dry_low"},
    "린넨": {"machine_wash_delicate", "DN_bleach", "tumble_dry_low", "iron_medium"},
    "폴리에스터": {"machine_wash_normal", "DN_bleach", "iron_low"},
    "나일론": {"machine_wash_delicate", "DN_bleach", "tumble_dry_low"},
    "아크릴": {"hand_wash", "DN_bleach", "iron_low"},
    "울": {"DN_wash", "DN_bleach", "DN_tumble_dry", "DN_wet_clean", "dry_flat_shade", "iron_low"},
    "앙고라": {"DN_wash", "DN_bleach", "DN_tumble_dry", "dry_flat_shade", "DN_iron"},
    "모달": {"machine_wash_delicate", "DN_bleach", "tumble_dry_low", "iron_low"},
    "레이온": {"hand_wash", "DN_bleach", "DN_tumble_dry", "DN_iron"},
    "실크": {"hand_wash", "DN_bleach", "DN_tumble_dry", "DN_iron", "dry_flat_shade"},
    "캐시미어": {"DN_wash", "DN_bleach", "DN_tumble_dry", "dry_flat_shade", "DN_iron"},
    "기타": {"DN_bleach", "machine_wash_normal"},
}


def infer_missing_labels(material: str, detected_labels: list[str]) -> list[tuple[str, float]]:
    material = material.lower()
    expected = set()

    for key, labels in MATERIAL_LABEL_MAP.items():
        if key in material:
            expected |= labels

    if not expected:
        expected = MATERIAL_LABEL_MAP["기타"]

    missing = expected - set(detected_labels)
    return [(label, 0.0) for label in missing]
