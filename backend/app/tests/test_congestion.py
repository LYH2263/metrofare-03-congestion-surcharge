import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="metrofare-test-")
os.environ["DATA_DIR"] = _tmp

import pytest  # noqa: E402

from app import seed  # noqa: E402
from app.engines.route_quote import quote_route  # noqa: E402
from app.modules.congestion_surcharge import (  # noqa: E402
    LEVELS,
    CongestionError,
    path_surcharge,
    validate_level,
)
from app.services.metro_service import MetroService  # noqa: E402

EDGES = [("A1", "A2"), ("A2", "A3"), ("A2", "B1"), ("B1", "B2")]
RULES = [{"max_hops": 2, "price": 3.0}, {"max_hops": 4, "price": 4.0}, {"max_hops": None, "price": 6.0}]

seed.init_db()


# ---- 纯领域逻辑 ----

def test_levels_are_valid_and_priced():
    assert set(LEVELS) == {"low", "medium", "high"}


def test_invalid_level_rejected():
    with pytest.raises(CongestionError):
        validate_level("rush")


def test_no_congestion_means_zero_surcharge():
    q = quote_route(EDGES, "A1", "B2", RULES, [])
    assert q["base_fare"] == 4.0
    assert q["surcharge_total"] == 0.0
    assert q["payable"] == 4.0
    assert q["fare"] == 4.0
    assert q["congestion_edges"] == []


def test_path_surcharge_accumulates_only_traversed_edges():
    total, used = path_surcharge(
        ["A1", "A2", "B1", "B2"],
        [
            {"a": "A2", "b": "B1", "level": "high", "surcharge": 3.0},
            {"a": "A2", "b": "A3", "level": "low", "surcharge": 1.0},
        ],
    )
    assert total == 3.0
    assert used == [{"a": "A2", "b": "B1", "level": "high", "surcharge": 3.0}]


# ---- 落库与服务层 ----

def test_set_on_missing_edge_rejected():
    with MetroService() as s, pytest.raises(ValueError):
        s.set_congestion("A1", "A9", "high")


def test_set_invalid_level_rejected():
    with MetroService() as s, pytest.raises(ValueError):
        s.set_congestion("A2", "B1", "evening")


def test_full_congestion_flow_and_snapshot():
    with MetroService() as s:
        # 市心-北苑 设为高拥挤（边无向，反向下单也应命中）
        row = s.set_congestion("B1", "A2", "high")
        assert row == {"a": "A2", "b": "B1", "level": "high", "surcharge": 3.0}

        listed = {(e["a"], e["b"]): e for e in s.congestion_edges()}
        assert ("A2", "B1") in listed

        # 城站 -> 机场 最短路 A1-A2-B1-B2，途经该拥挤边
        q = s.quote("A1", "B2", persist=True)
        assert q["reachable"]
        assert q["path"] == ["A1", "A2", "B1", "B2"]
        assert q["base_fare"] == 4.0
        assert q["surcharge_total"] == 3.0
        assert q["payable"] == 7.0
        assert q["fare"] == 7.0
        assert q["congestion_edges"] == [
            {"a": "A2", "b": "B1", "level": "high", "surcharge": 3.0}
        ]
        run_id = q["run_id"]
        assert run_id is not None

        # 只读询价不写记录
        before = {r["id"] for r in s.history(1000)}
        s.quote("A1", "A3", persist=False)
        after = {r["id"] for r in s.history(1000)}
        assert before == after

        # 清除市心-北苑拥挤后再询城站到机场：该边不得再出现
        s.clear_congestion("A2", "B1")
        assert s.congestion_edges() == []
        q2 = s.quote("A1", "B2", persist=False)
        assert q2["congestion_edges"] == []
        assert q2["surcharge_total"] == 0.0
        assert q2["payable"] == 4.0

        # 按编号打开旧记录：当时列出的拥挤边保持原样
        old = s.history_run(run_id)
        snap = old["result"]
        assert snap["congestion_edges"] == [
            {"a": "A2", "b": "B1", "level": "high", "surcharge": 3.0}
        ]
        assert snap["surcharge_total"] == 3.0
        assert snap["payable"] == 7.0


def test_surcharge_independent_of_hour_of_day():
    with MetroService() as s:
        s.set_congestion("A2", "A3", "medium")
        q = s.quote("A1", "A3", persist=False)
        # 入参没有任何钟点字段，加价只由途经边决定
        assert q["surcharge_total"] == 2.0
        assert q["payable"] == 5.0
        s.clear_congestion("A2", "A3")
