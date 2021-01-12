from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import os
from app import app


app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_SUPPRESS_SEND'] = app.testing

mail = Mail(app)


def generate_token(email):
    """Generate email confirmation token."""
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    """Confirm email token is valid."""
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def send_email(to, subject, template):
    """Send email."""
    msg = Message(subject, sender=os.environ.get('MAIL_USERNAME'), recipients=[to])
    msg.html = template
    mail.send(msg)
   