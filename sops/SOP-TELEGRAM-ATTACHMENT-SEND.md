# SOP-TELEGRAM-ATTACHMENT-SEND

Use this when SpongeBot needs to send a real file attachment to Telegram.

## Rule
Do **not** rely on session relay for Telegram attachment delivery.
Use the direct CLI send path and verify plugin JSON success.

## Exact working method
1. Put the outbound file under an allowed media root:
   - Recommended: `/data/.openclaw/media/outbound/`
2. Send with `openclaw message send`:

```bash
mkdir -p /data/.openclaw/media/outbound
cp /data/workspace/SOUL.md /data/.openclaw/media/outbound/SOUL.md
openclaw message send \
  --channel telegram \
  --target 171900099 \
  --message 'Attached: SOUL.md' \
  --media /data/.openclaw/media/outbound/SOUL.md \
  --json
```

## Success proof
Treat it as successful only if JSON includes all of:
- `"action": "send"`
- `"handledBy": "plugin"`
- `payload.ok: true`
- expected `payload.chatId`
- real `payload.messageId`

## Failure mode already seen
This failed:

```bash
openclaw message send --channel telegram --target 171900099 \
  --message 'Attached: SOUL.md' --media /data/workspace/SOUL.md --json
```

Error:

```text
LocalMediaAccessError: Local media path is not under an allowed directory: /data/workspace/SOUL.md
```

## Notes
- `/data/workspace/...` is **not** an allowed outbound local media root for this CLI path.
- `/data/.openclaw/media/...` is allowed and worked.
- Keep attachment sends on the direct Telegram CLI path for reliable proof.

Last verified: 2026-03-13
Verified target: Telegram DM `171900099`
Verified file: `SOUL.md`
Verified result: `messageId 3604`
