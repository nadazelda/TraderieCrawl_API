<div align="center">

### Read Me 🖍️

</div> 

## 📝 소개
디아블로2 트레더리 사이트에서 특정 아이템만 골라보기 편하게 만든 스크랩 소스입니다 

<br />

### 소스 구성
- Crawler.py
    - ChromDriver.py + paramJson.json을 조합하여 selenium으로 스크랩
	- 실제 작업을 수행하는 메인소스 

- main.py
	- 프로그램 실행 시작점 

- ChromDriver.py
	- selenium으로 사용할 크롬 설치 및 크롤링 함수정의 클래스 
	
- paramJson.json
	- url 파라미터로 사용할 데이터셋 

<br />

## ⚙ 기술 스택
> skills 폴더에 있는 아이콘을 이용할 수 있습니다.
### Front-end
	- python, json 
### Infra
	- Ec2 Linux Server
### Tools
	- python, selenium
<br />

## ⚙ 사용방법 
	
	- 재료, 유니크, 룬워드 등은 모두 특정 item id를 가지고 있습니다
	- 옵션별 id도 별도로 존재합니다
	- paramJson.json에 Item id, option id 를 입력해 둡니다 
	- 예시) 트레더리에서 '페티쉬 트로피' 를 선택해서 옵션에 매직, 독과뼈3스킬, 뼈창3스킬을 선택하고 검색하면 상단 주소에 아래 값들을 볼 수 있습니다 
		https://traderie.com/diablo2resurrected/product/3902033381?prop_Ladder=true&prop_500Min=3&prop_756Min=3
		"3902033381?prop_Ladder=true&prop_500Min=3&prop_756Min=3" 이부분을 아래처럼 표현해둠 
		"item_name": "페티쉬 트로피",
		"item_id": "4103765265",
		"isLadder": "true",
		"rarity": "magic",
		"props": {
		  "prop_500Min": "3",
		  "prop_756Min": "3"
		}
		


<br />

## 🤔 기술적 이슈와 해결 과정

- chromedriver 버전관리
    - 최신 버전의 호환성 문제발생을 막기위해 특정버전으 크롬exe 설치파일을 사용 
	
- api 호출 관련 정보수집방법
    - 관리자 모드를 통해 xhr 의 api 서버 호출 url을 하나씩 테스트하며 수집
	- traderie 전체 api 호출 주소를 알아낼 방법은 없음 
	- 검색리스트 api base url : https://traderie.com/api/diablo2resurrected/listings
	- 실제 트레더리 url : https://traderie.com/diablo2resurrected/product/

- public ip 해결
    - nqrok를 활용해 ec2 서버에서 연결해준다 curl http://본인ec2주소 :4040/api/tunnels 
<br />



- ec2 서버 https 접근방식
	EC2 서버 Docker 를 그대로 접근해도 되지만 공개하기위해선 ip노출을 막기위해 도메인 서비스가 필요함
	github page는 private repository를 서비스하기위해선 유료로 해야하기 때문에 도메인서비스 사용하기로 결정

	대안1. NGROK
		ngrok의 경우 무료로 사용할수 있고, 로컬 테스트할땐 크게 문제되지 않는다.
		단 배포서비스로 사용하기엔 부적합하다 
		최초 접근시 사용자 인증페이지 통과가 필요해 부적합하다 

	대안2.CORS
		Fast api의 기능 중 지정된 url에서의 요청만 허용하는 정책기능
		별도의 비용 발생 x

	대안3. 단일 HTTP 서비스
		Github page는 반드시 https 서비스 제공을 해야하기 때문에 http 불가능
	대안4. NGINX 
		SSL 인증을 발급해야하는데 GITHUB PAGE는 불가능

결론 : Cloudflare + Github Pages + fastApi 구성채택
