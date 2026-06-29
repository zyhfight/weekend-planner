"""
推荐引擎 - 基于用户意图 + POI 数据生成推荐
"""
import random
from typing import List, Dict, Any, Optional
from app.models.schemas import UserIntent, Recommendation, Location, BudgetBreakdown

# 杭州热门地点知识库（POI API 不可用时的 fallback）
# 实际生产环境应全部通过 API 获取
HANGZHOU_POIS = [
    {
        "id": "poi_001", "name": "西湖风景名胜区", "district": "西湖区",
        "tags": ["户外自然", "拍照打卡", "安静放空"],
        "location": {"lng": 120.1485, "lat": 30.2425},
        "ticket": 0, "transport_cost": 20, "food_cost": 80,
        "best_time": "全天，傍晚最佳", "duration": "半天-一天",
        "tips": ["周末人较多，建议早去", "苏堤白堤适合散步拍照", "雷峰塔可俯瞰全景"],
        "weather": "晴天最佳，雨天别有一番韵味",
    },
    {
        "id": "poi_002", "name": "中国美术学院（象山校区）", "district": "西湖区",
        "tags": ["文艺打卡", "拍照打卡", "安静放空"],
        "location": {"lng": 120.0830, "lat": 30.1942},
        "ticket": 0, "transport_cost": 20, "food_cost": 60,
        "best_time": "下午2-6点（光线适合拍照）", "duration": "3-4小时",
        "tips": ["校园建筑极具设计感", "转塘小吃街就在附近", "部分区域需预约"],
        "weather": "晴天最佳",
    },
    {
        "id": "poi_003", "name": "良渚文化村", "district": "余杭区",
        "tags": ["文艺打卡", "户外自然", "遛娃友好"],
        "location": {"lng": 119.9753, "lat": 30.2942},
        "ticket": 0, "transport_cost": 30, "food_cost": 100,
        "best_time": "全天", "duration": "一天",
        "tips": ["良渚博物院需预约", "美丽洲公园适合散步", "有很多文艺小店"],
        "weather": "晴天最佳，室外区域大",
    },
    {
        "id": "poi_004", "name": "小河直街历史文化街区", "district": "拱墅区",
        "tags": ["文艺打卡", "美食探店", "拍照打卡"],
        "location": {"lng": 120.1398, "lat": 30.2944},
        "ticket": 0, "transport_cost": 15, "food_cost": 120,
        "best_time": "下午-晚上", "duration": "3-5小时",
        "tips": ["有很多独立咖啡馆", "适合慢慢逛吃", "比河坊街安静很多"],
        "weather": "晴天雨天都适合",
    },
    {
        "id": "poi_005", "name": "九溪烟树", "district": "西湖区",
        "tags": ["户外自然", "拍照打卡", "运动冒险"],
        "location": {"lng": 120.1667, "lat": 30.2044},
        "ticket": 0, "transport_cost": 20, "food_cost": 60,
        "best_time": "上午9-11点", "duration": "3-4小时",
        "tips": ["溪水清凉，夏天可以踩水", "穿防滑鞋", "带好驱蚊水"],
        "weather": "晴天最佳",
    },
    {
        "id": "poi_006", "name": "浙江省博物馆（孤山馆区）", "district": "西湖区",
        "tags": ["文艺打卡", "安静放空", "遛娃友好"],
        "location": {"lng": 120.1478, "lat": 30.2514},
        "ticket": 0, "transport_cost": 20, "food_cost": 80,
        "best_time": "上午9-11点", "duration": "2-3小时",
        "tips": ["免费需预约", "带身份证", "馆内有咖啡厅可以休息"],
        "weather": "雨天也完全适合",
    },
    {
        "id": "poi_007", "name": "富义仓艺术中心", "district": "拱墅区",
        "tags": ["文艺打卡", "拍照打卡", "安静放空"],
        "location": {"lng": 120.1523, "lat": 30.2978},
        "ticket": 0, "transport_cost": 15, "food_cost": 100,
        "best_time": "下午", "duration": "2-3小时",
        "tips": ["京杭大运河边", "工业风拍照很出片", "附近有大兜路历史街区"],
        "weather": "晴天雨天都适合",
    },
    {
        "id": "poi_008", "name": "龙井村", "district": "西湖区",
        "tags": ["户外自然", "美食探店", "拍照打卡"],
        "location": {"lng": 120.1300, "lat": 30.2178},
        "ticket": 0, "transport_cost": 25, "food_cost": 150,
        "best_time": "上午10点-下午4点", "duration": "半天",
        "tips": ["真正的龙井茶产地", "可以体验采茶（春季）", "农家菜值得一试"],
        "weather": "晴天最佳",
    },
    {
        "id": "poi_009", "name": "杭州万象城", "district": "上城区",
        "tags": ["美食探店", "遛娃友好"],
        "location": {"lng": 120.2100, "lat": 30.2489},
        "ticket": 0, "transport_cost": 15, "food_cost": 200,
        "best_time": "全天", "duration": "半天",
        "tips": ["购物美食一站式", "有亲子设施", "停车方便"],
        "weather": "雨天也完全适合",
    },
    {
        "id": "poi_010", "name": "西溪国家湿地公园", "district": "西湖区",
        "tags": ["户外自然", "拍照打卡", "安静放空"],
        "location": {"lng": 120.0836, "lat": 30.2697},
        "ticket": 80, "transport_cost": 20, "food_cost": 100,
        "best_time": "上午8-11点", "duration": "半天-一天",
        "tips": ["门票80元，提前网购有优惠", "摇橹船体验很值得", "秋天芦苇最美"],
        "weather": "晴天最佳，四季各有特色",
    },
    {
        "id": "poi_011", "name": "馒头山社区", "district": "上城区",
        "tags": ["文艺打卡", "拍照打卡", "美食探店"],
        "location": {"lng": 120.1689, "lat": 30.2311},
        "ticket": 0, "transport_cost": 15, "food_cost": 60,
        "best_time": "上午10点-下午3点", "duration": "2-3小时",
        "tips": ["杭州最有烟火气的老社区", "有很多网红咖啡馆", "离南宋御街很近"],
        "weather": "晴天最佳",
    },
    {
        "id": "poi_012", "name": "径山寺", "district": "余杭区",
        "tags": ["户外自然", "安静放空", "运动冒险"],
        "location": {"lng": 119.8833, "lat": 30.3833},
        "ticket": 30, "transport_cost": 40, "food_cost": 50,
        "best_time": "上午8-12点", "duration": "半天",
        "tips": ["需要爬山，穿运动鞋", "寺内素斋很有名", "可以俯瞰杭州城景"],
        "weather": "晴天最佳，雨天路滑注意安全",
    },
]


