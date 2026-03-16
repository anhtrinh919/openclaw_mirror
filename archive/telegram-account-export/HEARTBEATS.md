# How This Enables Future Heartbeats

The export design is built to make OpenClaw heartbeats cheap, reliable, and relationship-aware.

## Core idea

Heartbeats should almost never read raw Telegram history directly.

Instead:
1. daily export writes canonical message events
2. lightweight derivation jobs compress those events into heartbeat-friendly inputs
3. OpenClaw heartbeats read the derived inputs and only drill into raw chat lines when needed

## Heartbeats this unlocks well

### 1) Daily Telegram summary

From `derived/daily-summary-input.json`, OpenClaw can answer:
- which chats mattered today
- who sent the most important inbound messages
- what commitments Boss made
- what open threads remain
- which messages included documents, links, or decisions

### 2) People follow-through heartbeat

From `derived/follow-through-candidates.json`, OpenClaw can track:
- **Boss owes someone something**
  - “I’ll send the deck tonight.”
  - “Let me check and get back to you.”
- **Someone owes Boss something**
  - “I’ll send it tomorrow.”
  - “Will update you after the meeting.”
- **Unanswered inbound**
  - important direct messages with no outbound reply after a threshold
- **Stale commitments**
  - promises with a time reference that are past due and not clearly resolved

## Why sender + direction matter so much

People follow-through is mostly about this question:

```text
Who owes the next action?
```

That becomes much easier when each event already says:
- who sent it (`sender`)
- whether it is inbound or outbound (`direction`)
- whether it contains a commitment or follow-up cue (`derived`)

## Suggested future heartbeat outputs

### A. Boss follow-through digest

Compact output example:

```json
{
  "date": "2026-03-13",
  "you_owe": [
    {
      "chat_key": "direct-alice-nguyen",
      "counterparty": "Alice Nguyen",
      "message_uid": "tgacct:boss-main:chat:123:msg:55",
      "commitment_text": "I’ll send you the revised deck before 5pm.",
      "due_hint": "before 5pm",
      "status": "open"
    }
  ],
  "others_owe_you": [
    {
      "chat_key": "group-vendor-x",
      "counterparty": "Vendor X",
      "message_uid": "tgacct:boss-main:chat:222:msg:91",
      "commitment_text": "We’ll revert with pricing tomorrow.",
      "due_hint": "tomorrow",
      "status": "waiting"
    }
  ],
  "unanswered_priority_inbound": []
}
```

### B. Relationship heartbeat

Useful for personal CRM-style nudges:
- people with active back-and-forth this week
- people waiting on Boss
- people who promised updates but went silent
- people not contacted for N days

## Minimum derivation logic needed

A strong v1 does **not** need full NLP. Simple heuristics already help:

- commitment phrases:
  - `i'll`, `i will`, `let me`, `will send`, `will update`, `get back to`, `mai`, `ngày mai`, `để mình`, `mình sẽ`, `em sẽ`, `anh sẽ`
- question signals:
  - `?`, `can you`, `when`, `where`, `gửi`, `được không`, `bao giờ`
- time references:
  - `today`, `tomorrow`, `tonight`, `before 5`, `this afternoon`, `mai`, `chiều nay`, `tối nay`
- resolution signals:
  - later outbound message with attachment/link/reply mentioning the promised object

## Practical heartbeat architecture

Recommended daily pipeline:

```text
Telegram exporter
  -> all-chats.jsonl
  -> summary/follow-through derivation scripts
  -> heartbeat reads derived JSON
  -> optional Telegram morning/evening brief
```

This keeps heartbeat prompts small, repeatable, and cheaper than asking the model to rediscover structure from raw chat logs every day.
