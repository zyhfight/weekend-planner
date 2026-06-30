# 🎯 周末去哪玩专家

> AI 驱动的周末出行推荐工具 — 基于自然语言对话 + 结构化卡片，帮你快速决策"周末去哪玩"

当前 MVP 覆盖城市：**杭州**

## 在线预览

启动服务后访问 `http://localhost:8000`

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/zyhfight/weekend-planner.git
cd weekend-planner

# 2. 安装依赖（Python 3.11+）
pip install fastapi uvicorn pydantic requests

# 3. 配置高德地图 API Key（可选，不配置则使用内置知识库）
export AMAP_KEY=你的高德Key

# 4. 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

打开浏览器访问 `http://localhost:8000` 即可使用。

## 项目结构

```
weekend-planner/
├── app/
│   ├── main.py                 # FastAPI 主服务（路由 + 会话管理）
│   ├── models/
│   │   └── schemas.py          # Pydantic 数据模型定义
│   └── services/
│       ├── amap_service.py     # 高德地图 POI + 天气 API 服务
│       ├── dialogue.py         # 对话意图解析 + 机器人回复生成
│       └── recommendation.py   # 推荐引擎（匹配度打分 + 排序）
├── static/
│   └── index.html              # 前端页面（Tailwind + Leaflet 地图）
├── .gitignore
└── README.md
```

## 核心功能

### 🗣️ 聊天式引导对话

通过几个关键问题快速锁定用户画像：

- 活动区域（西湖区/上城区/拱墅区/滨江区/余杭区/不限）
- 出行人数
- 总预算
- 偏好类型（户外自然/文艺打卡/美食探店/遛娃友好/安静放空）

也支持自然语言直接输入，如：

> 「西湖区，2个人，500以内，想要文艺+美食」

### 📍 结构化推荐卡片

每条推荐包含：
- **匹配度评分**（0-100%）
- **推荐理由**（基于用户偏好匹配）
- **预算明细**（门票/交通/餐饮拆解）
- **交通指引**
- **最佳时段**
- **天气适配**
- **实用小贴士**

### 🎲 盲盒模式

设定约束条件后，系统随机推荐一个高匹配度地点，减少决策疲劳。

### 🗺️ 地图查看

基于 Leaflet + OpenStreetMap，一键查看推荐地点在地图上的位置。

### 📅 天气联动

接入高德天气 API，自动根据实时天气调整推荐策略（晴天→户外，雨天→室内）。

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 核心对话接口（意图解析 + 推荐生成） |
| `/api/recommend` | GET | REST 风格直接推荐（非对话场景） |
| `/api/weather` | GET | 获取实时天气信息 |
| `/health` | GET | 服务健康检查 |

### 对话接口示例

```json
// POST /api/chat
{
  "message": "西湖区，2个人，500以内，文艺打卡",
  "session_id": "user-123"
}

// Response
{
  "message": "好的，已收到你的需求...",
  "intent": { "city": "杭州", "district": "西湖区", "group_size": 2, "budget": 500, "preferences": ["文艺打卡"] },
  "recommendations": [
    {
      "id": "poi_002",
      "name": "中国美术学院（象山校区）",
      "match_score": 95,
      "reason": "符合你文艺打卡的需求...",
      "budget_breakdown": { "ticket": 0, "transport": 20, "food": 60, "total": 160 }
    }
  ]
}
```

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | FastAPI + Pydantic | Python 轻量异步框架 |
| 前端 | HTML + Tailwind CSS CDN | 无构建步骤，纯静态 |
| 地图 | Leaflet + OpenStreetMap | 轻量开源地图方案 |
| 数据源 | 高德地图 Web API | POI + 天气（需 API Key） |
| 推荐引擎 | 规则匹配 + 打分排序 | MVP 阶段，后续可接入 LLM |

## 高德地图 API 配置

1. 注册 [高德开放平台](https://lbs.amap.com/) 账号
2. 创建应用，获取 **Web 服务 API Key**
3. 设置环境变量：

```bash
export AMAP_KEY=你的Key
```

不配置 Key 时，系统使用内置的杭州 12 个精选 POI 知识库，推荐功能仍可正常使用。

## 后续迭代

- [ ] 接入 DeepSeek/Claude LLM，增强对话理解
- [ ] 多城市扩展（上海、北京、成都）
- [ ] 行程规划（多地点串联）
- [ ] 实时人流数据
- [ ] 用户个性化记忆
- [ ] 社交分享功能

## License

MIT
