#!/usr/bin/env python3
"""Dust relay: send a prompt to a Dust agent and print the final answer.

Usage:
  DUST_API_KEY=... python3 dust_relay.py --workspace Jb3tKIEjjE --agent-handle @lc-main --prompt "..."

Supports Dust agent streaming via SSE and (optionally) auto-approves tool executions.

Important: Dust event streams can end before we see a terminal event. This relay implements:
- reconnection using ?lastEventId=
- fallback fetch of the conversation to grab the final agent message content

Relevant API refs:
- POST /api/v1/w/{wId}/assistant/conversations
- GET  /api/v1/w/{wId}/assistant/agent_configurations
- GET  /api/v1/w/{wId}/assistant/conversations/{cId}  (fallback)
- GET  /api/v1/w/{wId}/assistant/conversations/{cId}/messages/{mId}/events  (SSE)
- POST /api/v1/w/{wId}/assistant/conversations/{cId}/messages/{mId}/validate-action
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from typing import Generator, List, Optional, Tuple


BASE_URL_DEFAULT = "https://dust.tt"


def http_json(
    method: str,
    url: str,
    api_key: str,
    body: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = 60,
) -> dict:
    h = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if headers:
        h.update(headers)

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url=url, method=method, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError(f"Non-JSON response from {url}: {raw[:200]}")


def sse_stream(url: str, api_key: str, timeout: int = 900) -> Generator[dict, None, None]:
    """Yield decoded JSON payloads from SSE `data:` messages."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    }
    req = urllib.request.Request(url=url, method="GET", headers=headers)

    # urlopen timeout here is the *socket inactivity timeout*.
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        buffer: List[str] = []
        while True:
            line_b = resp.readline()
            if not line_b:
                break
            line = line_b.decode("utf-8", errors="replace").rstrip("\r\n")

            # Blank line => end of SSE event.
            if line == "":
                if buffer:
                    data_lines = [
                        l[len("data:"):].lstrip() for l in buffer if l.startswith("data:")
                    ]
                    buffer = []
                    if not data_lines:
                        continue
                    data_str = "\n".join(data_lines)
                    try:
                        yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                continue

            buffer.append(line)


def find_agent_configuration_id(agents: List[dict], handle: str) -> str:
    target = handle.lstrip("@").lower()
    for a in agents:
        h = (a.get("handle") or "").lstrip("@").lower()
        if h == target:
            return a["sId"]
    for a in agents:
        n = (a.get("name") or "").lower()
        if n == target:
            return a["sId"]
    raise RuntimeError(f"Agent handle not found: {handle}")


def find_agent_message_id(conversation: dict, user_message_id: str) -> str:
    content = conversation.get("content") or []
    for versions in content:
        if not isinstance(versions, list) or not versions:
            continue
        m = versions[-1]
        if not isinstance(m, dict):
            continue
        if m.get("type") == "agent_message" and m.get("parentMessageId") == user_message_id:
            return m.get("sId")
    raise RuntimeError("Failed to locate agent message in conversation content")


def extract_agent_message_content(conversation: dict, user_message_id: str) -> Optional[str]:
    """Best-effort: find the latest agent message content for this user message."""
    content = conversation.get("content") or []
    best: Optional[str] = None
    for versions in content:
        if not isinstance(versions, list) or not versions:
            continue
        m = versions[-1]
        if not isinstance(m, dict):
            continue
        if m.get("type") != "agent_message":
            continue
        if m.get("parentMessageId") != user_message_id:
            continue
        c = m.get("content")
        if isinstance(c, str) and c.strip():
            best = c
    return best


def validate_action(
    *,
    base_url: str,
    workspace_id: str,
    api_key: str,
    conversation_id: str,
    message_id: str,
    action_id: str,
    approved: bool,
) -> None:
    url = (
        f"{base_url}/api/v1/w/{workspace_id}/assistant/conversations/{conversation_id}"
        f"/messages/{message_id}/validate-action"
    )
    http_json(
        "POST",
        url,
        api_key,
        body={"actionId": action_id, "approved": approved},
        timeout=60,
    )


def get_conversation(*, base_url: str, workspace_id: str, api_key: str, conversation_id: str) -> dict:
    url = f"{base_url}/api/v1/w/{workspace_id}/assistant/conversations/{conversation_id}"
    return http_json("GET", url, api_key, timeout=60)


