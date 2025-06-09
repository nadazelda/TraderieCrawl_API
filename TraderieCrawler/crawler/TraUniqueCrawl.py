
from chrome.ChromeDriver import ChromeDriver
import json

class TraUniqueCrawl:
    #트레더리에서 유니크 아이템 목록을 뽑아내는 클래스 
    def __init__(self, usernameStr, passwordStr) -> None:
        self._driver = ChromeDriver()
        self._getUniqueList()  #트레더리 아이디리스트 뽑아내기
        
    def _getUniqueList(self):
        results = []
        for page in range(1, 18):
            baseUrl = f"https://traderie.com/api/diablo2resurrected/items?variants=&type=uniques&tags=true&page={page}"
            self._driver.get(baseUrl)
            try:
                # "pre" 태그가 로딩될 때까지 기다림
                self._driver.waitAllByCssSelector("pre")

                # JSON 텍스트 추출
                data = self._driver.findElementByCssSelector("pre").text
                items = json.loads(data)["items"]

                for item in items:
                    desc_text = item.get("description") or ""  # None이면 ""로
                    desc_lines = desc_text.split("\n")
                    desc_cleaned = [line.strip() for line in desc_lines if line.strip()]
                    results.append({
                        "id": item["id"],
                        "name": item["name"],
                        "img" : item["img"],
                        "description": desc_cleaned
                    })
                #print(results)
                print("✅ TraUniqueCrawl Page {page} fetched")
            except Exception as e:
                print("❌ TraUniqueCrawl Page {page} failed — {e}")
        # 결과 저장
        with open("jsons/traderie_api_unique.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return results