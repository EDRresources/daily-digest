import os
import re
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

digest_file = os.environ.get("DIGEST_FILE", "").strip()
print(f"DIGEST_FILE env var: '{digest_file}'")

if not digest_file:
    print("No digest file passed — skipping.")
    sys.exit(0)

basename = os.path.splitext(digest_file)[0]
m = re.match(r"digest_(\d{4})(\d{2})(\d{2})", basename)
if m:
    year, month_num, day_num = int(m.group(1)), int(m.group(2)), int(m.group(3))
    month_names = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    date_str = f"{month_names[month_num]} {day_num}, {year}"
else:
    date_str = basename

print(f"Date: {date_str}")

pages_url = f"https://edrresources.github.io/daily-digest/{digest_file}"

# Pull section headers (<h2>) from the digest HTML as a quick teaser list
teasers_html = ""
if os.path.exists(digest_file):
    with open(digest_file, encoding="utf-8") as f:
        html = f.read()
    sections = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.IGNORECASE | re.DOTALL)
    sections = [re.sub(r"<[^>]+>", "", s).strip() for s in sections]
    if sections:
        items = "".join(f'<li style="margin-bottom:4px;">{s}</li>' for s in sections)
        teasers_html = (
            '<p style="font-family:Georgia,serif;font-size:14px;color:#555;margin:12px 0 4px;">'
            "Today's sections:</p>"
            f'<ul style="font-family:Georgia,serif;font-size:14px;color:#2c1a00;margin:0 0 12px 18px;">{items}</ul>'
        )

html_body = (
    '<div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;color:#2c1a00;">'
    f'<p style="font-size:16px;margin:0 0 8px 0;"><strong>Daily Digest &mdash; {date_str}</strong></p>'
    + teasers_html
    + f'<p style="margin-top:20px;"><a href="{pages_url}" style="font-family:Georgia,serif;font-size:16px;color:#7a4a00;font-weight:bold;text-decoration:none;">&#9670; Open Today&rsquo;s Digest &rarr;</a></p>'
    + '<hr style="border:none;border-top:1px solid #c9a84c;margin:20px 0 12px;">'
    + '<p style="font-size:12px;color:#6b4f1a;margin:0;">Erik\'s Daily Digest &middot; sports, Birmingham news, Alzheimer\'s/FTD science</p>'
    + '</div>'
)

gmail_user = "erik.d.roberson@gmail.com"
gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")
recipients = ["erik.d.roberson@gmail.com"]

print(f"GMAIL_APP_PASSWORD present: {bool(gmail_password)} (length {len(gmail_password)})")
print(f"Sending to: {recipients}")

msg = MIMEMultipart("alternative")
msg["Subject"] = f"Daily Digest — {date_str}"
msg["From"] = gmail_user
msg["To"] = ", ".join(recipients)
msg.attach(MIMEText(html_body, "html"))

print("Connecting to Gmail SMTP...")
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(gmail_user, gmail_password)
    server.sendmail(gmail_user, recipients, msg.as_string())
    print("Email sent successfully!")
