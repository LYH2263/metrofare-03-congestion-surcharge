from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_path
from app.modules import congestion_surcharge as cs


def quote_route(
    edges: list[tuple[str, str]],
    start: str,
    end: str,
    rules: list[dict],
    congestion: list[dict] | None = None,
) -> dict:
    path = shortest_path(edges, start, end)
    if path is None:
        return {
            "start": start,
            "end": end,
            "hops": None,
            "path": None,
            "base_fare": None,
            "surcharge_total": None,
            "payable": None,
            "fare": None,
            "congestion_edges": [],
            "reachable": False,
        }
    hops = len(path) - 1
    base_fare = fare_for_hops(hops, rules)
    surcharge_total, used = cs.path_surcharge(path, congestion or [])
    payable = round(base_fare + surcharge_total, 2)
    return {
        "start": start,
        "end": end,
        "hops": hops,
        "path": path,
        "base_fare": base_fare,
        "surcharge_total": surcharge_total,
        "payable": payable,
        # fare 保留为应付票价，兼容既有读 fare 的调用方
        "fare": payable,
        "congestion_edges": used,
        "reachable": True,
    }
