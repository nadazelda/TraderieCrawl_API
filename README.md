
트레더리 Diablo2 아이템 일괄 검색 시스템의 전체 아키텍처입니다.

- **Frontend**  
  - GitHub Pages에서 호스팅  
  - `index.html`, `script.js`, `config.js` 구성  
  - 사용자 입력 → FastAPI로 API 요청

- **API Base URL**  
  - `config.js`에서 설정  
  - Cloudflare Tunnel을 통해 FastAPI에 안전하게 연결

- **FastAPI**  
  - `/app/main.py`  
  - `/ItemList`, `/MakeTraderieUrl` 등 API 제공  
  - 크롤링 트리거(`/crawl/*`) 호출 가능

- **크롤러 (Selenium 기반)**  
  - `/crawler/*.py`  
  - 옵션/룬워드/기초 아이템 등 웹에서 직접 크롤링  
  - 결과는 `/crawlResult/*.json`에 저장됨

- **Docker 컨테이너 구성**  
  - `fastapi`, `crawler`, `cloudflared`로 분리  
  - `docker-compose.yml`에서 볼륨(`/crawlResult`) 공유

---

### 📘 시스템 흐름도






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


## CloudFlare 관련
   - docker-compose.yml로 빌드전 개인적으로 ec2 서버에 최초 한번 실행인증을 해야한다
   - cloudflared 설치 (도커 밖에서)
      curl -LO https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
      chmod +x cloudflared-linux-amd64
      sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
   - Cloudflare 계정 로그인 및 터널 생성
   	cloudflared tunnel login
   - 인증서 생성 후 명령어로 터널생성
   	cloudflared tunnel create my-fastapi-tunnel
   - 승인파일 경로 
   	/home/ec2-user/.cloudflared/cert.pem
   - 해당 경로에 권한도 
   	chmod 644 /home/ec2-user/.cloudflared/하위 파일들 
   - 해당 폴더 권한도
   	chmod 755 /home/ec2-user/.cloudflared
   - 이후 quick tunnel로 구성해서 진행 

## 이슈.
1. 외부 http/https 접속접근을 위해 어떤방식을 채택할 것인가?
   - EC2 서버 Docker 를 그대로 접근해도 되지만 공개하기위해선 ip노출을 막기위해 도메인 서비스가 필요함
   - github page는 private repository를 서비스하기위해선 유료로 해야하기 때문에 도메인서비스 사용하기로 결정
   - NGROK
      ngrok의 경우 무료로 사용할수 있고, 로컬 테스트할땐 크게 문제되지 않는다. 단 배포서비스로 사용하기엔 부적합하다 
      최초 접근시 사용자 인증페이지 통과가 필요해 부적합하다 
   - CORS
      Fast api의 기능 중 지정된 url에서의 요청만 허용하는 정책기능, 별도의 비용 발생 x
      단일 HTTP 서비스, Github page는 반드시 https 서비스 제공을 해야하기 때문에 http 불가능
   - NGINX 
      SSL 인증을 발급해야하는데 GITHUB PAGE는 불가능
   
   ** Cloudflare + Github Pages + fastApi 구성채택 **




     
