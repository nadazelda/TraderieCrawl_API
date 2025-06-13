import json, time, os, requests, re
from difflib import get_close_matches

class TerrorZoneFromD2Emu:
    ACT_TRANSLATIONS = {
        "act1": "액트 1",
        "act2": "액트 2",
        "act3": "액트 3",
        "act4": "액트 4",
        "act5": "액트 5"
    }

    def __init__(self):
        self.translation_dict = self._load_translations()
        self.norm_dict = {self._normalize(k): v for k, v in self.translation_dict.items()}
        print("📂 정규화된 키 목록 일부:")
        for k in list(self.norm_dict.keys())[:10]:
            print("  -", k)
        self.result = self.get_terror_zone()
        print("📦 결과:", self.result)

    def _load_translations(self):
        path = "jsons/diablo_areaName.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _normalize(self, text: str) -> str:
        return re.sub(r"[^a-zA-Z0-9]", "", text).lower()

    def _fuzzy_translate(self, zone: str) -> str:
        norm_zone = self._normalize(zone)
        
        print(f"\n🟡 원본 zone: '{zone}' → 정규화: '{norm_zone}'")

        if norm_zone in self.norm_dict:
            print(f"✅ 정확 일치: '{zone}' → '{self.norm_dict[norm_zone]}'")
            return self.norm_dict[norm_zone]

        close_matches = get_close_matches(norm_zone, self.norm_dict.keys(), n=1, cutoff=0.8)
        if close_matches:
            match = close_matches[0]
            print(f"🧩 유사 일치: '{zone}' ≈ '{match}' → '{self.norm_dict[match]}'")
            return self.norm_dict[match]

        print(f"❌ 번역 실패: {zone}")
        return zone

    def translate_zone(self, zone_str: str) -> str:
        parts = re.split(r"\s*(?:and|,|&)\s*", zone_str)
        translated_parts = [self._fuzzy_translate(p.strip()) for p in parts]
        separators = re.findall(r"\s*(?:and|,|&)\s*", zone_str)
        result = translated_parts[0]
        for sep, part in zip(separators, translated_parts[1:]):
            result += sep + part
        return result


    def get_terror_zone(self):
        
        url = "https://d2runewizard.com/api/terror-zone"
        
        try:
            res = requests.get(url, timeout=5)
            res.raise_for_status()
            data = res.json()

            current = data.get("currentTerrorZone", {})
            next_ = data.get("nextTerrorZone", {})

            current_zone = self.translate_zone(current.get("zone", "Unknown"))
            next_zone = self.translate_zone(next_.get("zone", "Unknown"))

            current_act = self.ACT_TRANSLATIONS.get(current.get("act", "").lower(), current.get("act", "Unknown"))
            next_act = self.ACT_TRANSLATIONS.get(next_.get("act", "").lower(), next_.get("act", "Unknown"))

            return {
                "currTerror": f"{current_act}({current_zone})",
                "nextTerror": f"{next_act}({next_zone})"
            }

        except requests.RequestException as e:
            return {"error": f"API 요청 실패: {e}"}
