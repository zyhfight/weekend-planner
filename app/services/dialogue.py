"""
LLM 对话理解模块
MVP 阶段使用规则解析，后续可接入 DeepSeek/Claude API
"""
import re
import json
from typing import Optional, Dict, Any, List
from app.models.schemas import UserIntent

# 偏好标签关键词映射
TAG_KEYWORDS = {
    "户外自然": ["户外", "自然", "风景", "爬山", " hiking", "公园", "湿地", "森林", "山", "湖", "江", "溪"],
    "文艺打卡": ["文艺", "打卡", "拍照", "展览", "博物馆", "美术馆", "设计", "建筑", "小众", "艺术"],
    "美食探店": ["美食", "吃", "餐厅", "探店", "小吃", "夜市", "火锅", "杭帮菜", "咖啡", "咖啡馆"],
    "遛娃友好": ["娃", "孩子", "亲子", "遛娃", "宝宝", "家庭", "儿童", "小孩"],
    "运动冒险": ["运动", "冒险", "刺激", "徒步", "骑行", "攀岩", "跑山"],
    "安静放空": ["安静", "放空", "发呆", "独处", "安静", "禅", "冥想", "看书", "咖啡"],
}

DISTRICT_KEYWORDS = {
    "西湖区": ["西湖区", "西湖", "转塘", "留下", "西溪"],
    "上城区": ["上城区", "上城", "湖滨", "武林", "吴山", "南宋御街"],
    "拱墅区": ["拱墅区", "拱墅", "小河", "大兜路", "运河"],
    "滨江区": ["滨江区", "滨江", "钱江新城"],
    "余杭区": ["余杭区", "余杭", "良渚", "未来科技城"],
}

TRANSPORT_MAP = {
    "地铁": ["地铁", "轨道交通"],
    "自驾": ["自驾", "开车", "停车"],
    "步行": ["步行", "走路", "散步"],
}

DURATION_MAP = {
    "半天": ["半天", "几小时"],
    "一天": ["一天", "一整天"],
    "两天": ["两天", "周末两天"],
}


def parse_intent_from_text(text: str, existing: Optional[UserIntent] = None) -> UserIntent:
    """
    从用户输入文本中解析用户意图
    MVP 使用规则解析，后续可替换为 LLM 调用
    """
    if existing is None:
        intent = UserIntent()
    else:
        intent = existing

    text_lower = text.lower()

    # 解析区域
    for district, keywords in DISTRICT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                intent.district = district
                break

    # 解析人数
    num_match = re.search(r"(\d+)\s*人|我\s*(\d+)|(\d+)\s*个", text)
    if num_match:
        num = next(g for g in num_match.groups() if g is not None)
        intent.group_size = int(num)

    # 解析预算
    budget_match = re.search(r"(\d+)\s*元|预算\s*(\d+)|(\d+)\s*块|¥\s*(\d+)|(\d+)\s*以内", text)
    if budget_match:
        num = next(g for g in budget_match.groups() if g is not None)
        intent.budget = int(num)
    elif "不差钱" in text or "不限" in text or "多少钱都行" in text:
        intent.budget = 99999

    # 解析偏好标签
    matched_tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                matched_tags.append(tag)
                break
    if matched_tags:
        # 合并，不重复
        all_tags = set(intent.preferences + matched_tags)
        intent.preferences = list(all_tags)

    # 解析交通方式
    for transport, keywords in TRANSPORT_MAP.items():
        for kw in keywords:
            if kw in text:
                intent.transport = transport
                break

    # 解析时长
    for duration, keywords in DURATION_MAP.items():
        for kw in keywords:
            if kw in text:
                intent.duration = duration
                break

    # 解析宠物
    if any(kw in text for kw in ["宠物", "狗", "猫", "带宠物", "遛狗"]):
        intent.has_pet = True

    # 解析特殊需求
    if "生日" in text:
        intent.special_needs = "生日庆祝"
    elif "约会" in text or "表白" in text:
        intent.special_needs = "浪漫约会"

    return intent


