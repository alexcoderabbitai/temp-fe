from flask import Blueprint, render_template, request
import requests
import os
from utils.security import return_safe_html

api_url = os.getenv("TEMP_API_URL", "http://api.saddlebagexchange.com/api")

ffxiv_bp = Blueprint("ffxiv", __name__)


@ffxiv_bp.route("/ffxiv", methods=["GET", "POST"])
def ffxiv():
    return render_template("ffxiv_index.html", len=len)


@ffxiv_bp.route("/ffxiv_itemnames", methods=["GET", "POST"])
def ffxivitemnames():
    if request.method == "GET":
        return render_template("ffxiv_itemnames.html")
    elif request.method == "POST":
        raw_items_names = requests.get(
            "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/staging/libs/data/src/lib/json/items.json"
        ).json()
        item_ids = requests.get("https://universalis.app/api/marketable").json()

        resp_list = [
            {"id": id, "name": raw_items_names[str(id)]["en"]} for id in item_ids
        ]

        return return_safe_html(
            render_template(
                "ffxiv_itemnames.html",
                results=resp_list,
                fieldnames=["id", "name"],
                len=len,
            )
        )


# {
#   "home_server": "Famfrit",
#   "user_auctions": [
#     { "itemID": 4745, "price": 100, "desired_state": "below", "hq": true }
#   ]
# }
@ffxiv_bp.route("/pricecheck", methods=["GET", "POST"])
def ffxiv_pricecheck():
    return redirect("https://saddlebagexchange.com/price-sniper")
