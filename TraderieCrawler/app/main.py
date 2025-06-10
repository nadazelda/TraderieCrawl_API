# main.py
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
from crawler_logger import log_crawler_event
import shutil, os

def finalize_crawl_result():
    src_dir = "crawlResult"
    dst_dir = "/app/CrawlResult"  # 공유 디렉토리
    for filename in os.listdir(src_dir):
        if filename.endswith(".json"):
            shutil.copy2(os.path.join(src_dir, filename), os.path.join(dst_dir, filename))
    print("✅ 크롤링 결과가 공유 폴더로 복사되었습니다.")

def run_all_crawlers():
    try:
        log_crawler_event("start", "전체 크롤러 시작", notify=True)

        log_crawler_event("info", "옵션 크롤 시작", notify=True)
        TraOptionCrawl("", "")

        log_crawler_event("info", "유니크 아이템 크롤 시작", notify=True)
        TraUniqueCrawl("", "")

        log_crawler_event("info", "일반 아이템 크롤 시작", notify=True)
        TraBaseItemCrawl("", "")

        log_crawler_event("info", "아이템 이름 매핑")
        ItemName()

        log_crawler_event("info", "옵션 한글 매핑")
        ItemOption()

        log_crawler_event("info", "유니크 옵션 ID/한글 매핑")
        CrawlerResult()

        log_crawler_event("info", "룬워드 관련 수집", notify=True)
        TraRunWordsCrawl()
        ItemNameRunWords()
        CrawlResultRunWords()

        log_crawler_event("info", "유투브 관련 수집", notify=True)
        CrawlYoutube()

        finalize_crawl_result()
        log_crawler_event("end", "전체 크롤러 완료", notify=True)
    except Exception as e:
        log_crawler_event("error", "크롤러 실행 중 오류 발생", {"error": str(e)})
        print(f"❌ 크롤러 오류: {e}")
