import json, requests

class CrawlYoutube:
    API_KEY = ""  # 🔑 유튜브 API 키
    
    CHANNEL_ID = ""    # 📺 대상 채널 ID

    def __init__(self) -> None:
        self.make_uploads_playListJson()  #
        
    def get_uploads_playlist_id(self):
        url = f"https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "contentDetails",
            "id": self.CHANNEL_ID,
            "key": self.API_KEY
        }
        res = requests.get(url, params=params).json()
        return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def get_all_video_metadata(self,playlist_id, max_results=50):
        url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": max_results,
            "key":  self.API_KEY
        }
        results = []
        while True:
            res = requests.get(url, params=params).json()

            for item in res.get("items", []):
                snippet = item["snippet"]
                video_id = snippet["resourceId"]["videoId"]
                title = snippet["title"]
                published_at = snippet["publishedAt"]
                results.append({
                    "videoId": video_id,
                    "title": title,
                    "publishedAt": published_at
                })

            if "nextPageToken" not in res:
                break
            params["pageToken"] = res["nextPageToken"]
        return results
    
    def make_uploads_playListJson(self):
        uploads_playlist_id = self.get_uploads_playlist_id()
        videos = self.get_all_video_metadata(uploads_playlist_id)

        print("총 영상 수:", len(videos))
        print("예시:", videos[:2])  # 일부 출력 확인

        with open("crawlResult/youtube_videos.json", "w", encoding="utf-8") as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)