def calc_match_score(poi: Dict, intent: UserIntent) -> int:
    """计算 POI 与用户意图的匹配度（0-100）"""
    score = 0

    # 偏好标签匹配（最高60分）
    if intent.preferences:
        matched = sum(1 for tag in intent.preferences if tag in poi["tags"])
        score += min(60, matched * 20)
    else:
        score += 30  # 无偏好时给基础分

    # 区域匹配（20分）
    if intent.district and poi["district"] == intent.district:
        score += 20
    elif not intent.district:
        score += 10

    # 预算匹配（20分）
    total_cost = poi["ticket"] + poi["transport_cost"] + poi["food_cost"]
    if total_cost <= intent.budget:
        score += 20
    elif total_cost <= intent.budget * 1.2:
        score += 10

    return min(100, score)


def get_weather_bonus(poi: Dict, weather: str) -> str:
    """根据天气给出适配说明"""
    poi_weather = poi.get("weather", "")
    if "雨天" in poi_weather and "雨" in weather:
        return "☔ 今天有雨，这里是室内/避雨好去处"
    if "晴天" in poi_weather and "晴" in weather:
        return "☀️ 今天天气晴好，非常适合去这里"
    if "都适合" in poi_weather:
        return "🌤️ 今天无论什么天气都适合"
    return f"🌡️ 天气适配：{poi_weather}"


def generate_reason(poi: Dict, intent: UserIntent) -> str:
    """生成推荐理由"""
    reasons = []
    tags = poi["tags"]

    if intent.preferences:
        matched_tags = [t for t in intent.preferences if t in tags]
        if matched_tags:
            reasons.append(f"符合你{'、'.join(matched_tags)}的需求")

    if intent.group_size >= 3:
        reasons.append("空间宽敞，适合多人出行")
    elif intent.group_size == 2:
        reasons.append("很适合两人同行")

    budget_total = poi["ticket"] + poi["transport_cost"] + poi["food_cost"]
    if budget_total <= intent.budget:
        reasons.append(f"预计花费¥{budget_total}，在您的预算范围内")

    if not reasons:
        reasons.append("综合评分较高，值得一去")
    return "；".join(reasons)


def recommend(intent: UserIntent, weather_info: Dict = None, mode: str = "normal") -> List[Recommendation]:
    """
    核心推荐函数
    mode: "normal" | "blind_box"
    """
    pois = HANGZHOU_POIS

    # 计算匹配度
    scored = []
    for poi in pois:
        score = calc_match_score(poi, intent)
        scored.append((poi, score))

    # 排序
    scored.sort(key=lambda x: x[1], reverse=True)

    # 盲盒模式：随机选择前50%中的一个
    if mode == "blind_box" and scored:
        top_half = scored[:max(3, len(scored) // 2)]
        chosen = random.choice(top_half)
        scored = [chosen]

    # 取前5个
    top_n = scored[:5] if mode == "normal" else [scored[0]]

    # 构建推荐结果
    results = []
    for poi, score in top_n:
        total = poi["ticket"] + poi["transport_cost"] + poi["food_cost"]
        rec = Recommendation(
            id=poi["id"],
            name=poi["name"],
            address=f"{poi['district']}，杭州",
            location=Location(**poi["location"]),
            match_score=score,
            reason=generate_reason(poi, intent),
            budget_breakdown=BudgetBreakdown(
                ticket=poi["ticket"],
                transport=poi["transport_cost"],
                food=poi["food_cost"],
                total=total,
            ),
            transport_guide=_gen_transport_guide(poi),
            best_time=poi["best_time"],
            tips=poi["tips"],
            weather_suitability=get_weather_bonus(poi, weather_info.get("weather", "") if weather_info else ""),
            tags=poi["tags"],
        )
        results.append(rec)

    return results


def _gen_transport_guide(poi: Dict) -> str:
    """生成交通指引（简化版，实际应调用路线规划 API）"""
    name = poi["name"]
    district = poi["district"]
    guides = {
        "西湖区": "建议地铁1号线/2号线换乘公交，或骑行前往",
        "上城区": "地铁1号线/4号线可达，出站后步行或打车",
        "拱墅区": "地铁5号线可达，市区推荐骑行或公交",
        "滨江区": "地铁1号线可达，从市中心约30分钟",
        "余杭区": "地铁2号线/5号线换乘公交，建议预留1小时路程",
    }
    return guides.get(district, "建议使用地图导航前往")


# 盲盒模式
def blind_box_recommend(intent: UserIntent, weather_info: Dict = None) -> Recommendation:
    """盲盒推荐：随机选一个高匹配度地点"""
    results = recommend(intent, weather_info, mode="blind_box")
    return results[0] if results else None
