from pathlib import Path
import smtplib
from email.mime.text import MIMEText
import os
from src.utils.schema import EmailSchema

def load_prompt(prompt_path: str) -> str:
    """
    Load a prompt from a file.
    
    Args:
        prompt_path (str): Path to the prompt file.
        
    Returns:
        str: The content of the prompt file.
    """
    if not Path(prompt_path).exists():
        raise FileNotFoundError(f"Prompt file {prompt_path} does not exist.")
    
    prompt_path = Path(prompt_path)
    prompt_template = prompt_path.read_text(encoding="utf-8")
    return prompt_template


def send_email(to_email: str, subject: str, body: str) -> None:
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    host = os.getenv("EMAIL_HOST")
    port = int(os.getenv("EMAIL_PORT"))

    msg = MIMEText(body, "plain", "utf-8")
    msg[EmailSchema.SUBJECT] = subject
    msg[EmailSchema.FROM] = from_email
    msg[EmailSchema.TO] = to_email

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, [to_email], msg.as_string())
    except Exception as e:
        raise Exception(f"Email send failed: {e}")