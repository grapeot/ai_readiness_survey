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
AI_BUILDER_MODEL = "grok-4-fast"


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
        "text": "When a repetitive manual task (e.g., weekly data organization and email sending) annoys you, what comes to mind first?",
        "options": {
            "A": "Focus on manual completion with better concentration",
            "B": "Search for an existing paid tool to solve it permanently",
            "C": "Describe my needs to AI in natural language to generate automation code",
            "D": "Rethink the workflow fundamentally to eliminate this task"
        }
    },
    {
        "id": "Q2",
        "text": "When you try to use AI to assist your work, but its output is inaccurate or even nonsensical, your reaction is:",
        "options": {
            "A": "Confirm AI is unreliable and use it cautiously in serious work",
            "B": "Treat it like an intern, adjust instructions and try to teach it",
            "C": "Recognize insufficient context and provide relevant background materials",
            "D": "Reflect on workflow design and reconsider human-AI collaboration approach"
        }
    },
    {
        "id": "Q3",
        "text": "Your company introduces a new internal knowledge base, but the information is complex. How would you like to utilize it?",
        "options": {
            "A": "Wait for IT to provide a search interface or navigation",
            "B": "Read through everything myself to build a mental index",
            "C": "Consider connecting the knowledge base API with AI to build a custom Q&A bot",
            "D": "Proactively add structured data to make content machine-readable for future AI interaction"
        }
    },
    {
        "id": "Q4",
        "text": "You need AI to help write code for data analysis. Which scenario best matches your current interaction with AI?",
        "options": {
            "A": "Tell AI the goal directly and see what it produces",
            "B": "Provide the data schema first, then specify analysis requirements",
            "C": "Make iterative corrections in a long conversation until it's right",
            "D": "Stop and reorganize all corrections into a clear, complete new instruction"
        }
    },
    {
        "id": "Q5",
        "text": "You need to research ten competitors' latest developments and create a report. How would you leverage AI?",
        "options": {
            "A": "Ask AI one broad question to research all ten companies",
            "B": "Have AI list companies, then research each separately and summarize myself",
            "C": "Design a workflow where a manager AI splits tasks among analyst AIs",
            "D": "Co-define scope and standards, then have AI execute step-by-step with checkpoints"
        }
    },
    {
        "id": "Q6",
        "text": "What does an AI-native work environment mean to you?",
        "options": {
            "A": "AI assistant buttons embedded in all my software",
            "B": "Skillfully switching between different AI tools for complex tasks",
            "C": "Working in an AI-native environment where AI can read and write my files",
            "D": "My work outputs are structured knowledge assets that other AIs can call"
        }
    },
    {
        "id": "Q7",
        "text": "Forgetting old experience feels more like:",
        "options": {
            "A": "Threat",
            "B": "Challenge",
            "C": "Liberation",
            "D": "Opportunity"
        }
    },
    {
        "id": "Q8",
        "text": "What skill do you think will be most valuable in the future?",
        "options": {
            "A": "Mastering a specific AI tool",
            "B": "Ability to quickly learn any new tool",
            "C": "Critical thinking to define problems and judge outcomes",
            "D": "Designing and optimizing human-AI collaboration systems"
        }
    },
    {
        "id": "Q9",
        "text": "Imagine you're assigned to lead an important but vaguely defined project, such as using AI to improve customer satisfaction. In the first week, what would be your focus?",
        "options": {
            "A": "Start experimenting immediately with mainstream AI tools to find quick wins",
            "B": "Break down the goal into detailed technical tasks with a comprehensive timeline",
            "C": "Spend most time interviewing stakeholders to precisely define success metrics and pain points",
            "D": "Design a sustainable system for AI to continuously monitor and alert, with me making strategic decisions"
        }
    },
    {
        "id": "Q10",
        "text": "When you imagine truly mastering AI collaboration, which scenario best represents your ultimate career victory?",
        "options": {
            "A": "Maximum efficiency: completing days of work in minutes, becoming the undisputed efficiency champion",
            "B": "Extended intelligence: AI as my co-pilot for brainstorming and discovering hidden connections",
            "C": "Creative power: building custom micro-apps or automations to solve unique long-tail problems",
            "D": "Knowledge authority: becoming the AI evangelist who guides and empowers the team"
        }
    }
]


