import smtplib
from email.mime.text import MIMEText
from src.config import SMTP_EMAIL, SMTP_APP_PASSWORD


def send_verification_email(to_email: str, code: str):
    subject = "Your StudyMart Verification Code"
    body = f"Your verification code is: {code}\n\nEnter this code to complete your signup."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())


def send_verification_email(to_email: str, code: str):
    subject = "Your StudyMart Verification Code"
    body = f"Your verification code is: {code}\n\nEnter this code to complete your signup."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    print(f"Sending email to: {to_email}")

    

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        print("SMTP_EMAIL:", SMTP_EMAIL)
        print("SMTP_APP_PASSWORD exists:", bool(SMTP_APP_PASSWORD))
        print("To Email:", to_email)
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)

        try:
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
            print(f"Email successfully sent to: {to_email}")
        except Exception as e:
            print("SMTP Error:", e)
            raise

    print("Email sent successfully!")
    print(f"Email successfully sent to: {to_email}")