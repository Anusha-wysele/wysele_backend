import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_new_account_email(email_to: str, username: str, password: str):
    # This should be your frontend URL (e.g., https://wysele.com/login)
    login_url = f"{settings.FRONTEND_URL}/login"
    
    subject = "Welcome to Wysele - Your Admin Account is Ready"
    
    # 1. Create the HTML version (Clickable)
    html_content = f"""
    <html>
        <body>
            <h2>Welcome to Wysele!</h2>
            <p>A new administrator account has been created for you.</p>
            <p><b>Login Details:</b></p>
            <ul>
                <li><b>Username:</b> {username}</li>
                <li><b>Password:</b> {password}</li>
            </ul>
            <p>Please click the button below to log in and change your password:</p>
            <a href="{login_url}" 
               style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
               Login to Dashboard
            </a>
            <br><br>
            <p>If the button doesn't work, copy and paste this link: {login_url}</p>
            <p>Regards,<br>Wysele System Team</p>
        </body>
    </html>
    """

    # 2. Setup the Email Message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = email_to

    # Add the HTML content to the email
    part = MIMEText(html_content, "html")
    message.attach(part)

    # 3. Send via SMTP
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_otp_email(email_to: str, otp: str, purpose: str):
    label = "Consulting Form" if purpose == "consulting" else "Job Application"
    subject = f"Wysele - Email Verification OTP for {label}"
    html_content = f"""
    <html>
        <body>
            <h2>Email Verification</h2>
            <p>Use the OTP below to verify your email for your <b>{label}</b>.</p>
            <h1 style="letter-spacing: 8px; color: #007bff;">{otp}</h1>
            <p>This OTP expires in <b>10 minutes</b>. Do not share it with anyone.</p>
            <p>If you did not request this, ignore this email.</p>
            <p>Regards,<br>Wysele System Team</p>
        </body>
    </html>
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = email_to
    message.attach(MIMEText(html_content, "html"))
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
    except Exception as e:
        print(f"Failed to send OTP email: {e}")


def send_password_reset_email(email_to: str, reset_token: str):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    subject = "Wysele - Password Reset Request"
    html_content = f"""
    <html>
        <body>
            <h2>Password Reset</h2>
            <p>Click the button below to reset your password. This link expires in 30 minutes.</p>
            <a href="{reset_url}"
               style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
               Reset Password
            </a>
            <br><br>
            <p>If you did not request this, ignore this email.</p>
            <p>Regards,<br>Wysele System Team</p>
        </body>
    </html>
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = email_to
    message.attach(MIMEText(html_content, "html"))
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
    except Exception as e:
        print(f"Failed to send reset email: {e}")