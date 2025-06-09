from fastapi import APIRouter,HTTPException
from fastapi.responses import JSONResponse
from fastapi import Query  # 상단에 추가 필요
import logging,shutil,random
import  os
# 크롤링 관련 클래스들 import
from crawler.TraBaseItemCrawl import TraBaseItemCrawl
from crawler.TraOptionCrawl import TraOptionCrawl
from crawler.TraUniqueCrawl import TraUniqueCrawl
from crawler.ItemName import ItemName
from crawler.ItemOption import ItemOption
from crawler.CrawlResult import CrawlerResult
from crawler.TraRunWordsCrawl import TraRunWordsCrawl
from crawler.ItemNameRunWords import ItemNameRunWords
from crawler.CrawlResultRunWords import CrawlResultRunWords

from youtube.CrawlYoutube import CrawlYoutube
router = APIRouter()
# 필터 정의
class IgnorePingFilter(logging.Filter):
    def filter(self, record):
        return '/ping' not in record.getMessage()

# Uvicorn access log에 필터 적용
logging.getLogger("uvicorn.access").addFilter(IgnorePingFilter())
 
@router.get("/ping")
def ping():
    return {"status": "ok"}

@router.get("/crawl/unique")
async def crawlUnique(startKey: str = Query(...)):
    if startKey != "nadazelda":
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        # 2. 유니크 아이템 크롤
        print("▶ 유니크 아이템 크롤 시작")
        TraUniqueCrawl("", "")
        
        # 4. 아이템 한글 이름 매핑 + description 필터링 및 정제
        print("▶ 아이템 이름 매핑 및 설명 정제")
        ItemName()
         # 6. 유니크 아이템에 property_id, property_kor 매핑
        print("▶ 유니크 옵션 정제 및 ID/한글명 매핑")
        CrawlerResult()
        # ✅ 모든 크롤러가 정상 종료되면 결과 반영
        print("▶ 크롤러 파일복사완료")
        finalize_crawl_result()
        return JSONResponse(content={"message": "크롤링 완료"})

    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@router.get("/crawl/Itemoptions")
async def crawlItemoptions(startKey: str = Query(...)):
    if startKey != "nadazelda":
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        # 5. 옵션 한글 매핑
        print("▶ 옵션 한글 이름 매핑")
        ItemOption()
        # ✅ 모든 크롤러가 정상 종료되면 결과 반영
        print("▶ 크롤러 파일복사완료")
        finalize_crawl_result()
        
        return JSONResponse(content={"message": "크롤링 완료"})

    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})     
    
    
@router.get("/crawl/baseItem")
async def crawlbaseItem(startKey: str = Query(...)):
    if startKey != "nadazelda":
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        # 3. 재료/베이스 아이템 크롤
        print("▶ 일반 아이템(재료 등) 크롤 시작")
        TraBaseItemCrawl("", "")
        # ✅ 모든 크롤러가 정상 종료되면 결과 반영
        print("▶ 크롤러 파일복사완료")
        finalize_crawl_result()
        return JSONResponse(content={"message": "크롤링 완료"})
    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})   
    
      
@router.get("/crawl/runWords")
async def crawlrunWords(startKey: str = Query(...)):
    if startKey != "nadazelda":
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        ##룬워드 관련 수집시작 
        print("traderie 크롤링시작")
        TraRunWordsCrawl()
        print("이름명칭 매칭 시작")
        ItemNameRunWords()
        print("검색용 json 생성시작")
        CrawlResultRunWords()
        # ✅ 모든 크롤러가 정상 종료되면 결과 반영
        print("▶ 크롤러 파일복사완료")
        finalize_crawl_result()
        return JSONResponse(content={"message": "크롤링 완료"})
    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})     
    
    
    
@router.get("/crawl/startCrawlerAll")
async def start_crawler(startKey: str = Query(...)):
    if startKey != "nadazelda":
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        # 크롤링 시작 순서

        # 1. 옵션 정보부터 수집 (나중에 ID 매칭용)
        print("▶ 옵션 크롤 시작")
        TraOptionCrawl("", "")  # 로그인 필요 없음

        # 2. 유니크 아이템 크롤
        print("▶ 유니크 아이템 크롤 시작")
        TraUniqueCrawl("", "")

        # 3. 재료/베이스 아이템 크롤
        print("▶ 일반 아이템(재료 등) 크롤 시작")
        TraBaseItemCrawl("", "")

        # 4. 아이템 한글 이름 매핑 + description 필터링 및 정제
        print("▶ 아이템 이름 매핑 및 설명 정제")
        ItemName()

        # 5. 옵션 한글 매핑
        print("▶ 옵션 한글 이름 매핑")
        ItemOption()

        # 6. 유니크 아이템에 property_id, property_kor 매핑
        print("▶ 유니크 옵션 정제 및 ID/한글명 매핑")
        CrawlerResult()
        
        
        ##룬워드 관련 수집시작 
        TraRunWordsCrawl()
        ItemNameRunWords()
        CrawlResultRunWords()
        
        # ✅ 모든 크롤러가 정상 종료되면 결과 반영
        print("▶ 크롤러 파일복사완료")
        finalize_crawl_result()
       

        return JSONResponse(content={"message": "크롤링 완료"})
    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    

def finalize_crawl_result():
    src_dir = "crawlResult"
    dst_dir = "routes"
    for filename in os.listdir(src_dir):
        if filename.endswith(".json"):
            shutil.copy2(os.path.join(src_dir, filename), os.path.join(dst_dir, filename))
    print("✅ 크롤링 결과가 routes/로 복사되었습니다.")