def run(
    *,
    workspace_id: str,
    api_key: str,
    agent_handle: str,
    prompt: str,
    base_url: str = BASE_URL_DEFAULT,
    timezone: str = "UTC",
    auto_approve_tools: bool = True,
    max_reconnects: int = 8,
    reconnect_delay_s: float = 5.0,
) -> str:
    # 1) Resolve agent configurationId (sId)
    agents_url = f"{base_url}/api/v1/w/{workspace_id}/assistant/agent_configurations"
    agents_resp = http_json("GET", agents_url, api_key)

    agents = (
        agents_resp.get("agentConfigurations")
        or agents_resp.get("data")
        or agents_resp.get("agents")
        or agents_resp.get("agent_configurations")
    )

    if agents is None and isinstance(agents_resp, list):
        agents = agents_resp

    if not isinstance(agents, list):
        raise RuntimeError("Unexpected agents response shape")

    agent_id = find_agent_configuration_id(agents, agent_handle)

    # 2) Create conversation + initial user message mentioning agent
    conv_url = f"{base_url}/api/v1/w/{workspace_id}/assistant/conversations"
    body = {
        "title": None,
        "visibility": "unlisted",
        "message": {
            "content": prompt,
            "mentions": [{"configurationId": agent_id}],
            "context": {
                "timezone": timezone,
                "origin": "api",
                "username": "openclaw",
            },
        },
    }
    conv_resp = http_json("POST", conv_url, api_key, body=body)

    conversation = conv_resp.get("conversation") or conv_resp.get("data", {}).get("conversation")
    user_message = conv_resp.get("message") or conv_resp.get("data", {}).get("message")

    if not conversation or not user_message:
        raise RuntimeError("Unexpected createConversation response; missing conversation/message")

    conversation_id = conversation.get("sId")
    user_message_id = user_message.get("sId")
    if not conversation_id or not user_message_id:
        raise RuntimeError("Missing conversation_id/user_message_id")

    agent_message_id = find_agent_message_id(conversation, user_message_id)

    # 3) Stream agent message events (SSE) with reconnection
    base_events_url = (
        f"{base_url}/api/v1/w/{workspace_id}/assistant/conversations/{conversation_id}"
        f"/messages/{agent_message_id}/events"
    )

    terminal = {
        "agent_message_success",
        "agent_error",
        "agent_generation_cancelled",
        "user_message_error",
    }

    answer = ""
    saw_terminal = False
    last_event_id: Optional[str] = None

    reconnects = 0

    while True:
        events_url = base_events_url
        if last_event_id:
            events_url += "?" + urllib.parse.urlencode({"lastEventId": last_event_id})

        try:
            for event_blob in sse_stream(events_url, api_key, timeout=900):
                # Dust wraps as { eventId, data: { ...event... } }
                if isinstance(event_blob, dict) and isinstance(event_blob.get("eventId"), str):
                    last_event_id = event_blob.get("eventId")

                data = event_blob.get("data") if isinstance(event_blob, dict) else None
                if not isinstance(data, dict):
                    continue

                etype = data.get("type")

                # Auto-approve tool executions when requested.
                if etype == "mcp_approve_execution" and auto_approve_tools:
                    message_id = data.get("messageId")
                    action_id = data.get("actionId")
                    if message_id and action_id:
                        validate_action(
                            base_url=base_url,
                            workspace_id=workspace_id,
                            api_key=api_key,
                            conversation_id=conversation_id,
                            message_id=message_id,
                            action_id=action_id,
                            approved=True,
                        )
                    continue

                # We prefer final message content, not partial tokens.
                if etype == "agent_message_success":
                    msg = data.get("message") or {}
                    content = msg.get("content")
                    if isinstance(content, str) and content.strip():
                        answer = content
                    saw_terminal = True
                    break

                if etype in terminal:
                    saw_terminal = True
                    break

            if saw_terminal:
                break

        except Exception:
            # fall through to reconnect policy
            pass

        reconnects += 1
        if reconnects > max_reconnects:
            break
        time.sleep(reconnect_delay_s)

    # Fallback: fetch the conversation to grab final content.
    if not answer.strip():
        conv = get_conversation(
            base_url=base_url,
            workspace_id=workspace_id,
            api_key=api_key,
            conversation_id=conversation_id,
        )
        # Depending on API shape, conversation may be direct or nested.
        conv_obj = conv.get("conversation") if isinstance(conv, dict) else None
        if not isinstance(conv_obj, dict):
            conv_obj = conv
        c = extract_agent_message_content(conv_obj, user_message_id)
        if c:
            answer = c

    return answer.strip()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", required=True)
    p.add_argument("--agent-handle", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--base-url", default=BASE_URL_DEFAULT)
    p.add_argument("--timezone", default="UTC")
    p.add_argument("--no-auto-approve-tools", action="store_true")
    args = p.parse_args()

    api_key = os.environ.get("DUST_API_KEY")
    if not api_key:
        print("ERROR: DUST_API_KEY env var is required", file=sys.stderr)
        return 2

    try:
        ans = run(
            workspace_id=args.workspace,
            api_key=api_key,
            agent_handle=args.agent_handle,
            prompt=args.prompt,
            base_url=args.base_url,
            timezone=args.timezone,
            auto_approve_tools=not args.no_auto_approve_tools,
        )
        print(ans)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
