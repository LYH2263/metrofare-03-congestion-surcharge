from collections import defaultdict, deque


def shortest_hops(edges: list[tuple[str, str]], start: str, end: str) -> int | None:
    """Undirected graph BFS hop count; None if unreachable."""
    path = shortest_path(edges, start, end)
    if path is None:
        return None
    return len(path) - 1


def shortest_path(edges: list[tuple[str, str]], start: str, end: str) -> list[str] | None:
    """Undirected graph BFS; returns the vertex list of a shortest path, else None."""
    if start == end:
        return [start]
    g: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        g[a].add(b)
        g[b].add(a)
    if start not in g or end not in g:
        return None
    parents = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        for nxt in g[cur]:
            if nxt in parents:
                continue
            parents[nxt] = cur
            if nxt == end:
                path = [end]
                while parents[path[-1]] is not None:
                    path.append(parents[path[-1]])
                path.reverse()
                return path
            q.append(nxt)
    return None
