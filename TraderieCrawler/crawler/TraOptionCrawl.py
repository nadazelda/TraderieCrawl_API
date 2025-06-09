
from chrome.ChromeDriver import ChromeDriver
import json
class TraOptionCrawl:
    #트레더리에서 옵션 목록을 뽑아내는 클래스 
    def __init__(self, usernameStr, passwordStr) -> None:
        self._driver = ChromeDriver()
        self._getTraderie_optionList() #트레더리 아이디리스트 뽑아내기
    def _getTraderie_optionList(self):
      results = []

      baseUrl = "https://traderie.com/api/diablo2resurrected/properties"
      self._driver.get(baseUrl)
      try:
          # "pre" 태그가 로딩될 때까지 기다림
          self._driver.waitAllByCssSelector("pre")

          # JSON 텍스트 추출
          data = self._driver.findElementByCssSelector("pre").text
          items = json.loads(data)["properties"]

          for item in items:
              results.append({
                  "name": item.get("name", ""),
                  "id": item.get("id", ""),
                  "format": item.get("format", {})
              })
          print(f"✅ TraOptionCrawl 옵션 리스트 추출 성공")
      except Exception as e:
          print(f"❌ TraOptionCrawl 옵션 리스트 추출 실패 — {e}")

      # 결과 저장
      with open("jsons/traderie_api_optionList.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

      return results