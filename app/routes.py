from flask import Blueprint, render_template, request, jsonify, redirect, flash
from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, ChatMessage, User
from .services import chat_service
from config import Config
import httpx

main = Blueprint("main", __name__)


@main.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect("/login")
    initial_greeting = chat_service.get_initial_greeting()
    return render_template("index.html", initial_greeting=initial_greeting)


@main.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.json
    messages = data.get("messages", [])

    ip_address = request.remote_addr

    user_message = messages[-1]["content"]
    user_chat_message = ChatMessage(
        ip_address=ip_address, message=user_message, sender="user"
    )
    db.session.add(user_chat_message)

    response = chat_service.generate_response(messages)

    ai_chat_message = ChatMessage(ip_address=ip_address, message=response, sender="ai")
    db.session.add(ai_chat_message)

    db.session.commit()

    return jsonify({"response": response})


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hcaptcha_response = request.form.get("h-captcha-response")

        if not password:
            flash("Пароль не может быть пустым")
            return redirect("/login")

        if not username:
            flash("Имя пользователя не может быть пустым")
            return redirect("/login")

        if not hcaptcha_response:
            flash("Необходимо подтвердить, что вы не робот")
            return redirect("/login")

        data = {"secret": Config.HCAPTCHA_SECRET_KEY, "response": hcaptcha_response}
        response = httpx.post("https://hcaptcha.com/siteverify", data=data)

        if not response.json().get("success"):
            flash("Необходимо подтвердить, что вы не робот")
            return redirect("/login")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")

        flash("Неверный логин или пароль")

    return render_template("login.html", sitekey=Config.HCAPTCHA_SITE_KEY)


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        hcaptcha_response = request.form.get("h-captcha-response")

        if not password or not confirm_password:
            flash("Пароль не может быть пустым")
            return redirect("/login")

        if not username:
            flash("Имя пользователя не может быть пустым")
            return redirect("/login")

        if not hcaptcha_response:
            flash("Необходимо подтвердить, что вы не робот")
            return redirect("/login")

        if password != confirm_password:
            flash("Пароли не совпадают")
            return redirect("/register")

        data = {"secret": Config.HCAPTCHA_SECRET_KEY, "response": hcaptcha_response}
        response = httpx.post("https://hcaptcha.com/siteverify", data=data)

        if not response.json().get("success"):
            flash("Необходимо подтвердить, что вы не робот")
            return redirect("/login")

        if User.query.filter_by(username=username).first():
            flash("Пользователь уже существует")
            return redirect("/register")

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Регистрация успешна")
        return redirect("/login")
    return render_template("register.html", sitekey=Config.HCAPTCHA_SITE_KEY)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@main.route("/change_credentials", methods=["GET", "POST"])
@login_required
def change_credentials():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        hcaptcha_response = request.form.get("h-captcha-response")

        if not new_username:
            flash("Логин не может быть пустым")
            return redirect("/change_credentials")

        if not new_password or not confirm_password:
            flash("Пароль не может быть пустым")
            return redirect("/change_credentials")

        if new_password != confirm_password:
            flash("Пароли не совпадают")
            return redirect("/change_credentials")

        if not hcaptcha_response:
            flash("Необходимо подтвердить, что вы не робот")
            return redirect("/login")

        data = {"secret": Config.HCAPTCHA_SECRET_KEY, "response": hcaptcha_response}
        response = httpx.post("https://hcaptcha.com/siteverify", data=data)

        if not response.json().get("success"):
            flash("Необходимо подтвердить, что вы не робот")
            return redirect("/login")

        if (
            User.query.filter_by(username=new_username).first()
            and new_username != current_user.username
        ):
            flash("Этот логин уже занят")
            return redirect("/change_credentials")

        current_user.username = new_username
        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Ваши данные успешно обновлены")
        return redirect("/")

    return render_template("change_credentials.html", sitekey=Config.HCAPTCHA_SITE_KEY)
