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
        self.result = self.get_terror_zone()
        print("📦 결과:", self.result)

    def translate_zone(self, zone_str: str, translation_dict: dict) -> str:
        print('start translate_zone')
        parts = re.split(r"\s*(?:and|,|&)\s*", zone_str)
        translated_parts = [self._fuzzy_translate(p.strip(), translation_dict) for p in parts]
        separators = re.findall(r"\s*(?:and|,|&)\s*", zone_str)
        result = translated_parts[0]
        for sep, part in zip(separators, translated_parts[1:]):
            result += sep + part
        return result
    def _normalize(self, text: str) -> str:
        return re.sub(r"[^a-zA-Z0-9]", "", text).lower()
    def _fuzzy_translate(self, zone: str, translation_dict: dict) -> str:
        print('start _fuzzy_translate')
        print('zone',zone)
        norm_zone = self._normalize(zone)
        print('norm zone',norm_zone)
        norm_dict  = {self._normalize(k): v for k, v in translation_dict.items()}
        
        # 정확히 일치하면 바로 반환
        if norm_zone in norm_dict:
            return norm_dict[norm_zone]
        # 비슷한 키 중 가장 유사한 항목 찾기 (유사도 0.8 이상)
        close_matches = get_close_matches(norm_zone, norm_dict.keys(), n=1, cutoff=0.8)
        if close_matches:
            return norm_dict[close_matches[0]]
        print(f"❌ 번역 실패: {zone}")
        return zone  # 번역 실패 시 원문 그대로

    def get_terror_zone(self):
        TRANSLATION_FILE = "json/diablo_areaName.json"
        if os.path.exists(TRANSLATION_FILE):
            with open(TRANSLATION_FILE, "r", encoding="utf-8") as f:
                AREA_TRANSLATIONS = json.load(f)
        else:
            AREA_TRANSLATIONS = {}

        url = "https://d2runewizard.com/api/terror-zone"
        print('terrorzon url',url)
        try:
            res = requests.get(url, timeout=5)
            res.raise_for_status()
            data = res.json()

            current = data.get("currentTerrorZone", {})
            next_ = data.get("nextTerrorZone", {})

            current_zone = self.translate_zone(current.get("zone", "Unknown"), AREA_TRANSLATIONS)
            next_zone = self.translate_zone(next_.get("zone", "Unknown"), AREA_TRANSLATIONS)

            current_act = self.ACT_TRANSLATIONS.get(current.get("act", "").lower(), current.get("act", "Unknown"))
            next_act = self.ACT_TRANSLATIONS.get(next_.get("act", "").lower(), next_.get("act", "Unknown"))

            return {
                "currTerror": f"{current_act}({current_zone})",
                "nextTerror": f"{next_act}({next_zone})"
            }

        except requests.RequestException as e:
            return {"error": f"API 요청 실패: {e}"}