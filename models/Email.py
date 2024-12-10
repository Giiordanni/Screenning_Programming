import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import random
from db.redis import redis_client

load_dotenv()

def generateCode():
    return str(random.randint(100000, 900000))

def sendEmail(subject, recipient, body):
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')

    if not email_user or not email_password:
        raise ValueError("Email or password environment variables not set")

    html_body = f"<p>{body}</p>"

    print(email_user,recipient)

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_user
    msg['To'] = recipient
    msg.set_content(html_body, subtype='html', charset='utf-8')

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(email_user, email_password)
            s.send_message(msg)
        print('E-mail enviado com sucesso')
    except smtplib.SMTPException as e:
        print(f"Erro ao enviar e-mail: {e}")
        raise

def send_verification_code(email):
    code = generateCode()
    redis = redis_client()

    subject = "Código de verificação"
    
    ditc_code = {
        "code": code
    }
    redis.hset(f"verification_code:{email}", mapping=ditc_code)
    redis.expire(f"verification_code:{email}", 300)

    with open("templates/sendCodeVerification.html", 'r', encoding='utf-8') as file:
        html = file.read()
        body = html.format(codigo=code)
    
    sendEmail(subject, email, body)

def verify_code(email, code):
    redis = redis_client()

    stored_code = redis.hgetall(f"verification_code:{email}")
    
    if stored_code is None:
        print("Nenhum código encontrado no Redis para este email.")
        return False
    
    return stored_code.get("code", "").strip() == code.strip()
        
def user_data(email):
    redis = redis_client()
    return redis.hgetall(f"user_data:{email}")


def delete_data(key):
    redis_client().delete(key)
