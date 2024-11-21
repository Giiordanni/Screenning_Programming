import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import random
import redis

load_dotenv()

def redis_client():
    return redis.StrictRedis.from_url(os.getenv("REDIS_CLIENT"), decode_responses=True)

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

    subject = "Código de verificação"

    redis_client().setex(f"verification_code:{email}", 300, code)

    with open("templates/sendCodeVerification.html", 'r', encoding='utf-8') as file:
        html = file.read()
        body = html.format(codigo=code)
    
    sendEmail(subject, email, body)

def verify_code(email, code):
    
    stored_code = redis_client().get(f"verification_code:{email}")

    if stored_code is None:
        print("Nenhum código encontrado no Redis para este email.")
        return False
    
    return stored_code.strip() == code.strip()
        
def user_data(email):
    return redis_client().get(f"user_data:{email}")

