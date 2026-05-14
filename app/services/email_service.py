import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_new_account_email(email_to: str, username: str, password: str):
    login_url = f"{settings.FRONTEND_URL}/login"
    subject = "Welcome to Wysele - Your Account is Ready"
    html_content = f"""
    <html>
        <body>
            <h2>Welcome to Wysele!</h2>
            <p>Your account has been created. Here are your login credentials:</p>
            <ul>
                <li><b>Email:</b> {username}</li>
                <li><b>Temporary Password:</b> <code style="font-size:16px;">{password}</code></li>
            </ul>
            <p><b>Important:</b> You will be required to change your password on first login.</p>
            <a href="{login_url}"
               style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
               Login Now
            </a>
            <br><br>
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


def send_application_confirmation_email(email_to: str, first_name: str, job_code: str, role: str):
    subject = f"Application Received - {job_code}"
    html_content = f"""
    <html>
        <body>
            <h2>Application Received!</h2>
            <p>Hi <b>{first_name}</b>,</p>
            <p>Thank you for applying. We have received your application for the following position:</p>
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Job Code</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{job_code}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Role</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{role}</td>
                </tr>
            </table>
            <br>
            <p>Our team will review your application and get back to you shortly.</p>
            <p>Regards,<br>Wysele Recruitment Team</p>
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
        print(f"Failed to send application confirmation email: {e}")


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