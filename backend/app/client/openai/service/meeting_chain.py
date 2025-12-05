from typing import Dict, Any, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from client.openai.client import ai_client
from app.core.logger import log

# 定义 Pydantic 模型
class MeetingTypeResult(BaseModel):
    type: Literal["讨论", "同步", "评审"] = Field(description="会议类型")

class MeetingAssessmentResult(BaseModel):
    score: float = Field(description="十分制综合评分，保留一位小数", ge=0, le=10)
    reason: str = Field(description="详细的评分理由")

# 1. 判断会议类型
_detect_type_template = """你是一个会议类型分类助手。请根据会议标题和描述，判断会议类型。

| 会议分类 | 核心定义 | 举例 |
|---------|----------|--------|
| 讨论 | 针对非例行性议题，进行方案探讨、意见征集或做出决策的会议。 | 共创会、问题解决会、脑暴会、复盘会、意见征求会 |
| 评审 | 在固定节奏和框架下，处理周期性常规事务。参会人对会议目的、目标都很明确的讨论型会议。 | 例行评审会（如研发的评审会、职级晋升答辩会） |
| 同步 | 以信息传递、进度对齐与共识确认为主，不产出或偶尔产出新结论的会议。 | 宣贯会、培训分享、项目站会、述职、预约、团建、团队例会 |

输入信息：
标题：{title}
描述：{description}

{format_instructions}
"""

# 2. 根据类型评估会议质量
# 2.1 常规类会议评估细则
_assess_normal_template = """你是一个会议质量评估专家。请根据会议标题和描述，对【评审】类会议进行评分。

评分规则：
1. 标题内容表达清晰，能明确会议主题；
2. 描述中可以获取决策项、决策人
3. 会议资料准备
- **评估重点**：会议描述中是否明确列出资料信息  
- **判定方式**：
  - 文本中出现资料信息，例如 ”会议资料：[链接]”、”资料见附件”、”宣贯资料在钉盘 XX/XX/XX”等
  - 只要提到资料信息，即可认定为资料准备完备
4. 区分必选和可选参会人
  
输入信息：
标题：{title}
描述：{description}

{format_instructions}
"""

_assess_advertise_template = """你是一个会议质量评估专家。请根据会议标题和描述，对【宣贯】类会议进行评分。

评分规则：
1. 标题和描述内容表达清晰，能明确会议主题
2. 会议资料准备
- **评估重点**：会议描述中是否明确列出资料信息  
- **判定方式**：
  - 文本中出现资料信息，例如 ”会议资料：[链接]”、”资料见附件”、”宣贯资料在钉盘 XX/XX/XX”等
  - 只要提到资料信息，即可认定为资料准备完备

输入信息：
标题：{title}
描述：{description}

{format_instructions}
"""

_assess_discuss_template = """你是一个会议质量评估专家。请根据会议标题和描述，对【研讨】类会议进行评分。

评分规则：
1. 标题和描述内容表达清晰，能明确会议主题
2. 会议目标清晰度（Objective Clarity）  
- **评估维度**：会议描述中识别是否包含以下三要素（POT模型）
  - **Purpose（目的）**：为何召开此会？解决什么问题？
  - **Objective（目标）**：期望达成的具体结果
  - **Timeline/Agenda（议程流程）**：是否有时间安排或议题顺序？

3. 参会人合理性（Participant Rationality）  
- **评估重点**：会议描述中是否明确列出关键决策人  
- **适用范围**：**仅适用于【研讨】类会议**  

- **判定方式**：
  - 文本中出现具体角色（如“CMO”、“项目负责人”、“财务审批人”）或姓名
  - 不接受模糊表述（如“相关部门人员”、“管理层代表”）

4. 加分项
**有以下内容的可以加分，没有也不会影响原分数**
- 补充了会议背景描述
- 补充了会议资料

输入信息：
标题：{title}
描述：{description}

{format_instructions}
"""

class MeetingChain:
    """通过分步调用 LLM 完成会议评估：1) 识别类型 2) 针对类型评估 3) 聚合结果"""

    def __init__(self):
        self.llm = ai_client.get_llm("qwen-plus", True)

    def detect_type(self, title: str, description: str) -> str:
        """同步：返回会议类型字符串（研讨/宣贯/常规/无法识别）。"""
        parser = PydanticOutputParser(pydantic_object=MeetingTypeResult)
        prompt = ChatPromptTemplate.from_template(_detect_type_template)
        chain = prompt | self.llm | parser
        
        try:
            res = chain.invoke({
                "title": title, 
                "description": description,
                "format_instructions": parser.get_format_instructions()
            })
            return res.type
        except Exception as e:
            log.error(f"Detect type failed: {e}")
            return "常规"

    def assess_by_type(self, mtype: str, title: str, description: str) -> Dict[str, Any]:
        """同步：按类型评估，返回包含 partial_score 和 reason 的字典。"""
        parser = PydanticOutputParser(pydantic_object=MeetingAssessmentResult)
        
        if mtype == "宣贯":
            template = _assess_advertise_template
        elif mtype == "研讨":
            template = _assess_discuss_template
        else:
            template = _assess_normal_template
            
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | parser
        
        try:
            res = chain.invoke({
                "title": title, 
                "description": description,
                "format_instructions": parser.get_format_instructions()
            })
            return res.model_dump()
        except Exception as e:
            log.error(f"Assess failed: {e}")
            return {"score": 0.0, "reason": f"LLM 调用失败: {str(e)}"}

    def evaluate(self, title: str, description: str) -> Dict[str, Any]:
        """分步评估：检测类型 -> 按类型评估 -> 聚合返回完整结构"""
        mtype = self.detect_type(title, description)
        assess = self.assess_by_type(mtype, title, description)
        score = assess.get("score", 0.0)
        reason = assess.get("reason", "")
        log.info(f"Meeting Evaluation - Title: {title}, Type: {mtype}, Score: {score}, Reason: {reason}")
        return {"title": title, "type": mtype, "score": score, "reason": reason}


# 提供默认实例
default_meeting_chain = MeetingChain()


