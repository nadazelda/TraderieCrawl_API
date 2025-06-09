import pandas as pd
import re
import json
from difflib import SequenceMatcher

class ItemOption:
    
    def __init__(self) -> None:
        with open('jsons/option-filters.json', encoding='utf-8') as f:
            self.removal_keywords = json.load(f)

        with open('jsons/option_replacements.json', encoding='utf-8') as f:
            self.replacement_dict = {k.lower(): v for k, v in json.load(f).items()}

        self.modify_options = pd.read_json('jsons/modifyOption.json')
        self.game_options = pd.read_json('jsons/item-modifiers.json')
        self.tra_options = pd.read_json("jsons/traderie_api_optionList.json")

        self.global_options = pd.read_json("jsons/global-options.json")
        with open('jsons/global-options.json', encoding='utf-8') as f:
          global_raw = json.load(f)
          self.global_options = {entry['id'] for entry in global_raw}

        self.results = []
        self.process_options()

    def apply_removal_filter(self, text: str) -> bool:
        return any(keyword.lower() in text.lower() for keyword in self.removal_keywords)

    def apply_fixed_replacements(self, text: str) -> str:
        for eng, kor in sorted(self.replacement_dict.items(), key=lambda x: -len(x[0])):
            pattern = re.compile(re.escape(eng), re.IGNORECASE)
            text = pattern.sub(kor, text)
        return re.sub(r'\s{2,}', ' ', text).strip()

    def normalize(self, text: str) -> str:
        text = re.sub(r'%\+?d|%i|%%', '', text.lower())
        text = re.sub(r'[^a-zA-Z가-힣0-9\s]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def get_manual_translation(self, name: str, current_kokr: str) -> str:
      if current_kokr and current_kokr != name:
          return current_kokr

      for _, row in self.modify_options.iterrows():
          en = row['enUS']
          ko = row['koKR']

          # 특수 패턴 처리: "XXX (Class Only)" 구조
          match = re.match(r"^(.*)\s\(([^)]+ Only)\)$", name)
          if match:
              skill_part, class_part = match.groups()
              if skill_part.strip().lower() == en.lower():
                  return f"{ko} ({class_part.strip()})"

          # 일반 포함 치환
          if en.lower() in name.lower():
              return re.sub(en, ko, name, flags=re.IGNORECASE)

      return None

    def get_game_option_translation(self, name: str, current_kokr: str) -> str:
        if current_kokr and current_kokr != name:
            return current_kokr
        name_norm = self.normalize(name)
        best_match = None
        best_score = 0.0
        for _, row in self.game_options.iterrows():
            en_norm = self.normalize(str(row.get('enUS', '')))
            score = SequenceMatcher(None, en_norm, name_norm).ratio()
            if score > best_score and score >= 0.75:
                best_match = row.get('koKR')
                best_score = score
        # if best_match:
        #     print(f"✅ FUZZY MATCH: '{name}' → '{best_match}' (score: {best_score:.2f})")
        # else:
        #     print(f"❌ NO FUZZY MATCH: '{name}'")
        return best_match

    def process_options(self):
        
        for _, item in self.tra_options.iterrows():
            name_original = item.get('name', '')
            name = name_original
            item_id = item.get('id')
            if not name:
                continue

            if re.match(r"^to .*\(.*Only\)$", name):
                name = name[3:].strip()

            if self.apply_removal_filter(name):
                #print(f"⚠ FILTERED OUT: '{name}'")
                continue

            kokr = item.get('koKR', '')
            name = self.apply_fixed_replacements(name)

            manual_result = self.get_manual_translation(name, kokr)
            if manual_result:
                kokr = manual_result
            else:
                game_kokr = self.get_game_option_translation(name, kokr)
                kokr = game_kokr if game_kokr else name

            kokr = self.apply_fixed_replacements(kokr)
            #print(f"📌 FINAL: '{name}' → '{kokr}'")

            self.results.append({
                'id': item_id,
                'name': name_original,
                'koKR': kokr,
                'global':item_id in self.global_options
            })

        cleaned_results = []
        for row in self.results:
            cleaned_row = row.copy()
            if cleaned_row['koKR']:
                cleaned_row['koKR'] = re.sub(r'%(?:\+)?[di]', '', cleaned_row['koKR'])
                cleaned_row['koKR'] = re.sub(r'%%', '', cleaned_row['koKR'])
                cleaned_row['koKR'] = re.sub(r'\s{2,}', ' ', cleaned_row['koKR']).strip()
            cleaned_results.append(cleaned_row)

        cleaned_results = sorted(cleaned_results, key=lambda x: x['koKR'] or '')
        pd.DataFrame(cleaned_results).to_json(
            'crawlResult/optionCombo.json',
            orient='records',
            force_ascii=False,
            indent=2
        )
        