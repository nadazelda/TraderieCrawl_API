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
        print("▶ 옵션 크롤 시작")
        TraOptionCrawl("", "")

        print("▶ 유니크 아이템 크롤 시작")
        TraUniqueCrawl("", "")

        print("▶ 일반 아이템 크롤 시작")
        TraBaseItemCrawl("", "")

        print("▶ 아이템 이름 매핑")
        ItemName()

        print("▶ 옵션 한글 매핑")
        ItemOption()

        print("▶ 유니크 옵션 ID/한글 매핑")
        CrawlerResult()

        print("▶ 룬워드 관련 수집")
        TraRunWordsCrawl()
        ItemNameRunWords()
        CrawlResultRunWords()
         print("▶ 유투브 관련 수집")
        CrawlYoutube()

        finalize_crawl_result()
    except Exception as e:
        print(f"❌ 크롤러 오류: {e}") 
