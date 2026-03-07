import json, subprocess, os
from datetime import datetime
from zoneinfo import ZoneInfo

SHEET_ID="14x95k1XSJwrQpzx8NcLoCdWZC5ZBSyLexmWEq-9S6yE"

env=os.environ.copy()
env["PATH"]="/home/linuxbrew/.linuxbrew/bin:"+env.get("PATH","")
env["GOG_KEYRING_PASSWORD"]="openclaw_secure_2026"

def run(cmd):
    return subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env).stdout

# ensure auth
subprocess.run(["gog","auth","credentials","set","/data/workspace/gog_client_secret.json","--no-input"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["gog","auth","tokens","import","/data/workspace/gog_auth_backup.json","--no-input"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

file_path="/data/.openclaw/media/inbound/file_36---adb95f32-d112-4cba-8ba1-2d81648d8849.jpg"
name="invoice_2025-04-06_8.45USD.jpg"
up=json.loads(run(["gog","drive","upload",file_path,"--name",name,"--json","--no-input"]))
fid=up["file"]["id"]
url=up["file"]["webViewLink"]

added=datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S")
metadata={
  "description":"Lunch",
  "expense_account":"cambodia",
  "drive_file_id":fid,
  "drive_url":url,
  "source":"telegram",
  "chat_id":"171900099",
  "extracted_invoice_date_raw":"06/04/25",
  "extracted_value_raw":"8.45 USD"
}
row=["2025-04-06", added, "", 8.45, "USD", json.dumps(metadata, ensure_ascii=False), "FALSE"]
values=[row]

run(["gog","sheets","append",SHEET_ID,"Invoices!A:G","--values-json",json.dumps(values,ensure_ascii=False),"--insert","INSERT_ROWS","--input","USER_ENTERED","--no-input","--json"])

print(json.dumps({"drive_file_id":fid,"drive_url":url,"added":added},ensure_ascii=False))
