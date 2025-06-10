from datetime import datetime
from fastapi import APIRouter,HTTPException,FastAPI
from fastapi.responses import JSONResponse
from fastapi import Query  # 상단에 추가 필요
import asyncio,logging,random
from fastapi.middleware.cors import CORSMiddleware
from middleware.log_middleware import LoggingMiddleware
from collections import Counter
import json , os,re, glob
from schemas.item import ItemRequest,ItemListRequest
from services.url_builder import TraderieUrlBuilder
from app.kind_map import kind_map  # 같은 폴더에 있으면 이렇게 import
from services.Crawler import Crawler  # 필요 시 상단으로 옮겨도 됨
from services.notifier import start_scheduler

# ✅ FastAPI 앱 인스턴스 생성
app = FastAPI()
router = APIRouter()

# 서버 관리 로그를 위해 미들웨어 로그 서비스 등록
# 로그 관련이기 때문에 가장먼저 등록한다. 
app.add_middleware(LoggingMiddleware)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000","https://diuno88.github.io"],  # 또는 ["http://localhost:8000"] 만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 필터 정의 healthchekd 로그는 제외시킴 
class IgnorePingFilter(logging.Filter):
    def filter(self, record):
        return '/ping' not in record.getMessage()

# Uvicorn access log에 필터 적용
logging.getLogger("uvicorn.access").addFilter(IgnorePingFilter())

@router.get("/ping")
def ping():
    return {"status": "ok"}
    
