from urllib.parse import quote

class TraderieUrlBuilder:
    BASE_API_URL = "https://traderie.com/api/diablo2resurrected/listings"
    REAL_URL = "https://traderie.com/diablo2resurrected/product"

    def __init__(self, item_key: int):
        self.item_key = item_key
        self.params = {"item": item_key}

    def set_common_props(self, ladder: str, mode: str, ethereal: bool):
        if ladder == "Ladder":
            self.params["prop_Ladder"] = "true"
        elif ladder == "Non Ladder":
            self.params["prop_Ladder"] = "false"
        elif "Ladder" in ladder and "Non Ladder" in ladder:
            self.params["prop_Ladder"] = "Ladder,Non Ladder"
        else:
            self.params["prop_Ladder"] = ladder  # fallback (필요시 제거 가능)
        self.params["prop_Mode"] = mode
        self.params["prop_Ethereal"] = str(ethereal).lower()
        
    def set_global_props(self, global_props: dict):
        for key, value in global_props.items():
            if key.startswith("prop_"):
                # 기존 동작: true인 경우만 추가
                if isinstance(value, bool) and value is True:
                    self.params[key] = "true"
                # 새 동작: 문자열인 경우 그대로 추가
                elif isinstance(value, str):
                    self.params[key] = value
                
    def set_options(self, options: list):
        for opt in options:
            key = opt.get("key")
            min_val = opt.get("min")
            max_val = opt.get("max")
            if min_val is not None:
                self.params[f"prop_{key}Min"] = min_val
            if max_val is not None:
                self.params[f"prop_{key}Max"] = max_val

    def set_rarity(self, rarity: str):
        if rarity:
            self.params["prop_Rarity"] = rarity

    # def _build_query_string(self, exclude_keys=None):
    #     if exclude_keys is None:
    #         exclude_keys = []
    #     return "&".join([f"{k}={v}" for k, v in self.params.items() if k not in exclude_keys])


    def _build_query_string(self, exclude_keys=None):
        if exclude_keys is None:
            exclude_keys = []
        return "&".join([
            f"{quote(str(k), safe='')}={quote(str(v), safe='')}"
            for k, v in self.params.items()
            if k not in exclude_keys
        ])




    def get_base_url(self):
        return f"{self.BASE_API_URL}?{self._build_query_string()}"

    def get_real_url(self):
        # 'item'은 real_url 쿼리에서 제거
        return f"{self.REAL_URL}/{self.item_key}?{self._build_query_string(exclude_keys=['item'])}"

