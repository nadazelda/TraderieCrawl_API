import json
import re
import difflib


class CrawlerResult:
    # 🔹 상단에 파일 경로 상수 정의
    UNIQUE_ITEMS_PATH = "jsons/uniqueItemList.json"
    OPTION_COMBO_PATH = "crawlResult/optionCombo.json"
    OUTPUT_PATH = "crawlResult/uniqueResult.json"

    def __init__(self) -> None:
        
        # JSON 로딩
        with open(self.UNIQUE_ITEMS_PATH, "r", encoding="utf-8") as f:
            self.unique_items = json.load(f)

        with open(self.OPTION_COMBO_PATH, "r", encoding="utf-8") as f:
            self.option_items = json.load(f)

        # 매핑 생성
        self.option_names = [opt['name'] for opt in self.option_items]
        self.option_name_to_id = {opt['name']: opt['id'] for opt in self.option_items}
        self.option_name_to_kor = {opt['name']: opt['koKR'] for opt in self.option_items}
        self.cleaned_option_names = [self.clean_property_name(n) for n in self.option_names]

        # 디버그 설정
        self.DEBUG = False

        # 처리 실행
        self.process_items()
        self.sort_and_save()


    def clean_property_name(self, name: str) -> str:
        cleaned = re.sub(r'%\+?d%%', '', name)
        cleaned = re.sub(r'[%\d]', '', cleaned)
        return cleaned.strip()

    def clean_kor_name(self, name: str) -> str:
        cleaned = re.sub(r'\+?%d', '', name)
        cleaned = re.sub(r'\+?d', '', cleaned)
        cleaned = re.sub(r'[%\d]', '', cleaned)
        cleaned = re.sub(r'\s+', '', cleaned)
        return cleaned.strip()

    def find_closest_match(self, property_name: str):
        
        if property_name in self.option_names:
            return property_name


        cleaned_name = self.clean_property_name(property_name)
        
        if cleaned_name in self.cleaned_option_names:
            idx = self.cleaned_option_names.index(cleaned_name)
            return self.option_names[idx]

        matches = difflib.get_close_matches(cleaned_name, self.cleaned_option_names, n=1, cutoff=0.6)
        if matches:
            idx = self.cleaned_option_names.index(matches[0])
            return self.option_names[idx]

        return None

    def parse_description(self, desc_lines):
        parsed = []
        for line in desc_lines:
            line = line.strip()
            if not line:
                continue
            

            m = re.search(r'^\(?[+-]?(\d+)[-~](\d+)%?\)?\s*(.*)$', line)
            if m:
                parsed.append({
                    "min": int(m.group(1)),
                    "max": int(m.group(2)),
                    "property": m.group(3).strip()
                })
                continue
            
            m = re.search(r'^(.*?)[\s:+~]+(\d+)[-~](\d+)%?\)?$', line)
            if m:
                parsed.append({
                    "min": int(m.group(2)),
                    "max": int(m.group(3)),
                    "property": m.group(1).strip()
                })
                continue


            parsed.append({"property": line})
        return parsed

    def process_items(self):
        for item in self.unique_items:
            
            if not item.get("description_filtered"):
                desc_raw = item.get("description", "")
                if isinstance(desc_raw, str):
                    desc_lines = [line.strip() for line in desc_raw.split("\n") if line.strip()]
                elif isinstance(desc_raw, list):
                    desc_lines = [line.strip() for line in desc_raw if isinstance(line, str) and line.strip()]
                else:
                    desc_lines = []
                item["description_filtered"] = self.parse_description(desc_lines)


            for desc in item["description_filtered"]:
                prop = desc.get("property", "")
                matched_name = self.find_closest_match(prop)

                if self.DEBUG:
                    print(f"🔍 {prop} → {matched_name}")

                if matched_name and matched_name in self.option_name_to_id:
                    desc["property_id"] = self.option_name_to_id[matched_name]
                    desc["property_kor"] = self.clean_kor_name(self.option_name_to_kor.get(matched_name, ""))
                else:
                    desc["property_id"] = None
                    desc["property_kor"] = None

    def sort_and_save(self):
        self.unique_items = sorted(
            self.unique_items,
            key=lambda x: (
                x.get("description_filtered")[0].get("property_kor") or ''
                if x.get("description_filtered") and len(x.get("description_filtered")) > 0
                else ""
            ),
            reverse=False
        )

        with open(self.OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(self.unique_items, f, ensure_ascii=False, indent=2)

        print("✅ Finished adding property_id to uniqueResult.json")


# # 실행
# CrawlerResult = CrawlerResult()
