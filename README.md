# TraderieCrawl



## Crawler.py
   - self._getUniqueList()#트레더리 아이디리스트 뽑아내기
     - traderie_api_unique.json 생성
       - 트레더리 1~18페이지까지 유니크 수집
       - id : 트레더리 검색 아이템 키
       - name : 아이템 영어이름
       - description : 아이템 옵션
   - self._getBaseItemList()#base재료아이템'
     - traderie_api_normal.json생성
       - 트레더리 1~20페이지까지 기본 속성(노말)재료 수집
       - id : 트레더리 검색 아이템 키
       - ctg : 아이템 카테고리
       - name : 아이템 영어이름
         
   - self._getTraderie_optionList()# 트레더리 속성리스트 뽑아내기
     - traderie_api_optionList.json 생성
       - id : 트레더리 검색 옵션 키
       - name : 옵션명
       - format : 알수없음.....

## ItemName.py
    - 한글 영문명을 매칭시키고 아이템별 최소/최대값의 옵션도 지정한다 
    - traderie_api_unique.json / traderie_kor.json 으로 한글명 매칭 
    - uniqueItemList.json 생성 
    - id : 트레더리 검색 키 
    - name : 아이템 영문명 
    - korName : 아이템 한글명 
    - description_filtered : 옵션별 min, max 사전
## ItemOption.py
    - item-modifiers.json에서 최대한 비슷한 영문옵션명을 찾아서 한글명을 찾는다 
    - traderie_api_optionList.json / modifyOption.json / item-modifiers.json
    - itemOptionList.json생성
    - id : 트레더리 옵션 키
    - name : 영문옵션명
    - koKR : 한글옵션명

## CrawlerResult.py
    - api에서 사용할 기초 데이터 형식의 json을 생성
    - id : 아이템 검색 키 
    - name : 아이템 영문명 
    - korName : 아이템 한글명 
    - description_filtered: 옵션리스트 
      - min : 옵션 최소값 
      - max : 옵션 최대값 
      - property : 옵션 영문명 
      - property_id : 옵션 검색 키 
      - property_kor : 옵션 한글명 

## traderie_eng.json : 트레더리 영어이름 , 검색키
## traderie_kor.json : 트레더리 한글이름 , 검색키
## item-names.json: Diablo2 게임 패키지 내에 있는 아이템명 ( 한영 포함 )
## item-modifiers.json : Diablo2 게임 패키지 내에 있는 옵션명 ( 한영 포함 )
## modifyOption.json : 수집간 강제 변경할 문구 
