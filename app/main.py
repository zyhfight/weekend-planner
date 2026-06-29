"""
FastAPI 主服务 - 周末去哪玩专家
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid

from app.models.schemas import (
    ChatRequest, ChatResponse, UserIntent, Recommendation,
)
from app.services.dialogue import parse_intent_from_text, generate_bot_reply, should_generate_recommendation
from app.services.recommendation import recommend, blind_box_recommend
from app.services.amap_service import get_weather

# 会话存储（MVP 用内存，生产环境用 Redis）
sessions: dict = {}

app = FastAPI(title="周末去哪玩专家 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return FileResponse("/workspace/weekend-planner/static/index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    核心对话接口
    - 解析用户输入
    - 更新用户意图
    - 生成推荐（条件满足时）
    - 返回机器人回复
    """
    session_id = request.session_id or str(uuid.uuid4())

    # 获取或创建会话
    if session_id not in sessions:
        sessions[session_id] = {
            "intent": UserIntent(),
            "history": [],
            "last_recommendations": [],
        }

    session = sessions[session_id]
    intent: UserIntent = session["intent"]

    # 合并已有意图（前端可能直接传 intent）
    if request.intent:
        for field, value in request.intent.model_dump(exclude_none=True).items():
            setattr(intent, field, value)

    user_msg = request.message.strip()

    # 解析用户输入，更新意图
    intent = parse_intent_from_text(user_msg, intent)
    session["intent"] = intent
    session["history"].append({"role": "user", "content": user_msg})

    # 判断是否需要生成推荐
    is_blind_box = "盲盒" in user_msg or "随机" in user_msg
    should_recommend = should_generate_recommendation(intent) and (
        is_blind_box
        or any(kw in user_msg for kw in ["帮我找", "推荐", "去哪", "地方", "好的", "确认", "开始", "可以"])
        or (len(session["history"]) >= 2 and intent.preferences)  # 两轮对话后且有偏好就推荐
    )

    recommendations = None
    if should_recommend:
        # 获取天气信息
        weather_info = get_weather(intent.city)

        if is_blind_box:
            rec = blind_box_recommend(intent, weather_info)
            recommendations = [rec] if rec else []
        else:
            recommendations = recommend(intent, weather_info)

        session["last_recommendations"] = recommendations or []

    # 生成机器人回复
    bot_result = generate_bot_reply(user_msg, intent, recommendations)
    session["history"].append({
        "role": "assistant",
        "content": bot_result["message"],
        "recommendations": [r.model_dump() for r in recommendations] if recommendations else None,
    })

    return ChatResponse(
        message=bot_result["message"],
        intent=intent,
        recommendations=recommendations,
        ask_for=bot_result.get("ask_for"),
    )


@app.get("/api/weather")
async def weather(city: str = "杭州"):
    """获取天气信息"""
    return get_weather(city)


@app.get("/api/recommend")
async def get_recommendations(
    district: str = "",
    group_size: int = 1,
    budget: int = 500,
    preferences: str = "",
):
    """直接获取推荐（REST 风格，供非对话场景使用）"""
    prefs = [p.strip() for p in preferences.split(",") if p.strip()]
    intent = UserIntent(
        district=district or None,
        group_size=group_size,
        budget=budget,
        preferences=prefs,
    )
    weather_info = get_weather()
    results = recommend(intent, weather_info)
    return {"recommendations": results}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "周末去哪玩专家"}


# 挂载静态文件
app.mount("/static", StaticFiles(directory="/workspace/weekend-planner/static"), name="static")
