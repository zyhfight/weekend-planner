"""
高德地图 POI 服务
"""
import os
import requests
from typing import List, Optional, Dict, Any


AMAP_KEY = os.getenv("AMAP_KEY", "")  # 高德 API Key


def search_poi(
    keywords: str,
    city: str = "杭州",
    district: Optional[str] = None,
    types: Optional[str] = None,
    offset: int = 20,
    page: int = 1,
) -> List[Dict[str, Any]]:
    """
    搜索 POI 信息
    文档: https://lbs.amap.com/api/webservice/guide/api/search
    """
    if not AMAP_KEY:
        return []

    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": AMAP_KEY,
        "keywords": keywords,
        "city": city,
        "offset": str(offset),
        "page": str(page),
        "extensions": "all",  # 返回详细信息
        "output": "json",
    }
    if district:
        params["citylimit"] = "true"
    if types:
        params["types"] = types

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") == "1":
            return data.get("pois", [])
    except Exception as e:
        print(f"[高德API] 搜索失败: {e}")
    return []


def get_weather(city: str = "杭州") -> Dict[str, Any]:
    """
    获取实时天气
    文档: https://lbs.amap.com/api/webservice/guide/api/weatherinfo
    """
    if not AMAP_KEY:
        return {"weather": "未知", "temperature": "", "wind": ""}

    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": AMAP_KEY,
        "city": city,
        "extensions": "base",  # base=实时天气 all=预报
        "output": "json",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") == "1" and data.get("lives"):
            live = data["lives"][0]
            return {
                "weather": live.get("weather", ""),
                "temperature": live.get("temperature", ""),
                "wind": live.get("winddirection", "") + "风" + live.get("windpower", ""),
                "humidity": live.get("humidity", ""),
                "report_time": live.get("reporttime", ""),
            }
    except Exception as e:
        print(f"[高德API] 天气查询失败: {e}")
    return {"weather": "未知", "temperature": ""}
