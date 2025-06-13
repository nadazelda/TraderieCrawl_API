from services.TerrorZon import TerrorZoneFromD2Emu
from datetime import datetime
import time

# 캐시 전역 변수
_cached_terror_data = None
_last_fetch_time = 0
_last_fetch_hour = -1
CACHE_DURATION = 60*28  #28분

def get_terror_zone_cached():
    global _cached_terror_data, _last_fetch_time, _last_fetch_hour

    now = datetime.now()
    current_hour = now.hour
    now_timestamp = time.time()

    # ✅ 조건 1: 정각이 바뀌었을 때
    hour_changed = current_hour != _last_fetch_hour

    # ✅ 조건 2: 5분 이상 지났을 때 (예외 상황 대비)
    too_old = now_timestamp - _last_fetch_time > CACHE_DURATION

    if _cached_terror_data is None or hour_changed or too_old:
        print("🔄 테러존 정보 새로 요청 (정각 변경 또는 캐시 만료)")
        _cached_terror_data = TerrorZoneFromD2Emu().result
        _last_fetch_time = now_timestamp
        _last_fetch_hour = current_hour
    else:
        print("✅ 캐시된 테러존 정보 사용 중")

    return _cached_terror_data