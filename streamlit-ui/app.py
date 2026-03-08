"""GS Retail AI Agent Workshop — Streamlit UI"""
import streamlit as st
import time, uuid, json
from demo_mode import demo_response

# ── 페이지 설정 ──
st.set_page_config(
    page_title="GS Retail AI Agent",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 커스텀 CSS ──
st.markdown("""<style>
/* 전체 배경 */
.stApp { background-color: #080b12; }
section[data-testid="stSidebar"] { background-color: #0d111c; border-right: 1px solid #1e2840; }
section[data-testid="stSidebar"] .stMarkdown { color: #dce6ff; }

/* 헤더 숨기기 */
header[data-testid="stHeader"] { background: #080b12; }

/* 채팅 메시지 스타일 */
.stChatMessage { background-color: #111826 !important; border: 1px solid #1e2840 !important; border-radius: 12px !important; }

/* 버튼 */
.stButton > button { border-radius: 8px; font-weight: 600; }

/* Agent 카드 */
.agent-card-st {
    background: #111826; border: 1.5px solid #1e2840; border-radius: 10px;
    padding: 14px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s;
}
.agent-card-st:hover { border-color: #263354; }
.agent-card-st.selected { border-color: #0046BE; background: rgba(0,70,190,0.06); }
.agent-card-st .ac-name { font-size: 14px; font-weight: 700; color: #dce6ff; }
.agent-card-st .ac-type { font-size: 10px; color: #5a6a90; text-transform: uppercase; letter-spacing: 0.08em; }
.agent-card-st .ac-desc { font-size: 12px; color: #5a6a90; margin-top: 4px; line-height: 1.5; }

/* 상태 뱃지 */
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700;
}
.status-badge.live { background: rgba(0,232,122,0.1); border: 1px solid rgba(0,232,122,0.25); color: #00e87a; }
.status-badge.waiting { background: rgba(255,208,96,0.1); border: 1px solid rgba(255,208,96,0.25); color: #ffd060; }
.status-badge.off { background: rgba(90,106,144,0.1); border: 1px solid rgba(90,106,144,0.25); color: #5a6a90; }

/* 로그 엔트리 */
.log-entry-st {
    font-family: 'JetBrains Mono', 'SF Mono', monospace; font-size: 11px;
    line-height: 1.6; padding: 2px 0;
}
.log-ts { color: #323d58; }
.log-tool { color: #FF9900; font-weight: 600; }
.log-agent { color: #a78bfa; font-weight: 600; }
.log-ok { color: #00e87a; font-weight: 600; }
.log-sys { color: #00d4ff; font-weight: 600; }

/* Tool chip */
.tool-chip-st {
    display: inline-block; padding: 2px 8px; margin: 2px;
    background: #161e30; border: 1px solid #263354; border-radius: 10px;
    font-family: monospace; font-size: 10px; color: #5a6a90;
}

/* 통계 바 */
.stat-box {
    text-align: center; padding: 8px; background: #111826;
    border: 1px solid #1e2840; border-radius: 8px;
}
.stat-val { font-family: monospace; font-size: 18px; font-weight: 700; color: #00e87a; }
.stat-lbl { font-size: 9px; color: #323d58; text-transform: uppercase; letter-spacing: 0.1em; }

/* ── 고정 우측 로그 패널 ── */
.fixed-log-panel {
    position: fixed; top: 56px; right: 0; bottom: 0; width: 260px;
    background: #0d111c; border-left: 1px solid #1e2840;
    display: flex; flex-direction: column; z-index: 999;
    padding: 0;
}
.fixed-log-panel .log-header {
    padding: 12px 14px; border-bottom: 1px solid #1e2840;
    display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}
.fixed-log-panel .log-header .lh-title {
    font-size: 11px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #5a6a90;
}
.fixed-log-panel .log-header .live-dot {
    width: 6px; height: 6px; border-radius: 50%; background: #00e87a;
    margin-left: auto; animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.fixed-log-panel .log-stats {
    display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
    padding: 10px 14px; border-bottom: 1px solid #1e2840; flex-shrink: 0;
}
.fixed-log-panel .log-scroll {
    flex: 1; overflow-y: auto; padding: 10px 12px;
    font-family: 'JetBrains Mono', 'SF Mono', monospace; font-size: 10.5px;
}
.fixed-log-panel .log-scroll::-webkit-scrollbar { width: 3px; }
.fixed-log-panel .log-scroll::-webkit-scrollbar-thumb { background: #263354; }

/* 메인 콘텐츠 우측 여백 확보 */
section.main .block-container { padding-right: 280px !important; }
@media(max-width:1100px) { .fixed-log-panel { display:none; } section.main .block-container { padding-right: 1rem !important; } }
</style>""", unsafe_allow_html=True)

# ── 세션 상태 초기화 ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "agent_mode" not in st.session_state:
    st.session_state.agent_mode = "demo"  # "demo" | "agentcore"
if "agent_arn" not in st.session_state:
    st.session_state.agent_arn = ""
if "agent_status" not in st.session_state:
    st.session_state.agent_status = "off"  # "off" | "connecting" | "ready"
if "agent_name" not in st.session_state:
    st.session_state.agent_name = ""
if "logs" not in st.session_state:
    st.session_state.logs = [
        {"ts": "00:00", "tag": "sys", "msg": "Workshop UI 시작됨"},
        {"ts": "00:00", "tag": "sys", "msg": "샘플 데이터 로드 대기 중..."},
    ]
if "tool_calls_count" not in st.session_state:
    st.session_state.tool_calls_count = 0
if "turns" not in st.session_state:
    st.session_state.turns = 0


def add_log(tag, msg):
    ts = time.strftime("%H:%M:%S")
    st.session_state.logs.append({"ts": ts, "tag": tag, "msg": msg})


def render_log_entry(entry):
    tag_class = {"tool": "log-tool", "agent": "log-agent", "ok": "log-ok", "sys": "log-sys"}.get(entry["tag"], "log-sys")
    tag_label = {"tool": "[TOOL]", "agent": "[AGNT]", "ok": "[OK]", "sys": "[SYS]"}.get(entry["tag"], "[LOG]")
    return f'<span class="log-ts">{entry["ts"]}</span> <span class="{tag_class}">{tag_label}</span> {entry["msg"]}'


# Tool 이름 → 이모지 매핑
TOOL_ICONS = {
    "query_sales_db": "📊", "weather_api": "🌤️", "calc_order_qty": "🧮",
    "submit_order": "📦", "query_waste_db": "🗑️", "scan_all_stores": "🔍",
    "detect_anomaly": "🚨", "get_inventory": "📦",
}


def _tool_status_html(done_tools, current=None, thinking=False):
    """Tool 실행 상태를 인라인 HTML로 생성"""
    lines = []
    if thinking and not done_tools and not current:
        return '<div style="padding:8px 0;font-size:13px;color:#5a6a90">🔍 요청을 분석하고 있어요...</div>'
    for tc in done_tools:
        icon = TOOL_ICONS.get(tc["tool"], "🔧")
        lines.append(
            f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:12.5px">'
            f'<span>{icon}</span>'
            f'<span style="color:#dce6ff">{tc["tool"]}</span>'
            f'<span style="color:#00e87a;margin-left:auto;font-size:11px">✅ {tc.get("output","")[:35]}</span>'
            f'</div>'
        )
    if current:
        icon = TOOL_ICONS.get(current["tool"], "🔧")
        lines.append(
            f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:12.5px">'
            f'<span>{icon}</span>'
            f'<span style="color:#ffd060">{current["tool"]}</span>'
            f'<span style="color:#ffd060;margin-left:auto;font-size:11px">⏳ 실행 중...</span>'
            f'</div>'
        )
    return '<div style="background:#111826;border:1px solid #1e2840;border-radius:8px;padding:8px 12px;margin:4px 0">' + "".join(lines) + '</div>'


def _stream_text(text):
    """텍스트를 스트리밍처럼 표시"""
    placeholder = st.empty()
    displayed = ""
    # 줄 단위로 스트리밍 (글자 단위보다 자연스럽고 빠름)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        displayed += line + ("\n" if i < len(lines) - 1 else "")
        placeholder.markdown(displayed)
        if line.strip():
            time.sleep(0.04)
    placeholder.markdown(text)


# ══════════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    # 로고
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#0046BE,#0060ff);border-radius:9px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:13px">GS</div>
        <div>
            <div style="font-size:15px;font-weight:700;color:#dce6ff"><span style="color:#0046BE">GS</span> Retail AI Agent</div>
            <div style="font-size:10px;color:#5a6a90">Workshop — Kiro × Strands × AgentCore</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Agent 상태 ──
    if st.session_state.agent_status == "ready":
        st.markdown('<div class="status-badge live">🟢 Agent Ready</div>', unsafe_allow_html=True)
    elif st.session_state.agent_status == "connecting":
        st.markdown('<div class="status-badge waiting">🟡 연결 중...</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge off">⚪ Agent 미연결</div>', unsafe_allow_html=True)

    st.markdown("")

    # ── Agent 연결 섹션 ──
    st.markdown("##### 🔗 Agent 연결")

    connect_method = st.radio(
        "연결 방법", ["수동 입력 (ARN)", "자동 검색"],
        horizontal=True, label_visibility="collapsed"
    )

    if connect_method == "수동 입력 (ARN)":
        arn_input = st.text_input(
            "Runtime ARN",
            value=st.session_state.agent_arn,
            placeholder="arn:aws:bedrock-agentcore:us-east-1:...",
            label_visibility="collapsed",
        )
        if arn_input != st.session_state.agent_arn:
            st.session_state.agent_arn = arn_input

    else:  # 자동 검색
        if st.button("🔍 배포된 Agent 검색", use_container_width=True):
            with st.spinner("AgentCore Runtime 검색 중..."):
                try:
                    from agentcore_client import list_agent_runtimes
                    runtimes = list_agent_runtimes()
                    if runtimes and "error" not in runtimes[0]:
                        st.session_state["discovered_runtimes"] = runtimes
                        add_log("sys", f"{len(runtimes)}개 Runtime 발견")
                    else:
                        st.warning(f"검색 실패: {runtimes[0].get('error', 'Unknown')}")
                        add_log("sys", "Runtime 검색 실패")
                except Exception as e:
                    st.warning(f"AWS 연결 실패: {e}")
                    add_log("sys", f"AWS 연결 실패: {e}")

        if "discovered_runtimes" in st.session_state:
            for rt in st.session_state.discovered_runtimes:
                if "error" in rt:
                    continue
                status_emoji = "🟢" if rt["status"] == "READY" else "🟡"
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{status_emoji} {rt['name']}**<br><span style='font-size:10px;color:#5a6a90'>{rt['status']}</span>", unsafe_allow_html=True)
                with col2:
                    if st.button("가져오기", key=f"import_{rt['arn'][:20]}"):
                        st.session_state.agent_arn = rt["arn"]
                        st.session_state.agent_name = rt["name"]
                        add_log("sys", f"Agent 선택: {rt['name']}")

    # 연결 버튼
    if st.session_state.agent_arn:
        if st.session_state.agent_status != "ready":
            if st.button("⚡ Agent 연결하기", type="primary", use_container_width=True):
                st.session_state.agent_status = "connecting"
                add_log("sys", "AgentCore 연결 시도...")
                with st.spinner("Runtime 검증 중..."):
                    try:
                        from agentcore_client import validate_runtime
                        result = validate_runtime(st.session_state.agent_arn)
                        if result.get("valid") and result.get("ready"):
                            st.session_state.agent_status = "ready"
                            st.session_state.agent_mode = "agentcore"
                            st.session_state.agent_name = result.get("name", st.session_state.agent_arn.split("/")[-1])
                            add_log("ok", f"Agent 연결 완료: {st.session_state.agent_name} (READY)")
                            st.rerun()
                        elif result.get("valid"):
                            st.session_state.agent_status = "off"
                            st.warning(f"Runtime 상태: {result.get('status')} — READY가 아닙니다. 배포 완료를 기다려주세요.")
                            add_log("sys", f"Runtime 상태: {result.get('status')}")
                        else:
                            st.session_state.agent_status = "off"
                            st.error(f"검증 실패: {result.get('error')}")
                            add_log("sys", f"검증 실패: {result.get('error')}")
                    except Exception as e:
                        st.session_state.agent_status = "off"
                        st.error(f"AWS 연결 실패: {e}")
                        add_log("sys", f"AWS 연결 실패: {e}")
        else:
            if st.button("🔌 연결 해제", use_container_width=True):
                st.session_state.agent_status = "off"
                st.session_state.agent_mode = "demo"
                add_log("sys", "Agent 연결 해제됨")
                st.rerun()

    st.divider()

    # ── 현재 모드 표시 ──
    if st.session_state.agent_mode == "agentcore":
        st.markdown(f"""
        <div style="background:rgba(0,70,190,0.08);border:1px solid rgba(0,70,190,0.25);border-radius:8px;padding:10px">
            <div style="font-size:11px;color:#0046BE;font-weight:700;text-transform:uppercase;letter-spacing:0.08em">🤖 연결된 Agent</div>
            <div style="font-size:13px;font-weight:700;color:#dce6ff;margin-top:4px">{st.session_state.agent_name}</div>
            <div style="font-size:10px;color:#5a6a90;margin-top:2px">AgentCore · Strands SDK · Bedrock</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:rgba(255,208,96,0.06);border:1px solid rgba(255,208,96,0.2);border-radius:8px;padding:10px">
            <div style="font-size:11px;color:#ffd060;font-weight:700">💬 데모 모드</div>
            <div style="font-size:11px;color:#5a6a90;margin-top:4px">샘플 데이터 기반 시뮬레이션<br>Agent를 배포하면 실제 AgentCore로 전환됩니다</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── 빠른 질문 ──
    st.markdown("##### 💬 빠른 질문")
    quick_qs = [
        "역삼역점 내일 발주 해줘",
        "잠실새내점 폐기율 어때?",
        "이번주 이상 점포 있어?",
        "테헤란로점 금요일 발주인데 음료 많이 시켜줘",
    ]
    for q in quick_qs:
        if st.button(q, key=f"qq_{q[:10]}", use_container_width=True):
            st.session_state["pending_question"] = q
            st.rerun()

    st.divider()

    # ── 세션 관리 ──
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.turns = 0
        st.session_state.tool_calls_count = 0
        st.session_state.logs = [{"ts": time.strftime("%H:%M:%S"), "tag": "sys", "msg": "대화 초기화됨"}]
        st.rerun()


# ══════════════════════════════════════════════════════════════
# 메인 영역 — 채팅 + 고정 로그 패널
# ══════════════════════════════════════════════════════════════

# ── 고정 우측 로그 패널 (HTML로 렌더링) ──
log_entries_html = ""
for entry in reversed(st.session_state.logs[-50:]):
    log_entries_html += f'<div class="log-entry-st">{render_log_entry(entry)}</div>'

st.markdown(f"""
<div class="fixed-log-panel">
    <div class="log-header">
        <span class="lh-title">Agent 실행 로그</span>
        <span class="live-dot"></span>
    </div>
    <div class="log-stats">
        <div class="stat-box"><div class="stat-val">{st.session_state.tool_calls_count}</div><div class="stat-lbl">Tool Calls</div></div>
        <div class="stat-box"><div class="stat-val">{st.session_state.turns}</div><div class="stat-lbl">Turns</div></div>
    </div>
    <div class="log-scroll" id="logScroll">{log_entries_html}</div>
</div>
<script>
    var el = document.getElementById('logScroll');
    if(el) el.scrollTop = 0;
</script>
""", unsafe_allow_html=True)

# ── 채팅 영역 ──
# 헤더
mode_label = f"🤖 {st.session_state.agent_name}" if st.session_state.agent_mode == "agentcore" else "💬 GS25 발주 도우미 (데모)"
status_label = "AgentCore 연결됨" if st.session_state.agent_mode == "agentcore" else "샘플 데이터 모드"
st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;padding:8px 0;margin-bottom:8px">
    <div style="width:40px;height:40px;background:rgba(0,70,190,0.15);border:1px solid rgba(0,70,190,0.3);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px">📦</div>
    <div>
        <div style="font-size:15px;font-weight:700;color:#dce6ff">{mode_label}</div>
        <div style="font-size:11px;color:{'#00e87a' if st.session_state.agent_mode == 'agentcore' else '#5a6a90'}">{status_label}</div>
    </div>
    <div style="margin-left:auto;display:flex;gap:6px">
        <span style="padding:3px 9px;border-radius:10px;font-size:10px;font-weight:700;background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.25);color:#a78bfa;font-family:monospace">Strands SDK</span>
        <span style="padding:3px 9px;border-radius:10px;font-size:10px;font-weight:700;background:rgba(255,153,0,0.1);border:1px solid rgba(255,153,0,0.25);color:#FF9900;font-family:monospace">AgentCore</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 메시지 표시
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:80px 40px;color:#323d58">
        <div style="font-size:48px;opacity:0.3;margin-bottom:12px">🤖</div>
        <div style="font-size:18px;font-weight:700;color:#5a6a90;margin-bottom:8px">GS25 발주 자동화 Agent</div>
        <div style="font-size:13px;color:#323d58;line-height:1.8">
            왼쪽 사이드바에서 Agent를 연결하거나<br>
            아래 입력창에 질문을 입력해보세요<br><br>
            <span style="color:#5a6a90">Agent 미연결 시 샘플 데이터 기반 데모로 동작합니다</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "📦"):
        st.markdown(msg["content"])
        if msg.get("tool_calls"):
            with st.expander(f"🔧 Agent가 사용한 도구 ({len(msg['tool_calls'])}개)", expanded=False):
                for tc in msg["tool_calls"]:
                    st.markdown(f"""<div style="background:#0d111c;border:1px solid #263354;border-radius:6px;padding:8px 10px;margin:4px 0;font-family:monospace;font-size:11px">
                    <span style="color:#FF9900;font-weight:700">{tc['tool']}</span>
                    <span style="color:#323d58">→</span>
                    <span style="color:#00e87a">✓ done</span>
                    <span style="color:#323d58;margin-left:8px">{tc.get('time','')}</span>
                    <br><span style="color:#00d4ff">{tc.get('input','')}</span>
                    <br><span style="color:#00e87a">{tc.get('output','')}</span>
                    </div>""", unsafe_allow_html=True)

# 입력 처리
pending = st.session_state.pop("pending_question", None)
prompt = st.chat_input("메시지를 입력하세요...", key="chat_input")
user_input = pending or prompt

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.turns += 1
    add_log("agent", f"User: {user_input[:40]}...")

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="📦"):
        # Tool 실행 상태를 순차 표시할 placeholder
        status_area = st.empty()
        add_log("agent", "Analyzing request...")

        # Agent 호출
        if st.session_state.agent_mode == "agentcore" and st.session_state.agent_status == "ready":
            # 실제 AgentCore — 호출 전 "분석 중" 표시
            status_area.markdown(_tool_status_html([], thinking=True), unsafe_allow_html=True)
            try:
                from agentcore_client import invoke_agent
                result = invoke_agent(
                    st.session_state.agent_arn, user_input, st.session_state.session_id,
                )
            except Exception as e:
                result = {"text": f"❌ Agent 호출 실패: {e}", "tool_calls": []}
            # AgentCore 응답의 tool_calls도 순차 표시
            tool_calls = result.get("tool_calls", [])
            for i, tc in enumerate(tool_calls):
                status_area.markdown(
                    _tool_status_html(tool_calls[:i], current=tc),
                    unsafe_allow_html=True
                )
                time.sleep(0.3)
            if tool_calls:
                status_area.markdown(_tool_status_html(tool_calls), unsafe_allow_html=True)
                time.sleep(0.2)
        else:
            # 데모 모드 — Tool 하나씩 순차 표시
            result = demo_response(user_input)
            tool_calls = result.get("tool_calls", [])
            for i, tc in enumerate(tool_calls):
                # 현재까지 완료된 것 + 진행 중인 것 표시
                status_area.markdown(
                    _tool_status_html(tool_calls[:i], current=tc),
                    unsafe_allow_html=True
                )
                time.sleep(0.5 + 0.3 * (i % 2))
            # 전부 완료 표시
            if tool_calls:
                status_area.markdown(
                    _tool_status_html(tool_calls, current=None),
                    unsafe_allow_html=True
                )
                time.sleep(0.3)

        # Tool call 로그 기록
        for tc in result.get("tool_calls", []):
            add_log("tool", f"{tc['tool']} → {tc.get('output', '')[:50]}")
            st.session_state.tool_calls_count += 1
        add_log("ok", "Response sent")

        # 상태 영역을 최종 결과로 교체
        status_area.empty()

        # 최종 응답 스트리밍 표시
        _stream_text(result["text"])

        # Tool call 상세 (접기)
        if result.get("tool_calls"):
            with st.expander(f"🔧 사용된 도구 ({len(result['tool_calls'])}개)", expanded=False):
                for tc in result["tool_calls"]:
                    st.markdown(f"""<div style="background:#0d111c;border:1px solid #263354;border-radius:6px;padding:8px 10px;margin:4px 0;font-family:monospace;font-size:11px">
                    <span style="color:#FF9900;font-weight:700">{tc['tool']}</span>
                    <span style="color:#323d58">→</span>
                    <span style="color:#00e87a">✓ done</span>
                    <span style="color:#323d58;margin-left:8px">{tc.get('time','')}</span>
                    <br><span style="color:#00d4ff">{tc.get('input','')}</span>
                    <br><span style="color:#00e87a">{tc.get('output','')}</span>
                    </div>""", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant", "content": result["text"],
        "tool_calls": result.get("tool_calls", []),
    })
    st.rerun()
