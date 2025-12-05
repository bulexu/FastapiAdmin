"""
钉钉相关常量配置
"""

# 钉钉API相关常量
DINGTALK_API_BASE_URL = "https://oapi.dingtalk.com"
DINGTALK_ACCESS_TOKEN_URL = f"{DINGTALK_API_BASE_URL}/gettoken"

# SDK配置常量
DINGTALK_SDK_PROTOCOL = "https"
DINGTALK_SDK_REGION_ID = "central"

# 默认用户配置 待移除
DEFAULT_UNION_IDS = [
    'GT3e3cCj1qqYfLXpBQqhnAiEiE',    # 涛哥
    'WE8EbHLx019kz537fwygrAiEiE'     # 百恒
]

# 时间格式常量
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S+08:00"
DISPLAY_DATE_FORMAT = "%Y-%m-%d %H:%M"

# 会议相关常量
MEETING_STATUS_ACTIVE = "confirmed"
MEETING_STATUS_CANCELLED = "cancelled"
MEETING_STATUS_TENTATIVE = "tentative"

# 日历相关常量
DEFAULT_CALENDAR_ID = "primary"
DEFAULT_TIMEZONE = "+08:00"
