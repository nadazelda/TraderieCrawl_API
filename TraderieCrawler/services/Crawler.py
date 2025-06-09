import json, requests, subprocess
# import time
from urllib.parse import urlencode
from datetime import datetime, timezone, timedelta

from chrome.ChromeDriver import ChromeDriver

class Crawler:
    def __init__(self) -> None:
        self._driver = ChromeDriver() # 나중에 크롤러 할때
        
        # 리턴하는 형태로 바꾸기 위해 주석처리 트레더리 아이디리스트 뽑아내기
        # self._getSearchItem()
        
    def get_listing_summary(self, url: str):
        print(f"📡 Traderie JSON 요청: {url}")
        try:
            self._driver.get(url)
            self._driver.waitAllByCssSelector("pre", timeout=10)
            json_text = self._driver.findElementByCssSelector("pre").text
            parsed = json.loads(json_text)
            listings = parsed.get("listings", [])
            results = []

            def format_time(utc_str):
                dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                diff = now - dt
                if diff < timedelta(minutes=1):
                    return "방금 전"
                elif diff < timedelta(hours=1):
                    return f"{int(diff.total_seconds() // 60)}분 전"
                elif diff < timedelta(days=1):
                    return f"{int(diff.total_seconds() // 3600)}시간 전"
                else:
                    return dt.astimezone(timezone(timedelta(hours=9))).strftime("%Y.%m.%d %H:%M")
            for listing in listings[:20]:  # 상위 20개만
                prices = listing.get("prices") or []

                groups = {}  # group별 분류
                group_imgs = {}  # group별 이미지 리스트
                group_qtys = {}  # group별 수량 리스트

                for p in prices:
                    if not isinstance(p, dict):
                        continue
                    group = p.get("group", 0)
                    name = p.get("name", "N/A")
                    qty = p.get("quantity", 1)
                    img = p.get("img")

                    if group not in groups:
                        groups[group] = []
                        group_imgs[group] = []
                        group_qtys[group] = []

                    groups[group].append(f"{name} x{qty}")
                    group_imgs[group].append(img or "")
                    group_qtys[group].append(qty)
                sorted_groups = sorted(groups.keys())
                # 그룹별 텍스트를 OR로 구분
                # price_texts = [", ".join(groups[g]) for g in sorted(groups.keys())]
                # price_imgs = [group_imgs[g] for g in sorted(group_imgs.keys())]
                # price_qtys = [group_qtys[g] for g in sorted(group_qtys.keys())]
                if len(sorted_groups) == 1:
                    price_texts = [", ".join(groups[sorted_groups[0]])]
                    price_imgs = [group_imgs[sorted_groups[0]]]
                    price_qtys = [group_qtys[sorted_groups[0]]]
                else:
                    # ✅ 그룹이 여러 개일 경우 OR로 나누어 배열 유지
                    price_texts = [", ".join(groups[g]) for g in sorted_groups]
                    price_imgs = [group_imgs[g] for g in sorted_groups]
                    price_qtys = [group_qtys[g] for g in sorted_groups]



                updated = listing.get("updated_at", "")
                results.append({
                    "price_texts": (price_texts,"제안요청"),   # ✅ 그룹별 가격 텍스트 리스트 (OR 구분 가능)
                    "price_imgs": price_imgs,     # ✅ 그룹별 이미지 리스트
                    "price_qtys": price_qtys,     # ✅ 그룹별 수량 리스트
                    "updated_at": format_time(updated),
                    "id": listing.get("id")
                })

            return {
                "listings": results
            }        
        except Exception as e:
            print(f"❌ 크롤링 실패: {e}")
            return {
                "listings": []
            }
    def _getSearchItem(self) :
        result = []
        # paramJson.json 읽기
        with open("paramJson.json", "r", encoding="utf-8") as f:
            items = json.load(f)
        base_url = "https://traderie.com/api/diablo2resurrected/listings"
        real_url_base = "https://traderie.com/diablo2resurrected/product/"
        for item in items:
            query_params = {
                "item": item["item_id"],
                "prop_Ladder": item["isLadder"]
            }
            query_params.update(item["props"])

            url = f"{base_url}?{urlencode(query_params)}"
            real_url = f"{real_url_base}{item['item_id']}?{urlencode(query_params)}"
            print(f"Checking: {url}")
            if hasattr(self, "_driver"):
                self._driver.get(url)
            try:

                self._driver.waitAllByCssSelector("pre", timeout=10)
                # JSON 텍스트 추출
                json_text = self._driver.findElementByCssSelector("pre").text
                print(f"[*] JSON Text length: {len(json_text)}")  # JSON 응답 크기 로그
                parsed = json.loads(json_text)

                listings = parsed.get("listings", [])
                print(f"[*] Item: {item['item_name']}, Listings count: {len(listings)}")  # 매물 개수 로그
                if listings :
                    result.append({
                            "item_name": item['item_name'],
                            "listings_count": len(listings),
                            "real_url" : real_url,
                            "status": "✅" if listings else "❌"
                        })

                # 여기 아래를 주석풀면 출력문까진 정상확인
                # if listings:
                #     print(f"[✅] {item['item_name']} 매물 {len(listings)}건 있음")
                # else:
                #     print(f"[❌] {item['item_name']} 매물 없음")
            except Exception as e:
                print(f"[⚠️] {item['item_name']} 에러: {e}")
        return result
    # fast api에서 호출할 함수
    def get_results(self):
        return self._getSearchItem()
    def Exit(self):
        if hasattr(self, "_driver"):
            self._driver.quit()
