"""AgentCore 클라이언트 — Runtime 조회 및 Agent 호출"""
import json
import time
import boto3
from botocore.exceptions import ClientError


def validate_runtime(runtime_arn, region="us-east-1"):
    """Runtime ARN이 유효하고 READY 상태인지 검증"""
    try:
        client = boto3.client(
            "bedrock-agentcore", region_name=region,
            endpoint_url=f"https://bedrock-agentcore.{region}.amazonaws.com"
        )
        resp = client.get_agent_runtime(agentRuntimeArn=runtime_arn)
        status = resp.get("status", "UNKNOWN")
        name = resp.get("agentRuntimeName", "Unknown")
        return {"valid": True, "status": status, "name": name, "ready": status == "READY"}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        return {"valid": False, "error": f"{code}: {msg}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def list_agent_runtimes(region="us-east-1"):
    """배포된 AgentCore Runtime 목록 조회"""
    try:
        client = boto3.client(
            "bedrock-agentcore", region_name=region,
            endpoint_url=f"https://bedrock-agentcore.{region}.amazonaws.com"
        )
        resp = client.list_agent_runtimes()
        runtimes = []
        for rt in resp.get("agentRuntimeSummaries", []):
            runtimes.append({
                "arn": rt.get("agentRuntimeArn", ""),
                "name": rt.get("agentRuntimeName", "Unknown"),
                "status": rt.get("status", "UNKNOWN"),
            })
        return runtimes
    except Exception as e:
        return [{"error": str(e)}]


def invoke_agent(runtime_arn, message, session_id, region="us-east-1"):
    """AgentCore Runtime에 메시지 전송 및 응답 수신"""
    try:
        client = boto3.client(
            "bedrock-agentcore", region_name=region,
            endpoint_url=f"https://bedrock-agentcore.{region}.amazonaws.com"
        )
        resp = client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            agentRuntimeEndpointName="DEFAULT",
            payload=json.dumps({
                "query": message,
                "session_id": session_id,
            }),
        )
        # 스트리밍 응답 파싱
        body = resp.get("body", b"")
        if hasattr(body, "read"):
            body = body.read()
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        return parse_agent_response(body)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        return {"text": f"❌ AWS 오류: {code} — {msg}", "tool_calls": []}
    except Exception as e:
        return {"text": f"❌ Agent 호출 실패: {str(e)}", "tool_calls": []}


def parse_agent_response(raw):
    """Agent 응답에서 텍스트와 tool call 정보 추출"""
    tool_calls = []
    text_parts = []
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            text_parts.append(data.get("response", data.get("output", raw)))
            for tc in data.get("tool_calls", data.get("toolUse", [])):
                tool_calls.append({
                    "tool": tc.get("name", tc.get("tool", "unknown")),
                    "input": json.dumps(tc.get("input", {}), ensure_ascii=False)[:80],
                    "output": tc.get("output", tc.get("result", ""))[:100],
                    "time": tc.get("duration", "0.3s"),
                })
    except (json.JSONDecodeError, TypeError):
        text_parts.append(str(raw))
    return {"text": "\n".join(text_parts) or raw, "tool_calls": tool_calls}
