
import pandas as pd
import os,json
from difflib import get_close_matches
from chrome.ChromeDriver import ChromeDriver
import json
import re
import difflib

class TraRunWordsCrawl:
    #트레더리에서 유니크 아이템 목록을 뽑아내는 클래스
    def __init__(self) -> None:
        self._driver = ChromeDriver()
        print('TraRunWordsCrawl init')
        print('TraRunWordsCrawl start')
        self._getRunwordList()  #트레더리 아이디리스트 뽑아내기
        print('TraRunWordsCrawl end')
    def _getRunwordList(self):
        results = []
        with open("jsons/item-category.json", encoding="utf-8") as f:
            type_dict = json.load(f)
        # ✅ 룬워드 소켓 수 매핑
        with open("jsons/runwordsSocket.json", encoding="utf-8") as f:
            socket_list = json.load(f)  # 예: {"Faith": 4, "Enigma": 3, ...}
            socket_dict = {
                item["name"]: item["sockets"]
                for item in socket_list
                if isinstance(item, dict) and "name" in item and "sockets" in item
            }
            
        for page in range(0,5):
            baseUrl = f"https://traderie.com/api/diablo2resurrected/items?type=runewords&tags=true&page={page}"
            self._driver.get(baseUrl)
            try:
                # "pre" 태그가 로딩될 때까지 기다림
                self._driver.waitAllByCssSelector("pre")

                # JSON 텍스트 추출
                data = self._driver.findElementByCssSelector("pre").text
                items = json.loads(data)["items"]

                for item in items:
                  if not isinstance(item, dict):
                      continue

                  # 설명
                  desc_text = item["description"] if "description" in item and item["description"] else ""
                  desc_lines = desc_text.split("\n")
                  desc_cleaned = [line.strip() for line in desc_lines if line.strip()]

                  # 타입
                  item_types = []
                  if "tags" in item and isinstance(item["tags"], list):
                      for tag in item["tags"]:
                          if (
                              isinstance(tag, dict)
                              and "category" in tag
                              and tag["category"] == "Item Type"
                              and "tag" in tag
                          ):
                              item_types.append(tag["tag"])

                  #### tag 값을 잘 가져와야 아이템을 선택합니다

                  converted_types = []
                  if "tags" in item and isinstance(item["tags"], list):
                      for tag_obj in item["tags"]:
                          if (
                              isinstance(tag_obj, dict)
                              and tag_obj.get("category") == "Item Type"
                              and "tag" in tag_obj
                          ):
                              tag_name = tag_obj["tag"]
                              key = tag_name.lower()

                              if key in type_dict:
                                  # dict 복사 후 eng 추가
                                  type_info = type_dict[key].copy()
                                  type_info["eng"] = tag_name
                              else:
                                  # type_dict에 없을 경우 fallback
                                  type_info = {
                                      "kor": tag_name,
                                      "group": tag_name,
                                      "eng": tag_name
                                  }

                              converted_types.append(type_info)

                  # 이름과 소켓 매칭
                  name = item["name"] if "name" in item else ""
                  socket_count = socket_dict[name] if name in socket_dict else None

                  if socket_count is None and name:
                      close_matches = get_close_matches(name, socket_dict.keys(), n=1, cutoff=0.8)
                      if close_matches:
                          print(f"⚠️ '{name}' → 유사 소켓 매칭 '{close_matches[0]}'")
                          socket_count = socket_dict[close_matches[0]]

                  # 결과 누적
                  results.append({
                      "id": item["id"] if "id" in item else None,
                      "name": name,
                      "img": item["img"] if "img" in item else "",
                      "description": desc_cleaned,
                      "sockets": socket_count,
                      "type": converted_types
                  })


                print(f"✅ TraUniqueCrawl Page {page} fetched")
            except Exception as e:
                print(f"❌ TraUniqueCrawl Page {page} failed — {e}")
        # 결과 저장
        with open("jsons/traderie_api_runewords.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return results

#테스트실행
# TraRunWordsCrawl = TraRunWordsCrawl()
