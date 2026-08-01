from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("projects.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email address already registered.", "danger")
            return render_template("register.html")

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created successfully!", "success")
        return redirect(url_for("projects.dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("projects.dashboard"))

    # If no users exist in the system yet, guide first-time user to Sign Up
    if User.query.count() == 0:
        flash("Welcome to Lexora AI! Please sign up to create your account.", "info")
        return redirect(url_for("auth.register"))

    if request.method == "POST":
        login_input = request.form.get("login_input", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter(
            (User.username == login_input) | (User.email == login_input.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("projects.dashboard"))

        flash("Invalid username/email or password. If you haven't registered yet, please click 'Sign up' below.", "danger")
        return render_template("login.html")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
