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

# Embed the full digest content in the email body (not just a link).
inline_css = ""
body_content = ""
if os.path.exists(digest_file):
    with open(digest_file, encoding="utf-8") as f:
        html = f.read()

    style_match = re.search(r"<style[^>]*>(.*?)</style>", html, re.IGNORECASE | re.DOTALL)
    if style_match:
        inline_css = style_match.group(1)

    body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.IGNORECASE | re.DOTALL)
    body_content = body_match.group(1) if body_match else html

link_html = (
    f'<p style="margin:16px 0;"><a href="{pages_url}" '
    'style="font-family:Georgia,serif;font-size:14px;color:#7a4a00;font-weight:bold;text-decoration:none;">'
    '&#9670; View on the web &rarr;</a></p>'
    '<hr style="border:none;border-top:1px solid #c9a84c;margin:16px 0;">'
)

html_body = (
    f'<style>{inline_css}</style>'
    '<div style="max-width:700px;margin:0 auto;">'
    + link_html
    + body_content
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
