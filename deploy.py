#!/usr/bin/env python3
"""
部署脚本：调用AI Builder部署API
"""
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

AI_BUILDER_BASE_URL = "https://www.ai-builders.com/resources/students-backend"
SERVICE_NAME = "ai-readiness"
REPO_URL = "https://github.com/grapeot/ai_readiness_survey"
BRANCH = "master"
PORT = 8000

def deploy():
    token = os.getenv("AI_BUILDER_TOKEN")
    if not token:
        print("错误: AI_BUILDER_TOKEN环境变量未设置")
        return
    
    url = f"{AI_BUILDER_BASE_URL}/v1/deployments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "service_name": SERVICE_NAME,
        "repo_url": REPO_URL,
        "branch": BRANCH,
        "port": PORT
    }
    
    print(f"正在部署服务: {SERVICE_NAME}")
    print(f"仓库: {REPO_URL}")
    print(f"分支: {BRANCH}")
    print(f"端口: {PORT}")
    print()
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            print("部署请求已提交！")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if "status" in result:
                print(f"\n状态: {result['status']}")
            if "message" in result:
                print(f"消息: {result['message']}")
            if "deployment_prompt_url" in result:
                print(f"\n部署提示URL: {result['deployment_prompt_url']}")
                
    except httpx.HTTPStatusError as e:
        print(f"部署失败: HTTP {e.response.status_code}")
        print(f"响应: {e.response.text}")
    except Exception as e:
        print(f"部署失败: {str(e)}")

if __name__ == "__main__":
    deploy()