@router.post("/MakeTraderieUrl")
async def make_urls(payload: ItemRequest):
    try:
        payload_dict = payload.dict()  # ✅ 공통 dict 변환

        if payload_dict.get("items"):  # ✅ 다중 아이템 요청 처리
            results = []

            for item in payload_dict["items"]:
                builder = TraderieUrlBuilder(item_key=item["itemKey"])
                builder.set_common_props(
                    ladder=payload_dict["prop_Ladder"],
                    mode=payload_dict["prop_Mode"],
                    ethereal=payload_dict["prop_Ethereal"]
                )
                builder.set_options(payload_dict.get("options", []))

                # ✅ 글로벌 옵션만 추출해서 전달
                global_props = {
                    k: v for k, v in payload_dict.items()
                    if k.startswith("prop_") and k not in {"prop_Ladder", "prop_Mode", "prop_Ethereal"}
                }
                print("🧪 global_props 확인:", global_props)
                builder.set_global_props(global_props)

                base_url = builder.get_base_url()
                real_url = builder.get_real_url()


                def run_crawler():
                    crawler = Crawler()
                    try:
                        return crawler.get_listing_summary(base_url)
                    finally:
                        crawler.Exit()

                loop = asyncio.get_event_loop()
                crawl_result = await loop.run_in_executor(None, run_crawler)

                results.append({
                    "itemKey": item["itemKey"],
                    "base_url": base_url,
                    "real_url": real_url,
                    "listings": crawl_result["listings"]
                    
                })
                

            return {"results": results}

        else:  # ✅ 단일 아이템 처리
            builder = TraderieUrlBuilder(item_key=payload_dict["ItemKey"])
            builder.set_common_props(
                ladder=payload_dict["prop_Ladder"],
                mode=payload_dict["prop_Mode"],
                ethereal=payload_dict["prop_Ethereal"]
            )
            builder.set_options(payload_dict.get("Options", []))

            global_props = {
                k: v for k, v in payload_dict.items()
                if k.startswith("prop_") and k not in {"prop_Ladder", "prop_Mode", "prop_Ethereal"}
            }
            
            print("🧪 global_props 확인:", global_props)
            builder.set_global_props(global_props)

            if payload_dict.get("prop_Rarity"):
                builder.set_rarity(payload_dict["prop_Rarity"])

            base_url = builder.get_base_url()
            real_url = builder.get_real_url()

            def run_crawler():
                crawler = Crawler()
                try:
                    return crawler.get_listing_summary(base_url)
                finally:
                    crawler.Exit()

            loop = asyncio.get_event_loop()
            crawl_result = await loop.run_in_executor(None, run_crawler)

            return {
                "base_url": base_url,
                "real_url": real_url,
                "listings": crawl_result["listings"]
                
            }

    except Exception as e:
        print(f"❌ make_urls 내부 오류 발생: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    except asyncio.TimeoutError:
        return JSONResponse(status_code=504, content={"error": "⏱️ 크롤링 시간 초과"})



    
@router.get("/selectCategories")
async def select_categories(
    kind: str = Query(..., description="아이템 종류"),
    ctg: str = Query(..., description="카테고리 키")
):
    kind_key = kind.lower()
    if kind_key not in kind_map or kind_map[kind_key]["json_file"] is None:
        raise HTTPException(status_code=400, detail="유효하지 않은 kind입니다.")

    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_path, kind_map[kind_key]["json_file"])

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        if kind_key == "runwords":
            # type 리스트 안에 ctg가 포함되어 있는 경우만 필터링
            filtered_items = [item for item in data if ctg in item.get("type", [])]
        else:
            filtered_items = [item for item in data if item.get("ctg") == ctg]

        return {"items": filtered_items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카테고리 필터 실패: {e}")


@router.get("/ItemKinds")
async def item_kinds():

    with open("CrawlResult/youtube_videos.json", "r", encoding="utf-8") as f:
        videos = json.load(f)

    if videos:
        random_video = random.choice(videos)
        
    kinds = [{"key": k, "name": v} for k, v in kind_map.items()]
    return {"kinds": kinds, "random_video":random_video}



@router.post("/ItemList")
async def item_list(req: ItemListRequest):

    kind_key = req.kind.lower()
    if kind_key not in kind_map or kind_map[kind_key]["json_file"] is None:
        return {"items": []}

    base_path = "/app/CrawlResult"
    json_path = os.path.join(base_path, kind_map[kind_key]["json_file"])
    ctg_json_path = os.path.join(base_path, "..", "jsons", "item-category.json")
    
    print('base_path===',base_path)
    print('json_path===',json_path)
    print('ctg_json_path===',ctg_json_path)
        
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        with open(ctg_json_path, encoding="utf-8") as f:
            category = json.load(f)

        if kind_key == "unique":
            return {"items": data}
        elif kind_key == "runwords":
            #재료 카테고리 호출 
            base_item_path = os.path.join(base_path, "baseItemList.json")  # jsons가 아님
            with open(base_item_path, encoding="utf-8") as f:
                baseData = json.load(f)
                
            #룬워드에 붙을 스킬옵션들
            ## 룬워드 검색시 클래스 스킬옵션을 붙여서 검색하는걸 고려 
            skilloption_path = os.path.join(base_path, "optionCombo.json")  # jsons가 아님
            with open(skilloption_path, encoding="utf-8") as f:
                skilloption = json.load(f)
            # "to ~~~ (Class Only)" 형태 필터링
            pattern = re.compile(r'^to .+\(.*Only\)$', re.IGNORECASE)
            filtered = [opt for opt in skilloption if pattern.match(opt.get("name", ""))]
                
            data.sort(key=lambda x: x.get("korName", ""), reverse=False)    
            baseData.sort(key=lambda x: x.get("korName", ""), reverse=False)    
            filtered.sort(key=lambda x: x.get("koKR", ""), reverse=False)    
                       
            return {"items": data, "category":baseData, "options":filtered}
        else:
            print(' start rare material makgic Item ')
            base_item_path = os.path.join(base_path, "baseItemList.json")  # jsons가 아님
            with open(base_item_path, encoding="utf-8") as f:
                baseData = json.load(f)
                
            option_path = os.path.join(base_path, kind_map[kind_key]["option_file"])        
            print('option_path paht==',option_path)
            with open(option_path, encoding="utf-8") as f:
                optionData = json.load(f)
           
            # 정렬된 리스트로 변환
            with open("jsons/item-category.json", "r", encoding="utf-8") as f:
                 category = json.load(f)
            
            ctg_list = sorted(
                [{"eng": eng, "kor": val["kor"], "group": val["group"]} for eng, val in category.items()],
                key=lambda x: x["kor"]
            )
            print(" before return")
            data.sort(key=lambda x: x.get("korName", ""), reverse=False)    
            ctg_list.sort(key=lambda x: x.get("kor", ""), reverse=False)    
            optionData.sort(key=lambda x: x.get("koKR", ""), reverse=False)   
             
            return {"items": data, "options" : optionData,"categories": ctg_list}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 로드 실패: {e}")

#관리자 로그 페이지 
@router.get("/logs/inspect")
async def inspect_logs(date: str = None, suspicious_only: bool = False):
    pattern = f"logs/server_log_{date}.jsonl" if date else "logs/server_log_*.jsonl"
    files = sorted(glob.glob(pattern))
    logs = []
    for file in files:
        with open(file, encoding="utf-8") as f:
            for line in f:
                log = json.loads(line)
                if suspicious_only and not log.get("suspicious"):
                    continue
                logs.append(log)
    return JSONResponse(content=logs[-200:])


@router.get("/logs/stats")
async def get_log_stats(date: str = None):
    today = date or datetime.utcnow().strftime("%Y-%m-%d")
    file_path = f"logs/server_log_{today}.jsonl"

    suspicious_count = 0
    total_count = 0
    reasons = Counter()
    methods = Counter()
    paths = Counter()
    ips = Counter()
    unique_ips = set()

    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                log = json.loads(line)
                total_count += 1
                methods[log["method"]] += 1
                paths[log["path"]] += 1
                ip = log["ip"]
                unique_ips.add(ip)
                ips[ip] += 1
                if log.get("suspicious"):
                    suspicious_count += 1
                    if "reason" in log:
                        reasons[log["reason"]] += 1
    except FileNotFoundError:
        return JSONResponse(content={"message": "해당 날짜 로그 없음"}, status_code=404)

    return {
        "date": today,
        "total_requests": total_count,
        "unique_users": len(unique_ips),
        "top_ips": ips.most_common(5),
        "suspicious_requests": suspicious_count,
        "methods": methods,
        "top_paths": paths.most_common(5),
        "suspicious_reasons": reasons.most_common()
    }


start_scheduler()
app.include_router(router)