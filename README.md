# GS Retail AI Agent — Streamlit UI

GS Retail × Kiro 워크샵용 Agent 채팅 UI입니다.

## 구성

| 파일 | 설명 |
|------|------|
| `app.py` | Streamlit 메인 앱 (3-패널: 사이드바 + 채팅 + 실행 로그) |
| `demo_mode.py` | Agent 미연결 시 샘플 데이터 기반 데모 모드 |
| `agentcore_client.py` | AWS AgentCore Runtime 조회/호출 클라이언트 |
| `cloudformation.yaml` | EC2 + S3 + IAM 워크샵 인프라 템플릿 |
| `data/` | 샘플 JSON 데이터 (점포, 매출, 날씨, 재고, 폐기율, 이벤트) |

## 배포

CloudFormation으로 EC2에 자동 배포됩니다:

```bash
aws cloudformation create-stack \
  --stack-name gs-retail-workshop \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

배포 후 `http://<EC2_Public_IP>:8501`로 접속하세요.

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```
