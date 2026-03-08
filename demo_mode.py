"""데모 모드 — AgentCore 없이 샘플 데이터로 시뮬레이션 + Bedrock fallback"""
import json, os, random, time

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

DATA_DIR = os.environ.get("SAMPLE_DATA_DIR", "./data")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
BEDROCK_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

def _invoke_bedrock(message):
    """Bedrock Claude로 일반 질문 처리"""
    if not HAS_BOTO3:
        return None
    try:
        client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
        resp = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "system": "당신은 GS25 편의점 발주 자동화 도우미입니다. 친절하고 간결하게 한국어로 답변하세요.",
                "messages": [{"role": "user", "content": message}],
            }),
        )
        body = json.loads(resp["body"].read())
        return body.get("content", [{}])[0].get("text", "응답을 생성하지 못했습니다.")
    except Exception as e:
        return None

def load_json(name):
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def demo_response(message):
    """샘플 데이터 기반 데모 응답 생성"""
    msg = message.lower()
    tool_calls = []
    stores = load_json("stores.json") or []
    sales = load_json("sales_history.json") or []
    weather = load_json("weather_forecast.json") or {}
    inventory = load_json("inventory.json") or []
    waste = load_json("waste_rate.json") or []

    # 점포명 추출
    store_name = None
    for s in (stores if isinstance(stores, list) else stores.get("stores", [])):
        name = s.get("name", s.get("store_name", ""))
        if name and name in message:
            store_name = name
            break

    if "발주" in msg:
        tool_calls = [
            {"tool": "query_sales_db", "input": f'store: "{store_name or "역삼역점"}", weeks: 4', "output": "도시락 avg 62개/일, 음료 avg 180개/일", "time": "0.4s"},
            {"tool": "weather_api", "input": 'date: "tomorrow", location: "강남"', "output": "맑음, 최고 26°C → 아이스음료 +18%", "time": "0.3s"},
            {"tool": "calc_order_qty", "input": "base_data + weather_factor", "output": "도시락 78개, 음료 236개, 베이커리 38개", "time": "0.5s"},
        ]
        text = f"""📦 **{store_name or '역삼역점'}** 발주 분석 결과입니다.

최근 4주 매출 데이터와 내일 날씨를 분석했어요.

| 카테고리 | 권장 발주량 | 전주比 |
|---------|-----------|-------|
| 도시락/김밥 | 78개 | +26% |
| 음료 | 236개 | +31% |
| 베이커리 | 38개 | +12% |

💡 내일 맑은 날씨로 아이스음료 수요가 +18% 예상되어 음료 비중을 높였습니다.
⚠️ 베이커리 폐기율 8.2% — 15% 감소 적용했습니다."""

    elif "폐기" in msg:
        tool_calls = [
            {"tool": "query_waste_db", "input": f'store: "{store_name or "전체"}"', "output": "평균 폐기율 4.8%", "time": "0.3s"},
        ]
        text = f"""🗑️ **{store_name or '전체 점포'}** 폐기율 현황입니다.

| 카테고리 | 폐기율 | 상태 |
|---------|-------|------|
| 도시락 | 3.2% | ✅ 양호 |
| 베이커리 | 8.2% | ⚠️ 기준 초과 |
| 음료 | 1.1% | ✅ 양호 |
| 유제품 | 5.8% | ⚠️ 기준 초과 |

💡 베이커리와 유제품 카테고리의 발주량 조정을 권장합니다."""

    elif "이상" in msg or "감지" in msg or "알림" in msg:
        tool_calls = [
            {"tool": "scan_all_stores", "input": 'realtime: true, stores: "all_23"', "output": "23개 점포 스캔 완료", "time": "0.6s"},
            {"tool": "detect_anomaly", "input": 'threshold: 2.0', "output": "이상 감지: 3개 점포", "time": "0.4s"},
        ]
        text = """🚨 **이상 징후 감지 결과** (23개 점포 스캔)

| 점포 | 이상 유형 | 상세 |
|------|---------|------|
| 잠실 1호점 | 매출 급락 | 전일比 -38% (지하철 공사) |
| 홍대 2호점 | 폐기율 초과 | 14.2% (기준 5%) |
| 신촌 3호점 | 재고 부족 | 음료 카테고리 0건 |

담당 매니저에게 알림을 발송할까요?"""

    else:
        # 키워드 매칭 안 됨 → Bedrock Claude로 일반 질문 처리
        bedrock_answer = _invoke_bedrock(message)
        if bedrock_answer:
            tool_calls = [
                {"tool": "bedrock_claude", "input": f'model: "{BEDROCK_MODEL_ID}"', "output": "응답 생성 완료", "time": "1.2s"},
            ]
            text = bedrock_answer
        else:
            text = f"""안녕하세요! GS25 발주 자동화 Agent입니다 📦

아래와 같은 질문을 해보세요:
- "역삼역점 내일 발주 해줘"
- "잠실새내점 폐기율 어때?"
- "이번주 이상 점포 있어?"
- "테헤란로점 금요일 발주인데 음료 많이 시켜줘"

현재 **{len(stores) if isinstance(stores, list) else 0}개 점포** 데이터가 로드되어 있습니다."""

    return {"text": text, "tool_calls": tool_calls}