def build_analysis_prompt(answers: Dict[str, str]) -> Tuple[str, str]:
    """Build prompt for AI analysis, returns system prompt and user prompt"""
    # Build detailed responses including question text and selected option content
    responses_detailed = []
    for q in QUESTIONS:
        qid = q["id"]
        selected_key = answers.get(qid)
        selected_text = None
        if selected_key is not None:
            selected_text = q["options"].get(selected_key)
        options_list = [{"key": k, "text": v} for k, v in q["options"].items()]
        responses_detailed.append({
            "id": qid,
            "text": q["text"],
            "selected": {"key": selected_key, "text": selected_text},
            "options": options_list
        })
    responses_json = json.dumps(responses_detailed, ensure_ascii=False, indent=2)
    
    system_prompt = """You are a senior AI strategy consultant and course teaching assistant with deep understanding of the builder mindset and the five-stage AI collaboration framework.

Your working approach:

Be deep and think independently. Before answering questions or completing tasks, think: why am I being asked this question? What hidden reasons might there be? Often, a task is given to you within a larger context where assumptions have already been made. Think about what those assumptions might be, and whether the question itself might not be optimal. If we break through these assumptions, we might ask better questions and gain insights from more fundamental angles.

When answering questions, first think about what the success criteria for your answer are. In other words, what makes an answer good. Note that this is not about the question you are answering, but about what standards your response content itself must meet to effectively address the need. Then construct your answer based on these criteria.

You still need to provide an answer. But we have a collaborative relationship. Your goal is not simply to give a definitive answer in one round of conversation (which might force you to make assumptions when they are unclear), but to collaborate, step by step, to find the answer to the question, or even a better way to ask the question. In other words, your task is not to follow instructions, but to provide insight.

Language style requirements:
- Do not overuse bullet points; limit them to top level. Prefer natural language paragraphs.
- Do not use any quotation marks, including Chinese and English quotation marks.
- Use a rational, restrained language style, demonstrating expertise through depth of thought rather than grandiose rhetoric.
- Avoid literary metaphors.
- Maintain an empowering and guiding tone rather than judgmental."""
    
    user_prompt = f"""# Core Theoretical Framework

Identity Model: Individuals fall into two mindsets. User: Passive tool users who expect ready-made GUI solutions and blame tools for problems. Builder: Proactive problem solvers who treat AI as a computational interface through natural language interaction, dedicated to solving long-tail productivity problems, believing in learning through building.

Collaboration Maturity Model: AI collaboration progresses through five stages.

Stage One: Black Box. Treating AI as an oracle, lacking context.

Stage Two: Intern. Making iterative corrections through conversation, prone to context pollution. Core skill is Context Curation.

Stage Three: Teammate. Collaborating in AI-native environments, core is creating machine-readable knowledge assets, becoming a Context Architect.

Stage Four: Project Manager. Solving large task failures caused by context saturation. Core skill is Divide and Conquer.

Stage Five: Co-creator. Jointly exploring open strategic questions, where human judgment and expertise become the most important context.

# Student Responses (structured)
    The student's responses are provided as a structured list with each original question, the selected option key and content, and all available options for grounding:
    {responses_json}

# Report Structure and Instructions

Please generate a Markdown format report containing the following sections. When referencing a response, include the question text and the selected option content (do not use bare letters without content). Use the structured responses above as ground truth:

## Overall Score

First provide an overall score (0-100 points). This score should comprehensively consider the student's performance in both builder mindset and collaboration maturity dimensions. The score should reflect the student's current overall level while also considering their growth potential. After giving the score, briefly explain the scoring rationale in one sentence.

## Your Core Identity Diagnosis: User Mindset vs. Builder Mindset

Based on responses to questions 1-3, precisely determine the student's core identity orientation. Avoid simple binary divisions; describe mixed states. Be deep, able to discern the thinking patterns and underlying assumptions behind the student's responses.

## Your Collaboration Maturity Positioning: Which Stage?

Based on responses to questions 4-6, determine the student's current matching collaboration stage. Point out the corresponding skills they have mastered and typical bottlenecks they face. Think about the deep logic behind the student's responses, not just surface choices.

## Your Advancement Roadmap: From Rower to Navigator

Combining identity and stage diagnosis, provide 1-2 specific, actionable advancement recommendations closely aligned with course philosophy. These recommendations should break through the student's current assumptions and provide insights from more fundamental angles.

## Final Inspiring Question

At the end of the report, pose an open-ended question that can inspire the student to begin their builder journey. This question should guide the student to think about deeper issues.

# Rules

The report must naturally use course keywords (such as builder, context curation, context architect, divide and conquer, long-tail productivity problems, etc.).

Do not use any quotation marks, including Chinese and English quotation marks.

Total word count should be controlled within 1000 words.

Please generate the report content directly without additional explanatory text."""
    
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
        # Validate answer format
        if not answers or len(answers) < 9:
            raise HTTPException(status_code=400, detail="Incomplete answers. Please answer all questions.")
        
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
