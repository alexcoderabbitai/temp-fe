from flask import Blueprint, render_template, send_from_directory
from utils.security import return_safe_html

general_bp = Blueprint("general", __name__)


@general_bp.route("/", methods=["GET", "POST"])
def root():
    return return_safe_html(render_template("index.html"))


@general_bp.route("/favicon.ico", methods=["GET", "POST"])
def favicon():
    return send_from_directory("templates", "chocobo.png")


@general_bp.route("/openapi-spec.json", methods=["GET", "POST"])
def openapispec():
    with open("openapi-spec.json", "r") as file:
        content = file.read()
    return content
