import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def format_reviews_html(reviews, target_date):
    if not reviews:
        return f"<p>No new reviews found since {target_date}.</p>"
    
    html = f"<h2>Google Play Reviews since {target_date}</h2>"
    html += f"<p>Total reviews: {len(reviews)}</p><hr>"
    
    for r in reviews:
        stars = "★" * r['score'] + "☆" * (5 - r['score'])
        html += f"""
        <div style="margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 10px;">
            <strong>{r['userName']}</strong> ({r['at'].strftime('%Y-%m-%d %H:%M')})<br>
            <span style="color: #f39c12; font-size: 1.2em;">{stars}</span><br>
            <p>{r['content']}</p>
        </div>
        """
    return html

def send_email(subject, body_html, to_emails):
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    msg = MIMEMultipart()
    msg['From'] = Config.SENDER_EMAIL
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject

    msg.attach(MIMEText(body_html, 'html'))

    try:
        print(f"Connecting to SMTP server {Config.SMTP_SERVER}:{Config.SMTP_PORT}...")
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Email sent successfully to {', '.join(to_emails)}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise
