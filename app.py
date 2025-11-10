"""
AI竞争力诊断问卷App - FastAPI后端
"""
import os
import json
from typing import Dict, Any, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx

# 加载环境变量
load_dotenv()

app = FastAPI(title="AI竞争力诊断问卷")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# AI Builder API配置
AI_BUILDER_BASE_URL = "https://www.ai-builders.com/resources/students-backend"
AI_BUILDER_MODEL = "gpt-5"


def get_ai_builder_token() -> str:
    """从环境变量获取AI Builder Token"""
    token = os.getenv("AI_BUILDER_TOKEN")
    if not token:
        raise ValueError("AI_BUILDER_TOKEN环境变量未设置")
    return token


# 问卷问题数据
QUESTIONS = [
    {
        "id": "Q1",
        "text": "当一个重复性的手动任务（例如，每周整理数据并发送邮件）让你感到厌烦时，你脑中首先出现的想法更接近于？",
        "options": {
            "A": "这是工作流程的一部分，想办法更专注、更快速地手动完成它。",
            "B": "寻找一个现成的付费软件或工具（如Mailchimp），一劳永逸地解决问题。",
            "C": "用自然语言向AI描述我的需求，让它生成一段代码或脚本来自动化这个流程。",
            "D": "这暴露了流程本身的问题，我会思考如何从根本上重构工作流，让这个任务消失。"
        }
    },
    {
        "id": "Q2",
        "text": "当你尝试使用AI辅助工作，但它的产出不准确甚至胡说八道时，你的反应是？",
        "options": {
            "A": "证实了AI目前还不可靠，在严肃工作中应谨慎使用。",
            "B": "把它看作一个需要引导的实习生，我会调整我的指令，尝试几次，看能否教会它。",
            "C": "这是一个信号，说明我提供给它的上下文不足。我会整理相关背景资料喂给它。",
            "D": "我会反思我的工作流，也许这个问题本身就不适合让AI独立完成，需要重新设计人机协作的方式。"
        }
    },
    {
        "id": "Q3",
        "text": "公司引入了一个全新的内部知识库，但信息繁杂。你希望如何利用它？",
        "options": {
            "A": "等待IT部门推出一个好用的搜索界面或导航功能。",
            "B": "自己花时间通读一遍，建立自己的大脑索引。",
            "C": "思考是否能用AI连接这个知识库的API，构建一个自己专用的智能问答机器人。",
            "D": "主动为知识库内容撰写和补充结构化数据，让它变得机器可读，从而方便自己和团队未来用AI进行交互。"
        }
    },
    {
        "id": "Q4",
        "text": "你需要AI帮你写一段用于数据分析的代码。在与AI的交互中，哪种情况最符合你的现状？",
        "options": {
            "A": "我直接告诉它目标，比如帮我分析销售数据，然后看看它会给我什么。",
            "B": "我会先给它数据表的结构（Schema），然后提出具体分析需求。",
            "C": "在一次长对话中，我不断提出修改意见，比如这里不对，换个图表，那里逻辑错了，重新计算，直到它改对为止。",
            "D": "如果对话变得混乱，我会停止追问，直接回到我最初的指令上，把所有修正和新要求编辑、整合进去，形成一个清晰、完整的新指令。"
        }
    },
    {
        "id": "Q5",
        "text": "你需要调研十个竞争对手的最新动态并形成报告。你会如何借助AI？",
        "options": {
            "A": "向AI提出一个总括性问题：请调研这十家公司并给我一份报告。",
            "B": "我会先让AI帮我列出十家公司的名单，然后逐一让它分别深入调研每一家，最后我自己汇总。",
            "C": "我会设计一个工作流，让一个主管AI将任务拆分给十个分析员AI，每个分析员AI负责一家公司，最后由主管AI汇总所有报告。",
            "D": "我和AI一起探讨，先定义最新动态的范围和标准，然后让AI分步执行，并在关键节点向我汇报，由我来调整下一步的调研方向。"
        }
    },
    {
        "id": "Q6",
        "text": "对你而言，AI原生的工作环境意味着什么？",
        "options": {
            "A": "在我的所有软件里都内嵌了AI助手按钮。",
            "B": "我能熟练地在不同的AI工具之间切换，以完成复杂任务。",
            "C": "我的工作文档、代码和数据都存放在一个AI可以随时读写的环境中（如Cursor），AI是我的队友。",
            "D": "我的工作成果本身就是可被其他AI调用的、结构化的知识资产。"
        }
    },
    {
        "id": "Q7",
        "text": "忘掉旧经验对你来说，更像是一种？",
        "options": {
            "A": "威胁",
            "B": "挑战",
            "C": "解放",
            "D": "机遇"
        }
    },
    {
        "id": "Q8",
        "text": "你认为未来最有价值的技能是？",
        "options": {
            "A": "精通某个特定AI工具",
            "B": "快速学习任何新工具的能力",
            "C": "定义问题和判断结果的批判性思维",
            "D": "设计和优化人机协作系统"
        }
    },
    {
        "id": "Q9",
        "text": "想象你被指派领导一个重要但定义模糊的项目，例如利用AI提升客户满意度。在项目启动的第一周，你的工作重心会是什么？",
        "options": {
            "A": "立即动手实验：直接选用几种主流AI工具，对现有的客户数据进行分析和互动，快速寻找可能存在的亮点或速效成果。",
            "B": "规划详细路径：将提升满意度这个大目标，拆解成一系列具体、可执行的技术任务（如：数据清理、情感分析模型训练、聊天机器人部署等），并制定一份详尽的执行时间表。",
            "C": "定义核心问题：花费大部分时间与业务部门、客户支持团队甚至真实客户进行访谈，目的是精确地定义客户满意度的衡量标准，以及当前最关键的痛点是什么。",
            "D": "设计工作系统：思考如何构建一个可持续的系统，让AI能够长期、自动地监测、分析并预警客户满意度的变化，而你的角色是基于这个系统的洞察来做出战略决策。"
        }
    },
    {
        "id": "Q10",
        "text": "当您想象自己已真正掌握与AI的协作时，以下哪种情景最能代表您职业生涯中的终极胜利？",
        "options": {
            "A": "效率的极致：我能在几分钟内完成过去需要数天才能完成的分析和报告，成为团队中无可争议的效率冠军和领域专家。",
            "B": "智慧的延伸：AI成为我思维的副驾驶，能帮我进行头脑风暴、突破创意瓶颈，并发现我独自一人可能会忽略的深层联系与机会。",
            "C": "创造的力量：每当团队被一个现有工具无法解决的、独特的长尾问题所困扰时，我能通过自然语言指挥AI，为我们量身打造一个微型应用或自动化流程来根本性地解决它。",
            "D": "知识的权威：我成为组织内的AI布道者，总能第一时间掌握最新的AI工具和方法论，并指导、赋能团队中的其他人。"
        }
    }
]


def build_analysis_prompt(answers: Dict[str, str]) -> Tuple[str, str]:
    """构建用于AI分析的Prompt，返回system prompt和user prompt"""
    answers_json = json.dumps(answers, ensure_ascii=False, indent=2)
    
    system_prompt = """你是一位资深的AI战略顾问和课程助教，深刻理解构建者心态和AI协作五阶段框架。

你的工作方式：

要有深度，有独立思考。在回答问题、做任务之前先想想，为什么要问这个问题？背后有没有什么隐藏的原因？因为很多时候可能交给你一个任务，是在一个更大的context下面，已经做了一些假设。你要思考这个假设可能是什么，有没有可能问的问题本身不是最优的，如果我们突破这个假设，可以问出更正确的问题，从更根本的角度得到启发。

在你回答问题的时候，要先思考一下，你的答案的成功标准是什么。换言之，什么样的答案是好的。注意，不是说你要回答的问题，而是说你的回答的内容本身要满足什么标准，才算是很好地解决了需求。然后针对这些标准构思答案。

你最终还是要给出一个答案的。但是我们是一个collaborative的关系。你的目标不是单纯的在一个回合的对话中给出一个确定的答案（这可能会逼着你一些假设不明的时候随意做出假设），而是合作，一步步找到问题的答案，甚至是问题实际更好的问法。换言之，你的任务不是follow指令，而是给出启发。

语言风格要求：
- 不要滥用bullet points，把它们局限在top level。尽量用自然语言自然段。
- 不要使用任何引号，包括中文引号和英文引号。
- 使用理性内敛的语言风格，用思考深度来表现专业，而不是堆砌宏大词藻。
- 避免用文学性比喻。
- 保持赋能和引导的语气，而非评判。"""
    
    user_prompt = f"""# 核心理论框架

身份认同模型: 个体分为两种心态。用户 (User)：被动使用工具，期待现成的GUI解决方案，将问题归咎于工具。构建者 (Builder)：主动解决问题，将AI视为通过自然语言交互的计算接口，致力于解决长尾生产力问题，信奉通过构建来学习。

协作成熟度模型: 与AI的协作分为五个阶段。

阶段一：黑箱 (Black Box): 将AI视为神谕，缺乏上下文。

阶段二：实习生 (Intern): 通过对话反复修正，易造成上下文污染。核心技能是 上下文策展 (Context Curation)。

阶段三：队友 (Teammate): 在AI原生环境中协作，核心是创造机器可读的知识资产，成为 上下文架构师 (Context Architect)。

阶段四：项目经理 (Project Manager): 解决因上下文饱和导致的大型任务失败。核心技能是 分而治之 (Divide and Conquer)。

阶段五：共创者 (Co-creator): 共同探索开放性战略问题，人类的判断力和专业知识成为最重要的上下文。

# 学员回答
学员的回答如下（JSON格式）：
{answers_json}

# 分析报告结构与指令

请生成一份Markdown格式的报告，包含以下部分：

## 综合评分

首先给出一个综合评分（0-100分），这个分数应该综合考虑学员在构建者心态和协作成熟度两个维度的表现。分数应该反映学员当前的整体水平，同时也要考虑其成长潜力。给出分数后，用一句话简要说明评分的依据。

## 你的核心身份诊断：用户心智 vs. 构建者心智

基于问题1-3的回答，精确判断学员的核心身份偏向。避免简单的二元划分，可以描述其混合状态。要有深度，能够洞察学员回答背后的思维模式和潜在假设。

## 你的协作成熟度定位：在五阶段的哪一级？

基于问题4-6的回答，判断学员当前最匹配的协作阶段。指出其掌握的相应技能和面临的典型瓶颈。要思考学员回答背后的深层逻辑，而不仅仅是表面的选择。

## 你的进阶路径图：从划桨手到领航员

结合身份和阶段的诊断，提供1-2个具体、可执行的、与课程理念紧密结合的进阶建议。这些建议应该能够突破学员当前的假设，从更根本的角度给出启发。

## 最后的启发性问题

在报告结尾，提出一个能激发学员开启构建者旅程的开放性问题。这个问题应该能够引导学员思考更深层的问题。

# 规则

报告中必须自然地使用课程中的关键词（如构建者、上下文策展、上下文架构师、分而治之、长尾生产力问题等）。

不要使用任何引号，包括中文引号和英文引号。

总字数控制在1000字以内。

请直接生成报告内容，不需要额外的说明文字。"""
    
    return system_prompt, user_prompt


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回前端页面"""
    return FileResponse("static/index.html")


@app.get("/api/questions")
async def get_questions():
    """获取问卷问题列表"""
    return {"questions": QUESTIONS}


@app.post("/api/analyze")
async def analyze_answers(answers: Dict[str, str]):
    """分析用户答案并生成报告"""
    try:
        # 验证答案格式
        if not answers or len(answers) < 9:
            raise HTTPException(status_code=400, detail="答案不完整，请回答所有问题")
        
        # 构建Prompt
        system_prompt, user_prompt = build_analysis_prompt(answers)
        
        # 调用AI Builder API
        token = get_ai_builder_token()
        url = f"{AI_BUILDER_BASE_URL}/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": AI_BUILDER_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2500
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
        
        # 提取生成的报告内容
        if "choices" in result and len(result["choices"]) > 0:
            report_content = result["choices"][0]["message"]["content"]
            return {"report": report_content}
        else:
            raise HTTPException(status_code=500, detail="AI API返回格式异常")
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"AI API调用失败: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

