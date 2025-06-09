import json
import re
import difflib


class CrawlResultRunWords:
    def __init__(self) -> None:
        print('start CrawlResultRunWords')
        # 파일 경로
        uniquenameCombo_path = "jsons/runWordsItemList.json"
        optionCombo_path = "crawlResult/optionCombo.json"

        # JSON 로딩
        with open(uniquenameCombo_path, "r", encoding="utf-8") as f:
            self.unique_items = json.load(f)

        with open(optionCombo_path, "r", encoding="utf-8") as f:
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
        print('end CrawlResultRunWords')


    def clean_property_name(self, name: str) -> str:
        cleaned = re.sub(r'%\+?d%%', '', name)      # %+d%% 제거
        cleaned = re.sub(r'[%\d]', '', cleaned)     # 숫자 및 % 제거
        return cleaned.strip()


    def clean_kor_name(self, name: str) -> str:
        cleaned = re.sub(r'\+?%d', '', name)
        cleaned = re.sub(r'\+?d', '', cleaned)
        cleaned = re.sub(r'[%\d]', '', cleaned)
        cleaned = re.sub(r'\s+', '', cleaned)
        return cleaned.strip()

    def find_closest_match(self, property_name: str):
        # 1차: 원문 그대로 매칭
        if property_name in self.option_names:
            return property_name

        # 2차: 클린한 이름 기준 비교
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

            # 앞쪽 수치: (+3-5%) To Cold Skill Damage
            m = re.search(r'^\(?[+-]?(\d+)[-~](\d+)%?\)?\s*(.*)$', line)
            if m:
                min_val = int(m.group(1))
                max_val = int(m.group(2))
                prop = m.group(3).strip()
                parsed.append({"min": min_val, "max": max_val, "property": prop})
                continue

            # 뒤쪽 수치: Cold Skill Damage +3-5%
            m = re.search(r'^(.*?)[\s:+~]+(\d+)[-~](\d+)%?\)?$', line)
            if m:
                prop = m.group(1).strip()
                min_val = int(m.group(2))
                max_val = int(m.group(3))
                parsed.append({"min": min_val, "max": max_val, "property": prop})
                continue

            # fallback
            parsed.append({"property": line})
        return parsed

    def process_items(self):
        for item in self.unique_items:
            # 🔄 description_filtered가 비어 있을 경우 복원
            if not item.get("description_filtered"):
                desc_raw = item.get("description", "")
                if isinstance(desc_raw, str):
                    desc_lines = [line.strip() for line in desc_raw.split("\n") if line.strip()]
                elif isinstance(desc_raw, list):
                    desc_lines = [line.strip() for line in desc_raw if isinstance(line, str) and line.strip()]
                else:
                    desc_lines = []
                item["description_filtered"] = self.parse_description(desc_lines)

            # 🔍 옵션 매칭 및 한글 처리
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
      # 🔹 한글 기준 정렬 (없는 경우 빈 문자열 처리)
      self.unique_items = sorted(
          self.unique_items,
          key=lambda x: (
              x.get("description_filtered")[0].get("property_kor") or ''
              if x.get("description_filtered") and len(x.get("description_filtered")) > 0
              else ""
          ),
          reverse=False
      )
      print("dfdf")
      # 저장
      #결과 를 임시 폴더로 저장한다
      output_path = "crawlResult/runWordsResult.json"
      with open(output_path, "w", encoding="utf-8") as f:
          json.dump(self.unique_items, f, ensure_ascii=False, indent=2)

      print("✅ Finished adding property_id to runWordsResult.json")
