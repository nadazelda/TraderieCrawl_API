
from chrome.ChromeDriver import ChromeDriver
import json, re, os

class TraBaseItemCrawl:
    #트레더리에서 재료 아이템 목록을 뽑아내는 클래스 
    def __init__(self, usernameStr, passwordStr) -> None:
        
        self._driver = ChromeDriver()
        self._itemNameMap = self._loadItemNameMap()
        self._categoryMap = self._loadCategoryMap()
        self._getBaseItemList() #트레더리 아이디리스트 뽑아내기

    # ✅ item-names.json 불러오기
    def _loadItemNameMap(self):
        with open("jsons/item-names.json", "r", encoding="utf-8") as f:
            raw_list = json.load(f)
        return {item["enUS"]: item["koKR"] for item in raw_list if "enUS" in item and "koKR" in item}
    def _loadCategoryMap(self):
        with open("jsons/item-category.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        return raw     
    def _getBaseItemList(self):
        results = []
        
        for page in range(1, 20):
            baseUrl = f"https://traderie.com/api/diablo2resurrected/items?type=base&tags=true&page={page}"
            self._driver.get(baseUrl)
            
            try:
                # "pre" 태그가 로딩될 때까지 기다림
                self._driver.waitAllByCssSelector("pre")

                # JSON 텍스트 추출
                data = self._driver.findElementByCssSelector("pre").text
                items = json.loads(data)["items"]

                for item in items:
                    # ctg URL에서 필요한 부분(예: 'club', 'javelin')만 추출
                    ctg_match = re.search(r'https://cdn\.nookazon\.com/diablo2resurrected/([a-zA-Z0-9_-]+)', item["img"])
                    
                    ctg_category = ctg_match.group(1) if ctg_match else "unknown"
                    item_tier = next(
                        (tag["tag"] for tag in item["tags"] if tag["category"] == "Tier"),
                        None  # ← 없을 경우 None 반환
                    )
                    # ✅ korName 설정: name이 key에 있다면 koKR로, 없으면 빈 문자열
                    kor_name = self._itemNameMap.get(item["name"], "")
                    # 소켓수 추출                     
                    desc = item.get("description", "")
                    socket_match = re.search(r"Max sockets:\s*(\d+)", desc)
                    max_sockets = int(socket_match.group(1)) if socket_match else None
                    # ✅ ctg_category 기반 group 추출 (bow → weapon 등)
                    
                    # 그룹 정보 추출
                    group = None
                    if ctg_category in self._categoryMap:
                        category_info = self._categoryMap[ctg_category]
                        if isinstance(category_info, dict):
                            group = category_info.get("group")
                            ##동의어가 잇을땐 표준용어로교체
                            #Claws 류가 h2h로 돼있음 
                            if "same" in category_info:
                                ctg_category = category_info["same"]
                    results.append({
                        "id": item["id"],
                        "ctg": ctg_category,
                        "img" : item["img"],
                        "name": item["name"],
                        "maxSockets":max_sockets,
                        "korName": kor_name,
                        "group":group,
                        "tier":item_tier
                    })
                #print(results)
                print(f"✅ Page {page} fetched")
            except Exception as e:
                print(f"❌ Page {page} failed — {e}")
        # ✅ 외부 JSON 파일에서 추가 아이템 불러오기
        # 반지, 목걸이의 경우 없어서 강제로 추가합니다
        extra_path = "jsons/addBaseItem.json"
        if os.path.exists(extra_path):
            try:
                with open(extra_path, "r", encoding="utf-8") as f:
                    extra_items = json.load(f)
                    if isinstance(extra_items, list):
                        results.extend(extra_items)
                        print(f"✅ Extra {len(extra_items)} items loaded from {extra_path}")
                    else:
                        print(f"⚠ 경고: {extra_path} 내용이 리스트 형식이 아님")
            except Exception as e:
                print(f"❌ 추가 아이템 로드 실패: {e}")
        else:
            print(f"ℹ 추가 아이템 파일 없음: {extra_path}")
                
                
        result_df = sorted(results, key=lambda x: x['korName'] or '', reverse=False)
        # 결과 저장
        with open("crawlResult/baseItemList.json", "w", encoding="utf-8") as f:
            json.dump(result_df, f, ensure_ascii=False, indent=2)

        return results