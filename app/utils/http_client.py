import httpx


def get(url: str, timeout_ms: int) -> httpx.Response:
    timeout_seconds = timeout_ms / 1000
    return httpx.get(url, timeout=httpx.Timeout(timeout_seconds))
