from flask import url_for, request
from flask_jwt_extended import create_access_token
from flask_mail import Message
import datetime
from .extensions import mail


def send_activation_email(user_id, email):
    token = create_access_token(identity=user_id, expires_delta=datetime.timedelta(hours=15))
    domain = f"{request.scheme}://{request.host}"
    activation_link = f"{domain}{url_for('auth.activate', token=token)}"
    print(f'this is the activation link: {activation_link}')
    msg = Message(subject="Activate Your Account", recipients=[email])
    msg.body = f'Please click the link to activate your account: {activation_link}'
    mail.send(msg)
    

