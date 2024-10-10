from flask import Blueprint, render_template, request
import requests
import os
from utils.security import return_safe_html

api_url = os.getenv("TEMP_API_URL", "http://api.saddlebagexchange.com/api")

wow_bp = Blueprint("wow", __name__)


@wow_bp.route("/wow", methods=["GET", "POST"])
def wow():
    return render_template("wow_index.html", len=len)


@wow_bp.route("/itemnames", methods=["GET", "POST"])
def itemnames():
    if request.method == "GET":
        return render_template("itemnames.html")
    elif request.method == "POST":
        json_data = {}
        response = requests.post(
            f"{api_url}/wow/itemnames",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        resp_list = [{"id": k, "name": v} for k, v in response.items()]

        return return_safe_html(
            render_template(
                "itemnames.html", results=resp_list, fieldnames=["id", "name"], len=len
            )
        )
