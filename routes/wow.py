from flask import Blueprint, render_template, request
import requests
import os
from utils.security import return_safe_html

api_url = os.getenv("TEMP_API_URL", "http://api.saddlebagexchange.com/api")

wow_bp = Blueprint("wow", __name__)

NO_RATE_LIMIT = os.getenv("NO_RATE_LIMIT", "False").lower() in ("true", "1", "yes")

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


@wow_bp.route("/wowoutofstock", methods=["GET", "POST"])
def wow_outofstock_api():
    if request.method == "GET":
        return return_safe_html(render_template("wow_outofstock.html"))
    elif request.method == "POST":
        category = int(request.form.get("item_class"))
        if category == -1:
            include_cat = []
        else:
            include_cat = [category]
        json_data = {
            "region": request.form.get("region"),
            "salesPerDay": float(request.form.get("salesPerDay")),
            "avgPrice": int(request.form.get("avgPrice")),
            "minMarketValue": int(request.form.get("minMarketValue")),
            "populationWP": int(request.form.get("populationWP")),
            "populationBlizz": int(request.form.get("populationBlizz")),
            "rankingWP": int(request.form.get("rankingWP")),
            "includeCategories": include_cat,
            "excludeCategories": [],
        }

        response = requests.post(
            f"{api_url}/wow/outofstock",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        if "data" not in response or len(response["data"]) == 0:
            # @coderabbitai will need to move the logger function over so it can be used here
            print(
                f"Error no matching data with given inputs {json_data} response {response}"
            )
            if NO_RATE_LIMIT:
                return f"Error no matching data with given inputs {json_data} response {response}"
            # send generic error message to remove XSS potential
            return "error no matching results found matching search inputs"
        response = response["data"]

        for row in response:
            del row["itemID"]
            del row["item_class"]
            del row["item_subclass"]
            del row["connectedRealmId"]
            del row["itemQuality"]

        fieldnames = list(response[0].keys())

        return return_safe_html(
            render_template(
                "wow_outofstock.html",
                results=response,
                fieldnames=fieldnames,
                len=len,
            )
        )