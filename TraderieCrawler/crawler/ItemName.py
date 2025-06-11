import pandas as pd
import re

class ItemName:
    excluded_keywords = ['Per Char Level', 'Based On Char Level', 'Based On Character Level','sec Duration','Duration','H damage','Durability'
    ,'To Maximum Damage'
    ,'Paladin smite dmg'
    ,'Assassin kick dmg'
    ,'Fire Damage'
    ,'Defense (Based on Character Level)'
    
    ]
    remove_same_keyword=['Damage']
    #pattern = re.compile(r'\(?\+?(\d+)[-~](\d+)%?\)?\s*(.*)') #독사마술사 날라감;;
    pattern = re.compile(r'(.*?)(\d+)[-~](\d+)', re.IGNORECASE)



    def _makeDataFrameFilter(self, data, filter):
        rtn_data_df = pd.DataFrame(data)
        if filter:  # 빈 리스트나 None이 아닌 경우
            rtn_data_df = rtn_data_df[filter]
        return rtn_data_df
    def parse_description(self, desc_list):
        parsed = []
        for line in desc_list:
            # 특정 키워드 포함된 옵션제거 
            if any(keyword in line for keyword in self.excluded_keywords):
                #print(f"❌ excluded: {line}")
                continue
            
            line = line.strip()
            
            # 완전 일치 제거# 특정 키워드 동일한 옵션제거       
            if line in self.remove_same_keyword:
                continue

            # (1) 범위가 앞에 있는 경우
            m = re.search(r'[-+]?[\(]?(\d+)[-~](\d+)[\)%\s]*([a-zA-Z ].*)$', line)
            if m:
                min_val = int(m.group(1))
                max_val = int(m.group(2))
                prop = m.group(3).strip()
                parsed.append({
                    "min": min_val,
                    "max": max_val,
                    "property": prop
                })
                #print(f"✅ parsed (front): {line} → {prop}")
                continue

            # (2) 범위가 뒤에 있는 경우
            m = re.search(r'^(.*?)[\s:+~]+(\d+)[-~](\d+)%?$', line)
            if m:
                prop = m.group(1).strip()
                min_val = int(m.group(2))
                max_val = int(m.group(3))
                parsed.append({
                    "min": min_val,
                    "max": max_val,
                    "property": prop
                })
                #print(f"✅ parsed (rear): {line} → {prop}")
                continue
            # (3) 패턴: Cold Resist (-70% to -90%)
            m = re.search(r'^([A-Za-z ]*Resist(?:ance)?)\s*\(\s*-?(\d+)%?\s+to\s+-?(\d+)%?\s*\)$', line)
            if m:
                prop = m.group(1).strip()
                min_val = int(m.group(2))
                max_val = int(m.group(3))
                parsed.append({
                    "min": min_val,
                    "max": max_val,
                    "property": prop
                })
                #print(f"✅ parsed (to-range): {line} → {prop}")
                continue
            # (4) 괄호 안 수치만 존재: Damage Increased by (10-30%)
            m = re.search(r'^(.*?)\s*\(\s*(\d+)[-~](\d+)%?\s*\)$', line)
            if m:
                prop = m.group(1).strip()
                min_val = int(m.group(2))
                max_val = int(m.group(3))
                parsed.append({
                    "min": min_val,
                    "max": max_val,
                    "property": prop
                })
                #print(f"✅ parsed (in-parens): {line} → {prop}")
                continue  
            # fallback → 넣어야 안 빠짐
            # parsed.append({"property": line})
            #print(f"⚠️ fallback: {line}")

        return parsed
    

    def __init__(self) -> None:
        # uniqueItems 파일
        unique_dia = pd.read_json("jsons/traderie_api_unique.json")

        # korName을 가지고 있는 데이터 불러오기 (예시)
        tra_kor = pd.read_json("jsons/traderie_kor.json")
        tra_kor_df = pd.DataFrame(tra_kor)

        # description 필터링 + 파싱
        unique_dia["description_filtered"] = unique_dia["description"].apply(self.parse_description)

        # unique_dia와 tra_kor_df 병합 (id와 korName 연결된 컬럼명 확인 필요)
        # tra_kor_df에 'id' 컬럼이 없으면 매칭 키를 맞춰서 수정하세요.
        merged_df = pd.merge(unique_dia, tra_kor_df[['traderieCode', 'korName']],
                             left_on='id', right_on='traderieCode', how='left')

        # ✅ korName 공백 제거
        merged_df['korName'] = merged_df['korName'].fillna('').apply(lambda x: re.sub(r'\s+', '', x.strip()))
        # 최종 결과 컬럼 선택 (korName 포함)
        result_df = merged_df[['id', 'name','img', 'korName', 'description_filtered']]
        
        # 저장
        #한글 기준 ㄱ >ㅎ 
        result_df = result_df.sort_values(by='korName', ascending=False)
        
        result_df.to_json('jsons/uniqueItemList.json',orient='records', force_ascii=False, indent=2)