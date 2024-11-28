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
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")

        flash("Неверный логин или пароль")

    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not password:
            flash("Пароль не может быть пустым")
            return redirect("/register")

        if password != confirm_password:
            flash("Пароли не совпадают")
            return redirect("/register")

        if User.query.filter_by(username=username).first():
            flash("Пользователь уже существует")
            return redirect("/register")

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Регистрация успешна")
        return redirect("/login")
    return render_template("register.html")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
