import os, re, json, subprocess
from datetime import datetime, date
from zoneinfo import ZoneInfo
import fitz

PDF_PATH = "/data/.openclaw/media/inbound/file_33---c18cef8d-3b52-4c8a-9e88-ca22a7aa0124.pdf"
OUT_DIR = "/data/workspace/tmp/batch_pdf_20260303"
IMG_DIR = os.path.join(OUT_DIR, "images")
SHEET_ID = "14x95k1XSJwrQpzx8NcLoCdWZC5ZBSyLexmWEq-9S6yE"
SHEET_RANGE = "Invoices!A:G"

os.makedirs(IMG_DIR, exist_ok=True)

# Regex
DATE_STRICT = re.compile(r"\b(\d{1,2})[-/\.](\d{1,2})[-/\.](\d{2,4})\b")
DATE_LOOSE = re.compile(r"(\d{1,2})\D{1,4}(\d{1,2})\D{1,4}(\d{2,4})")
MONEY_RE = re.compile(r"(?<!\d)(\d{1,3}(?:[\.,\s]\d{3})+|\d{4,})(?!\d)")

KEYWORDS_TOTAL = [
    "thanh toan", "thanh toán", "tổng", "tong", "total", "grand total",
    "tien thanh toan", "tiền thanh toán", "tien thanh", "tiền thanh", "thành tiền",
    "amount due", "amount"
]


def run_cmd(cmd: list[str], env=None) -> str:
    p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
    return p.stdout.strip()


def norm_int(s: str):
    s = s.strip().replace(" ", "").replace(".", "").replace(",", "")
    try:
        return int(s)
    except Exception:
        return None


def detect_currency(text: str):
    t = text.lower()
    if "thb" in t or "฿" in t:
        return "THB"
    if "usd" in t or "$" in t:
        return "USD"
    if "khr" in t or "៛" in t:
        return "KHR"
    if "vnd" in t or "vnđ" in t or "đ" in t:
        return "VND"
    return "VND"


def parse_dates_from_lines(lines, rx):
    cands = []
    for idx, ln in enumerate(lines):
        for m in rx.finditer(ln):
            d, mn, y = m.group(1), m.group(2), m.group(3)
            try:
                y = int(y)
                if y < 100:
                    y += 2000
                dt = date(y, int(mn), int(d))
            except Exception:
                continue
            score = 0
            lnu = ln.lower()
            if any(k in lnu for k in ["ngay", "ngày", "date", "sale date", "giovao", "gio vao", "giờ vào", "ngiy"]):
                score += 3
            if idx < 10:
                score += 1
            cands.append((score, dt, m.group(0), ln))
    if not cands:
        return None
    cands.sort(key=lambda x: (-x[0], x[1]))
    return cands[0]


def pick_date(text: str):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    res = parse_dates_from_lines(lines, DATE_STRICT)
    if res:
        return res
    return parse_dates_from_lines(lines, DATE_LOOSE)


def pick_total(text: str):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    def line_weight(ln: str):
        l = ln.lower()
        if any(k in l for k in KEYWORDS_TOTAL):
            return 3
        return 1

    amounts = []
    for i, ln in enumerate(lines):
        w = line_weight(ln)
        if w == 3:
            candidates = [ln]
            if i + 1 < len(lines):
                candidates.append(lines[i + 1])
            for cln in candidates:
                lcln = cln.lower()
                # skip common ID/VAT lines
                if "vat" in lcln and "total" not in lcln:
                    continue
                if "tin" in lcln and "total" not in lcln:
                    continue
                for m in MONEY_RE.finditer(cln):
                    raw = m.group(1)
                    val = norm_int(raw)
                    if val is None or val < 1000:
                        continue
                    # sanity cap (avoid picking IDs)
                    if val > 200_000_000:
                        continue
                    amounts.append((w, val, raw, cln))

    # fallback: if none, take best numeric from whole text but still cap
    if not amounts:
        for ln in lines:
            lcln = ln.lower()
            if "vat" in lcln or "tin" in lcln:
                continue
            for m in MONEY_RE.finditer(ln):
                raw = m.group(1)
                val = norm_int(raw)
                if val is None or val < 1000 or val > 200_000_000:
                    continue
                amounts.append((1, val, raw, ln))

    if not amounts:
        return None
    amounts.sort(key=lambda x: (-x[0], -x[1]))
    return amounts[0]


