from typing import Optional


def send_email(to: str, subject: str, body: str) -> None:
    """Placeholder email sender that just prints the email contents."""
    print(f"Sending email to {to}: {subject} - {body}")
