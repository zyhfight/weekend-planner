"""
数据模型定义 - Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class UserIntent(BaseModel):
    """用户意图模型"""
    city: str = "杭州"
    district: Optional[str] = None
    group_size: int = 1
    budget: int = 500  # 总预算（元）
    preferences: List[str] = Field(default_factory=list)
    duration: Optional[str] = None
    transport: Optional[str] = None
    weather_sensitive: bool = True
    has_pet: bool = False
    special_needs: Optional[str] = None


class Location(BaseModel):
    """地理位置"""
    lng: float
    lat: float


class BudgetBreakdown(BaseModel):
    """预算明细"""
    ticket: int = 0
    transport: int = 0
    food: int = 0
    other: int = 0
    total: int = 0


class Recommendation(BaseModel):
    """推荐结果"""
    id: str
    name: str
    address: str
    location: Location
    match_score: int = 0  # 0-100
    reason: str = ""
    budget_breakdown: BudgetBreakdown
    transport_guide: str = ""
    best_time: str = ""
    tips: List[str] = Field(default_factory=list)
    weather_suitability: str = ""
    tags: List[str] = Field(default_factory=list)


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # "user" or "assistant"
    content: str
    recommendations: Optional[List[Recommendation]] = None


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    session_id: str = "default"
    intent: Optional[UserIntent] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    intent: Optional[UserIntent] = None
    recommendations: Optional[List[Recommendation]] = None
    ask_for: Optional[List[str]] = None  # 需要用户补充的信息字段
