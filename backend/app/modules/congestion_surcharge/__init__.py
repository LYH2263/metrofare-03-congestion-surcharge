"""拥挤附加模块：附加挂在邻接边上，按边上的拥挤等级收取加价。

- 每条邻接边可设置一个拥挤等级及对应加价；
- 等级必须在 LEVELS 内，否则拒绝；
- 询价时沿最短路把途经每一边的加价加总，与询价钟点无关。
"""

# 拥挤等级 -> 该边上的加价（元）。顺序即拥挤程度由轻到重。
LEVELS: dict[str, float] = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
}


class CongestionError(ValueError):
    """拥挤等级非法或附加写到不存在的边上。"""


def validate_level(level: str) -> str:
    if level not in LEVELS:
        raise CongestionError(f"invalid congestion level: {level!r}")
    return level


def surcharge_for_level(level: str) -> float:
    validate_level(level)
    return round(LEVELS[level], 2)


def as_map(items) -> dict[tuple[str, str], dict]:
    """把拥挤边列表归一成以无序边对为键的映射，便于沿路径查询。"""
    out: dict[tuple[str, str], dict] = {}
    for it in items:
        out[_key(it["a"], it["b"])] = it
    return out


def path_surcharge(path: list[str], items) -> tuple[float, list[dict]]:
    """沿最短路（顶点序列）累计途经边的拥挤加价。

    返回 (附加合计, 途经拥挤边列表)。无任何拥挤边时合计为 0、列表为空。
    """
    table = as_map(items)
    used: list[dict] = []
    total = 0.0
    for a, b in zip(path, path[1:]):
        hit = table.get(_key(a, b))
        if hit is None:
            continue
        amount = round(float(hit["surcharge"]), 2)
        used.append({"a": a, "b": b, "level": hit["level"], "surcharge": amount})
        total = round(total + amount, 2)
    return total, used


def _key(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a <= b else (b, a)