def restore_gog_auth():
    env = os.environ.copy()
    env["PATH"] = "/home/linuxbrew/.linuxbrew/bin:" + env.get("PATH", "")
    env["GOG_KEYRING_PASSWORD"] = "openclaw_secure_2026"
    # idempotent
    subprocess.run(["gog", "auth", "credentials", "set", "/data/workspace/gog_client_secret.json", "--no-input"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["gog", "auth", "tokens", "import", "/data/workspace/gog_auth_backup.json", "--no-input"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def gog_drive_upload(local_path: str, name: str):
    env = os.environ.copy()
    env["PATH"] = "/home/linuxbrew/.linuxbrew/bin:" + env.get("PATH", "")
    env["GOG_KEYRING_PASSWORD"] = "openclaw_secure_2026"
    out = run_cmd(["gog", "drive", "upload", local_path, "--name", name, "--json", "--no-input"], env=env)
    j = json.loads(out)
    f = j.get("file", {})
    return f.get("id"), f.get("webViewLink")


def gog_sheets_append(values_2d):
    env = os.environ.copy()
    env["PATH"] = "/home/linuxbrew/.linuxbrew/bin:" + env.get("PATH", "")
    env["GOG_KEYRING_PASSWORD"] = "openclaw_secure_2026"
    payload = json.dumps(values_2d, ensure_ascii=False)
    out = run_cmd([
        "gog", "sheets", "append", SHEET_ID, SHEET_RANGE,
        "--values-json", payload,
        "--insert", "INSERT_ROWS",
        "--input", "USER_ENTERED",
        "--no-input", "--json"
    ], env=env)
    return json.loads(out)


def main():
    restore_gog_auth()

    doc = fitz.open(PDF_PATH)
    now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S")

    extracted = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text("text") or ""

        currency = detect_currency(text)
        dres = pick_date(text)
        tres = pick_total(text)

        invoice_date_iso = ""
        invoice_date_raw = ""
        if dres:
            _score, dt, raw, _ln = dres
            invoice_date_iso = dt.isoformat()
            invoice_date_raw = raw

        value = ""
        value_raw = ""
        if tres:
            _w, val, raw, _ln = tres
            value = str(val)
            value_raw = raw

        # render page image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        img_path = os.path.join(IMG_DIR, f"invoice_page_{i+1:02d}.png")
        pix.save(img_path)

        extracted.append({
            "page": i + 1,
            "invoice_date_iso": invoice_date_iso,
            "invoice_date_raw": invoice_date_raw,
            "value": value,
            "value_raw": value_raw,
            "currency": currency,
            "img_path": img_path,
            "text_len": len(text),
        })

    # upload images to Drive + build rows for Sheets
    rows = []
    for item in extracted:
        page_no = item["page"]
        name = f"batch_pdf_2026-03-03_page_{page_no:02d}.png"
        fid, url = gog_drive_upload(item["img_path"], name)

        # For batch test we do not have description/expense_account from user.
        # Store placeholders; Boss can decide later if we want inference.
        metadata = {
            "source": "batch_pdf",
            "pdf_pages": 24,
            "page": page_no,
            "drive_file_id": fid,
            "drive_url": url,
            "description": "",
            "expense_account": "",
            "extracted_invoice_date_raw": item["invoice_date_raw"],
            "extracted_value_raw": item["value_raw"],
            "needs_manual_date": (item["invoice_date_iso"] == ""),
            "needs_manual_review": (item["invoice_date_iso"] == ""),
        }

        rows.append([
            item["invoice_date_iso"],
            now,
            "",  # vendor not extracted
            item["value"],
            item["currency"],
            json.dumps(metadata, ensure_ascii=False),
            "FALSE"
        ])

    # append to sheet
    append_res = gog_sheets_append(rows)

    # write extracted.json
    out_json = os.path.join(OUT_DIR, "extracted.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"append_result": append_res, "items": extracted}, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "pages": doc.page_count,
        "sheet_append": append_res,
        "out_json": out_json,
        "missing_date": sum(1 for x in extracted if x["invoice_date_iso"] == ""),
        "missing_value": sum(1 for x in extracted if x["value"] == ""),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
