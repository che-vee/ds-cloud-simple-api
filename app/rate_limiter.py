import time
from typing import Dict

def fixed_window_rate_limiter(rate: int, window_size: int):
    ip_count = {}

    def consume(ip: str):
        current_time = time.time()

        if ip not in ip_count or current_time - ip_count[ip]["window_start_time"] >= window_size:
            ip_count[ip] = {"window_start_time": current_time, "window_count": 1}
            return True

        if ip_count[ip]["window_count"] < rate:
            ip_count[ip]["window_count"] += 1
            return True

        return False

    return consume