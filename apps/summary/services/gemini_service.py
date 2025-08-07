import json
import re
import datetime
import os
from dotenv import load_dotenv

from django.contrib.auth.models import User

from google import genai
from google.genai import types
from apps.usage.models import UsageRecord


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# user_data = """
# YouTube - 2시간 30분 (쉬는 시간에 봄. 너무 오래 본 것 같음)
# Instagram - 1시간 (별로 할 일 없을 때 켰음)
# Notion - 40분 (강의 노트 정리)
# Chrome - 1시간 10분 (과제 관련 자료 조사)
# 게임 - 1시간 (스트레스 풀려고 함)
# """

PROMPT_TEMPLATE = """
당신은 사용자의 스마트폰 사용 습관을 분석하는 요약 및 피드백 전문가입니다.

다음은 사용자의 하루 스마트폰 사용 기록입니다. 각 항목은 사용한 앱 이름, 사용 시간, 그리고 사용자가 직접 남긴 간단한 메모로 구성되어 있습니다.

다음 지시사항을 반드시 지켜서 분석을 수행해 주세요:

1. 모든 데이터를 기반으로 **하루 전체 스마트폰 사용 습관을 요약**해 주세요.  
   - 단순 나열이 아닌, 사용자 습관의 **경향성이나 특징**을 중심으로 2~3문장으로 요약합니다.

2. 이어서, 사용자가 **내일 더 나은 습관을 가질 수 있도록 짧은 피드백**을 제공해 주세요.  
   - **긍정적인 영향**을 줄 수 있도록 표현하되, 개선이 필요한 점은 **정제된 표현으로 부드럽게 지적**해 주세요.  
   - 잔소리처럼 들리지 않도록, **조언의 형태**로 작성해 주세요.

3. 출력은 반드시 다음의 JSON 형식을 따릅니다.  
   - 다른 설명이나 포맷 없이 JSON 객체만 출력합니다.

```json
{{
  "summary": "짧은 두세 줄 피드백",
  "feedback": "짧은 한두 줄 피드백"
}}
```
휴대폰 사용 기록:
{user_data}

---

### 출력 예시 기대값

```json
{{
  "summary": "유튜브는 학습목적으로 잘 이용하셨군요! 새벽에 스마트폰을 하는 습관은 다음날 컨디션을 망칠 수 있습니다.",
  "feedback": "YouTube 사용 시간을 조금 줄이면 더 생산적인 하루가 될 수 있어요!"
}}
```

※ 반드시 JSON만 출력하고, 다른 설명은 하지 마세요.
"""


def prompt(user_data: str) -> str:
    return PROMPT_TEMPLATE.format(user_data=user_data)


def extract_json(text: str) -> dict:
    # ```json ... ``` 또는 ``` ... ``` 안의 JSON만 추출
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        json_text = match.group(1)
    else:
        json_text = text.strip() 

    try:
        return json.loads(json_text)
    
    except json.JSONDecodeError as e:
        print("❗ JSON 파싱 실패:", e)
        print("원본 응답:", text)
        return None
    

def generate_summary(user: User, target_date: datetime.date) -> tuple[bool, str]: 
    start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
    end_of_day = datetime.datetime.combine(target_date, datetime.time.max)
    
    records = UsageRecord.objects.filter(
        user=user,
        created_at__range=(start_of_day, end_of_day)
    ).select_related('app').order_by('start_time')
    
    if not records.exists():
        return False, f"{target_date}에는 사용 기록이 없습니다."

    # 앱 이름 + 사용 시간 + 메모 기반으로 텍스트 생성
    record_lines = []
    for record in records:
        app_name = record.app.app_name if record.app else "알 수 없음"
        usage_minutes = round((record.usage_time_ms or 0) / 1000 / 60)
        memo = record.memo.strip() if record.memo else ""

        line = f"{app_name} - {usage_minutes}분"
        if memo:
            line += f" ({memo})"
        record_lines.append(line)

    user_data_text = "\n".join(record_lines)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt(user_data_text),
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
    )
    data = extract_json(response.text)
    return True, f"{data['summary']} {data['feedback']}"
