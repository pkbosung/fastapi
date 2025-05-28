import requests

YOUTUBE_API_KEY = ""

def fetch_washing_info(keywords):
    search_results = []
    for keyword in keywords:
        try:
            url = f"https://www.google.com/search?q={keyword}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                search_results.append({"title": f"{keyword} 정보 보기", "url": url})
        except:
            continue
    return search_results

def fetch_youtube_videos(keywords, max_results=3):
    search_query = keywords[0]
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": search_query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video",
        "regionCode": "KR",
    }
    response = requests.get(url, params=params)
    videos = []
    if response.status_code == 200:
        for item in response.json().get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            videos.append({"title": title, "url": f"https://youtu.be/{video_id}"})
    return videos