def get_missing_fields(intent: UserIntent) -> List[str]:
    """检查还需要收集哪些信息"""
    missing = []
    if not intent.district and not intent.preferences:
        missing.append("preferences")
    if intent.group_size == 1 and "solo" not in " ".join(intent.preferences):
        pass  # 1人也可以，不强制
    return missing


def should_generate_recommendation(intent: UserIntent) -> bool:
    """判断是否有足够信息生成推荐"""
    # 至少有偏好信息或区域信息就可以推荐
    return bool(intent.preferences or intent.district)


def generate_bot_reply(user_message: str, intent: UserIntent, recommendations: list = None) -> Dict[str, Any]:
    """
    生成机器人回复
    返回：{ "message": str, "ask_for": list }
    """
    msg = user_message.lower()

    # 盲盒模式
    if "盲盒" in user_message or "随机" in user_message:
        return {
            "message": "🎲 好的，给你来个盲盒推荐！正在随机抽取一个高匹配度的好地方...",
            "ask_for": [],
        }

    # 追问场景
    if recommendations and any(kw in msg for kw in ["这个", "第一个", "第", "详细", "怎么说", "为什么"]):
        return {
            "message": f"关于「{recommendations[0].name if recommendations else '这个地方'}」，有什么想具体了解的？我可以告诉你交通、花费、注意事项等详细信息 😊",
            "ask_for": [],
        }

    # 修改条件
    if any(kw in msg for kw in ["换个", "不要", "重新", "不喜欢", "太远", "太贵", "太晒", "太累"]):
        return {
            "message": "好的，我重新帮你筛选一下～ 有没有特别想调整的？比如区域、预算、或者类型？",
            "ask_for": [],
        }

    # 初始引导
    if intent.group_size == 1 and not intent.preferences and not intent.district:
        return {
            "message": (
                "嗨！我是你的**周末去哪玩专家** 🎯\n\n"
                "先确认几个关键信息，1分钟搞定：\n\n"
                "① **活动区域？**\n"
                "　西湖区 / 上城区 / 拱墅区 / 滨江区 / 余杭区 / 不限\n\n"
                "② **几个人？**\n"
                "　1人 / 2人 / 3-4人 / 5人以上\n\n"
                "③ **总预算大概多少？**\n"
                "　200以内 / 200-500 / 500-1000 / 不差钱\n\n"
                "④ **偏好类型？**（可多选）\n"
                "　户外自然 / 文艺打卡 / 美食探店 / 遛娃友好 / 安静放空\n\n"
                "也可以直接告诉我你的想法，比如「西湖区，2个人，500以内，想要文艺+美食」"
            ),
            "ask_for": ["district", "group_size", "budget", "preferences"],
        }

    # 有推荐结果后的跟进
    if recommendations:
        return {
            "message": (
                f"以上 {len(recommendations)} 个地方，有感兴趣的吗？\n\n"
                "你可以：\n"
                "　🔄 说「换一批」重新推荐\n"
                "　🎲 说「盲盒模式」让我随机选一个\n"
                "　❓ 直接问我某个地方的详细信息"
            ),
            "ask_for": [],
        }

    # 默认：确认已收集的信息，询问是否生成推荐
    summary = _intent_summary(intent)
    return {
        "message": (
            f"好的，已收到你的需求：\n{summary}\n\n"
            "确认无误的话，我就开始帮你找地方啦！🎯\n"
            "（也可以继续补充，比如「带宠物」「不要爬山」等）"
        ),
        "ask_for": [],
    }


def _intent_summary(intent: UserIntent) -> str:
    parts = []
    if intent.district:
        parts.append(f"📍 区域：{intent.district}")
    parts.append(f"👥 人数：{intent.group_size}人")
    parts.append(f"💰 预算：¥{intent.budget}以内")
    if intent.preferences:
        parts.append(f"🏷️ 偏好：{'、'.join(intent.preferences)}")
    if intent.has_pet:
        parts.append("🐶 带宠物")
    if intent.transport:
        parts.append(f"🚇 交通：{intent.transport}")
    return "\n".join(f"　{p}" for p in parts)
