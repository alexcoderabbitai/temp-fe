import json, os
from datetime import datetime

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect

from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests, logging

from ddtrace import patch_all, tracer, config, Pin
from ddtrace.profiling import Profiler

from routes.ffxiv import ffxiv_bp
from routes.general import general_bp
from routes.wow import wow_bp
from utils.security import add_security_headers, return_safe_html

# Enable Datadog tracing
patch_all()
profiler = Profiler()
profiler.start()

# Initialize Datadog tracer
DD_AGENT_HOST = os.getenv("DD_AGENT_HOST", "localhost")
tracer.configure(
    hostname=DD_AGENT_HOST,  # Replace with your Datadog agent hostname if different
    port=8126,  # Replace with your Datadog agent port if different
)

# Set Datadog service and environment variables
os.environ["DD_SERVICE"] = "flask-test"
os.environ["DD_ENV"] = "production"
os.environ["DD_VERSION"] = "1.0"
os.environ["DD_LOGS_INJECTION"] = "true"

# Alternatively, configure Datadog settings directly
config.service = "flask-test"
config.env = "production"
config.version = "1.0"

# Get API URL from environment variable or use default if not set
api_url = os.getenv("TEMP_API_URL", "http://api.saddlebagexchange.com/api")

app = Flask(__name__)
# Attach the tracer to the Flask app
Pin.override(app, service="flask-test")

# Initialize Flask-CORS with your app and specify allowed origins
origins = [
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "https://temp.saddlebagexchange.com",
    "http://tryanna.xyz",
]
CORS(app, resources={r"/*": {"origins": origins}})

# Check for NO_RATE_LIMIT environment variable
NO_RATE_LIMIT = os.getenv("NO_RATE_LIMIT", False)
if not NO_RATE_LIMIT:
    # Apply rate limit if NO_RATE_LIMIT is not set
    limiter = Limiter(get_remote_address, app=app, default_limits=["1 per second"])

# Set the logging level to INFO for the Flask app
app.logger.setLevel(logging.INFO)
app.logger.disabled = True
logging.basicConfig(level=logging.INFO)

# Setup logging for custom errors

# Configure the logger with the custom format
log_format = (
    "%(levelname)s:\t[%(process)d][%(asctime)s] [%(module)s][%(funcName)s]  %(message)s"
)
formatter = logging.Formatter(log_format)

# Create a handler and set the formatter
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Create the logger and add the handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG
logger.addHandler(handler)


class CustomLogHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def format(self, record):
        return f"{record.levelname}: {record.getMessage()}"


custom_handler = CustomLogHandler()
app.logger.addHandler(custom_handler)


# Register blueprints to add routes
app.register_blueprint(wow_bp)
app.register_blueprint(ffxiv_bp)
app.register_blueprint(general_bp)


# Use add_security_headers from utils/security.py
@app.after_request
def apply_security_headers(response):
    return add_security_headers(response)


@app.route("/ffxivcraftsim", methods=["GET", "POST"])
def ffxivcraftsim():
    return redirect("https://saddlebagexchange.com/ffxiv/craftsim/queries")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("ffxiv_craftsim.html"))
    elif request.method == "POST":
        if request.form.get("hide_expert_recipes") == "True":
            hide_expert_recipes = True
        else:
            hide_expert_recipes = False

        json_data = {
            "home_server": request.form.get("home_server"),
            "cost_metric": request.form.get("cost_metric"),
            "revenue_metric": request.form.get("revenue_metric"),
            "sales_per_week": int(request.form.get("sales_per_week")),
            "median_sale_price": int(request.form.get("median_sale_price")),
            "max_material_cost": int(request.form.get("max_material_cost")),
            "jobs": [int(request.form.get("job"))],
            "filters": [int(request.form.get("filters"))],
            "stars": int(request.form.get("stars")),
            "lvl_lower_limit": int(request.form.get("lvl_lower_limit")),
            "lvl_upper_limit": int(request.form.get("lvl_upper_limit")),
            "yields": int(request.form.get("yields")),
            "hide_expert_recipes": hide_expert_recipes,
        }

        craftsim_post_json = requests.post(
            f"{api_url}/v2/craftsim",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        return craftsim_results_table(
            craftsim_post_json, "ffxiv_craftsim.html", json_data
        )


def craftsim_results_table(craftsim_results, html_file_name, json_data={}):
    if "data" not in craftsim_results:
        logger.error(str(craftsim_results))
        # send generic error message to remove XSS potential
        return f"error no matching results found matching search inputs"

    if len(craftsim_results["data"]) == 0:
        if json_data:
            return (
                f"error no matching results found matching search inputs:\n {json_data}"
            )
        else:
            return f"error no matching results found matching search inputs:\n {craftsim_results}"

    craftsim_results = craftsim_results["data"]

    for item_data in craftsim_results:
        del item_data["itemID"]
        hq = item_data["hq"]
        del item_data["hq"]
        yields = item_data["yieldsPerCraft"]
        del item_data["yieldsPerCraft"]

        se_link = item_data["itemData"]
        del item_data["itemData"]
        universalisLink = item_data["universalisLink"]
        del item_data["universalisLink"]

        costEst = item_data["costEst"]
        del item_data["costEst"]
        revenueEst = item_data["revenueEst"]
        del item_data["revenueEst"]

        item_data["hq"] = hq
        item_data["yields"] = yields
        item_data["item-data"] = se_link
        item_data["universalisLink"] = universalisLink

        item_data["material - current region min listing cost:"] = costEst[
            "material_min_listing_cost"
        ]
        item_data["material - median regional cost:"] = costEst["material_median_cost"]
        item_data["material - average regional cost:"] = costEst["material_avg_cost"]

        item_data["revenue - current home server min listing price:"] = revenueEst[
            "revenue_home_min_listing"
        ]
        item_data["revenue - current regional min listing price:"] = revenueEst[
            "revenue_region_min_listing"
        ]
        item_data["revenue - regional median sale price:"] = revenueEst[
            "revenue_median"
        ]
        item_data["revenue - regional average sale price:"] = revenueEst["revenue_avg"]

    fieldnames = list(craftsim_results[0].keys())

    return return_safe_html(
        render_template(
            html_file_name,
            results=craftsim_results,
            fieldnames=fieldnames,
            len=len,
        )
    )


@app.route("/ffxivshoppinglist", methods=["GET", "POST"])
def ffxiv_shopping_list():
    return redirect("https://saddlebagexchange.com/ffxiv/shopping-list")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("ffxiv_shoppinglist.html"))
    elif request.method == "POST":
        shopping_list = request.form.get("shopping_list")
        json_data = {
            "home_server": request.form.get("home_server"),
            "region_wide": bool(request.form.get("region_wide")),
            "shopping_list": json.loads(shopping_list),
        }

        shopping_list_json = requests.post(
            f"{api_url}/v2/shoppinglist",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        return ffxiv_shopping_list_result(
            shopping_list_json, "ffxiv_shoppinglist.html", json_data
        )


def ffxiv_shopping_list_result(shopping_list_results, html_file_name, json_data={}):
    if "data" not in shopping_list_results:
        logger.error(str(shopping_list_results))
        # send generic error message to remove XSS potential
        return f"error no matching results found matching search inputs"

    if len(shopping_list_results["data"]) == 0:
        if json_data:
            return (
                f"error no matching results found matching search inputs:\n {json_data}"
            )
        else:
            return f"error no matching results found matching search inputs:\n {shopping_list_results}"

    shopping_list_data = shopping_list_results["data"]
    for item_data in shopping_list_data:
        itemID = item_data["itemID"]
        del item_data["itemID"]
        item_data_copy = {
            "worldName": item_data["worldName"],
            "name": item_data["name"],
            "hq": item_data["hq"],
            "pricePerUnit": item_data["pricePerUnit"],
            "quantity": item_data["quantity"],
            "itemData": f"https://saddlebagexchange.com/queries/item-data/{itemID}",
            "uniLink": f"https://universalis.app/market/{itemID}",
        }
        for k, v in item_data_copy.items():
            if k not in item_data.keys():
                item_data[k] = v
            else:
                del item_data[k]
                item_data[k] = v

    fieldnames = list(shopping_list_data[0].keys())
    return return_safe_html(
        render_template(
            html_file_name,
            results=shopping_list_data,
            fieldnames=fieldnames,
            len=len,
        )
    )


@app.route("/ffxivbestdeals", methods=["GET", "POST"])
def ffxivbestdeals():
    if request.method == "GET":
        return return_safe_html(render_template("ffxivbestdeals.html"))
    elif request.method == "POST":
        json_data = {
            "home_server": request.form.get("home_server"),
            "discount": int(request.form.get("discount")),
            "medianPrice": int(request.form.get("medianPrice")),
            "salesAmount": int(request.form.get("salesAmount")),
            "maxBuyPrice": int(request.form.get("maxBuyPrice")),
            "filters": [int(request.form.get("filters"))],
        }
        response = requests.post(
            f"{api_url}/bestdeals",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        if "data" not in response:
            logger.error(str(response))
            # send generic error message to remove XSS potential
            return f"error no matching results found matching search inputs"

        if len(response["data"]) == 0:
            logger.error(
                f"No matching results found with seach inputs {json_data} response {response}"
            )
            # send generic error message to remove XSS potential
            return f"error no matching results found matching search inputs"

        resp_list = response["data"]
        column_order = [
            "itemName",
            "worldName",
            "discountHQ",
            "discountNQ",
            "minPriceHQ",
            "minPrice",
            "medianHQ",
            "medianNQ",
            "salesAmountHQ",
            "salesAmountNQ",
            "quantitySoldHQ",
            "quantitySoldNQ",
            "averageHQ",
            "averageNQ",
            "mainCategory",
            "subCategory",
            "itemData",
            "uniLink",
            "lastUploadTime",
        ]
        resp_list = [{key: item.get(key) for key in column_order} for item in resp_list]
        fieldnames = list(resp_list[0].keys())
        return return_safe_html(
            render_template(
                "ffxivbestdeals.html", results=resp_list, fieldnames=fieldnames, len=len
            )
        )


#### WOW ####
@app.route("/uploadtimers", methods=["GET", "POST"])
def uploadtimers():
    return redirect("https://saddlebagexchange.com/wow/upload-timers")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("uploadtimers.html"))
    elif request.method == "POST":
        json_data = {}
        response = requests.post(
            f"{api_url}/wow/uploadtimers",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        if "data" not in response:
            logger.error(
                f"No matching results found with seach inputs {json_data} response {response}"
            )
            # send generic error message to remove XSS potential
            return f"error no matching results found matching search inputs"

        response = response["data"]

        for row in response:
            del row["tableName"]
            del row["lastUploadUnix"]

            pop = row["dataSetName"]
            del row["dataSetName"]
            row["dataSetName"] = pop

        fieldnames = list(response[0].keys())

        return return_safe_html(
            render_template(
                "uploadtimers.html", results=response, fieldnames=fieldnames, len=len
            )
        )


#
# @app.route("/itemnames", methods=["GET", "POST"])
# def itemnames():
#     if request.method == "GET":
#         return return_safe_html(render_template("itemnames.html"))
#     elif request.method == "POST":
#         json_data = {}
#         response = requests.post(
#             f"{api_url}/wow/itemnames",
#             headers={"Accept": "application/json"},
#             json=json_data,
#         ).json()
#
#         resp_list = []
#         for k, v in response.items():
#             resp_list.append({"id": k, "name": v})
#
#         return return_safe_html(
#             render_template(
#                 "itemnames.html", results=resp_list, fieldnames=["id", "name"], len=len
#             )
#         )


@app.route("/megaitemnames", methods=["GET", "POST"])
def megaitemnames():
    if request.method == "GET":
        return return_safe_html(render_template("megaitemnames.html"))
    elif request.method == "POST":
        json_data = {
            "region": request.form.get("region"),
            "discount": int(request.form.get("discount")),
        }
        response = requests.post(
            f"{api_url}/wow/megaitemnames",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        column_order = [
            "itemID",
            "desiredPrice",
            "itemName",
            "salesPerDay",
        ]
        response = [{key: item.get(key) for key in column_order} for item in response]
        fieldnames = list(response[0].keys())
        return return_safe_html(
            render_template(
                "megaitemnames.html", results=response, fieldnames=fieldnames, len=len
            )
        )


@app.route("/petshoppinglist", methods=["GET", "POST"])
def petshoppinglist():
    return redirect("https://saddlebagexchange.com/wow/shopping-list")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("petshoppinglist.html"))
    elif request.method == "POST":
        json_data = {
            "region": request.form.get("region"),
            "itemID": int(request.form.get("petID")),
            "maxPurchasePrice": int(request.form.get("maxPurchasePrice")),
            "connectedRealmIDs": {},
        }

        response = requests.post(
            f"{api_url}/wow/shoppinglistx",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        if "data" not in response:
            logger.error(
                f"Error no matching data with given inputs {json_data} response {response}"
            )
            if NO_RATE_LIMIT:
                return f"Error no matching data with given inputs {json_data} response {response}"
            # send generic error message to remove XSS potential
            return f"error no matching results found matching search inputs"

        response = response["data"]

        column_order = [
            "realmID",
            "price",
            "quantity",
            "realmName",
            "realmNames",
            "link",
        ]
        response = [{key: item.get(key) for key in column_order} for item in response]
        fieldnames = list(response[0].keys())

        return return_safe_html(
            render_template(
                "petshoppinglist.html", results=response, fieldnames=fieldnames, len=len
            )
        )


@app.route("/petmarketshare", methods=["GET", "POST"])
def petmarketshare():
    return redirect("https://saddlebagexchange.com/wow/pet-marketshare")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("petmarketshare.html"))
    elif request.method == "POST":
        json_data = {
            "region": request.form.get("region"),
            "homeRealmName": request.form.get("homeRealmName"),
            "minPrice": int(request.form.get("minPrice")),
            "salesPerDay": int(request.form.get("salesPerDay")),
            "includeCategories": [],
            "excludeCategories": [],
            "sortBy": "estimatedRegionMarketValue",
        }

        response = requests.post(
            f"{api_url}/wow/petmarketshare",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        if "data" not in response:
            logger.error(
                f"Error no matching data with given inputs {json_data} response {response}"
            )
            if NO_RATE_LIMIT:
                return f"Error no matching data with given inputs {json_data} response {response}"
            # send generic error message to remove XSS potential
            return f"error no matching results found matching search inputs"

        response = response["data"]
        column_order = [
            "salesPerDay",
            "itemName",
            "percentChange",
            "state",
            "avgTSMPrice",
            "estimatedRegionMarketValue",
            "homeMinPrice",
            "itemID",
            "link",
            "undermineLink",
            "warcraftPetsLink",
        ]
        response = [{key: item.get(key) for key in column_order} for item in response]
        fieldnames = list(response[0].keys())

        return return_safe_html(
            render_template(
                "petmarketshare.html", results=response, fieldnames=fieldnames, len=len
            )
        )


@app.route("/petexport", methods=["GET", "POST"])
def petexport():
    return redirect("https://saddlebagexchange.com/wow/export-search")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("petexport.html"))
    elif request.method == "POST":
        json_data = {
            "region": request.form.get("region"),
            "itemID": int(request.form.get("itemID")),
            "populationWP": int(request.form.get("populationWP")),
            "populationBlizz": int(request.form.get("populationBlizz")),
            "rankingWP": int(request.form.get("rankingWP")),
            "minPrice": int(request.form.get("minPrice")),
            "maxQuantity": int(request.form.get("maxQuantity")),
            "sortBy": "minPrice",
            "connectedRealmIDs": {},
        }

        response = requests.post(
            f"{api_url}/wow/exportx",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        if "data" not in response:
            logger.error(
                f"Error no matching data with given inputs {json_data} response {response}"
            )
            if NO_RATE_LIMIT:
                return f"Error no matching data with given inputs {json_data} response {response}"
            # send generic error message to remove XSS potential
            return f"error no matching results found matching search inputs"
        response = response["data"]

        for row in response:
            del row["connectedRealmID"]
            del row["realmPopulationInt"]
            row["allRealms"] = row["connectedRealmNames"]
            row["connectedRealmNames"] = row["connectedRealmNames"][0]
            link = row["link"]
            del row["link"]
            row["link"] = link
            undermineLink = row["undermineLink"]
            del row["undermineLink"]
            row["undermineLink"] = undermineLink

        fieldnames = list(response[0].keys())

        return return_safe_html(
            render_template(
                "petexport.html", results=response, fieldnames=fieldnames, len=len
            )
        )


@app.route("/regionundercut", methods=["GET", "POST"])
def regionundercut():
    return redirect("https://saddlebagexchange.com/wow/region-undercut")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("regionundercut.html"))
    elif request.method == "POST":
        addonData = request.form.get("addonData")
        json_data = {
            "region": request.form.get("region"),
            "homeRealmID": int(request.form.get("homeRealmID")),
            "addonData": json.loads(addonData),
        }

        response = requests.post(
            f"{api_url}/wow/regionundercut",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        if "undercut_list" not in response or "not_found_list" not in response:
            logger.error(
                f"Error no matching data with given inputs {json_data} response {response}"
            )
            if NO_RATE_LIMIT:
                return f"Error no matching data with given inputs {json_data} response {response}"
            # send generic error message to remove XSS potential
            return f"error no matching results found matching search inputs"
        undercuts = response["undercut_list"]

        for row in undercuts:
            del row["connectedRealmId"]
            realmName = row["realmName"]
            del row["realmName"]
            row["realmName"] = realmName
            undermineLink = row["link"]
            del row["link"]
            row["undermineLink"] = undermineLink

        undercuts_fieldnames = list(undercuts[0].keys())

        if "not_found_list" not in response:
            logger.error(
                f"Error no matching data with given inputs {json_data} response {response}"
            )
            # send generic error message to remove XSS potential
            return f"error no matching results found matching search inputs"
        not_found = response["not_found_list"]

        for row in not_found:
            del row["connectedRealmId"]
            realmName = row["realmName"]
            del row["realmName"]
            row["realmName"] = realmName
            undermineLink = row["link"]
            del row["link"]
            row["undermineLink"] = undermineLink

        not_found_fieldnames = list(not_found[0].keys())

        return return_safe_html(
            render_template(
                "regionundercut.html",
                results=undercuts,
                fieldnames=undercuts_fieldnames,
                results_n=not_found,
                fieldnames_n=not_found_fieldnames,
                len=len,
            )
        )


@app.route("/bestdeals", methods=["GET", "POST"])
def bestdeals():
    return redirect("https://saddlebagexchange.com/wow/best-deals/recommended")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("bestdeals.html"))
    elif request.method == "POST":
        json_data = {
            "region": request.form.get("region"),
            "type": request.form.get("type"),
            "discount": int(request.form.get("discount")),
            "minPrice": int(request.form.get("minPrice")),
            "salesPerDay": float(request.form.get("salesPerDay")),
            "item_class": int(request.form.get("item_class")),
            "item_subclass": -1,
        }

        response = requests.post(
            f"{api_url}/wow/bestdeals",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        if "data" not in response or len(response["data"]) == 0:
            logger.error(
                f"Error no matching data with given inputs {json_data} response {response}"
            )
            if NO_RATE_LIMIT:
                return f"Error no matching data with given inputs {json_data} response {response}"
            # send generic error message to remove XSS potential
            return f"error no matching results found matching search inputs"
        response = response["data"]

        for row in response:
            del row["itemID"]
            del row["connectedRealmId"]

            minPrice = row["minPrice"]
            del row["minPrice"]
            row["minPrice"] = minPrice

            historicalPrice = row["historicPrice"]
            del row["historicPrice"]
            row["historicPrice"] = historicalPrice

            itemName = row["itemName"]
            del row["itemName"]
            row["itemName"] = itemName

            realmName = row["realmName"]
            del row["realmName"]
            row["realmName"] = realmName

            link = row["link"]
            del row["link"]
            row["link"] = link

            link = row["exportLink"]
            del row["exportLink"]
            row["exportLink"] = link

        fieldnames = list(response[0].keys())

        return return_safe_html(
            render_template(
                "bestdeals.html",
                results=response,
                fieldnames=fieldnames,
                len=len,
            )
        )




@app.route("/petimport", methods=["GET", "POST"])
def petimport():
    if request.method == "GET":
        return render_template("petimport.html")
    elif request.method == "POST":
        headers = {"Accept": "application/json"}
        petsOnly = request.form.get("petsOnly")
        if petsOnly == "False":
            petsOnly = False
        else:
            petsOnly = True
        json_data = {
            "region": request.form.get("region"),
            "homeRealmID": int(request.form.get("homeRealmID")),
            "ROI": int(request.form.get("ROI")),
            "avgPrice": int(request.form.get("avgPrice")),
            "maxPurchasePrice": int(request.form.get("maxPurchasePrice")),
            "profitAmount": int(request.form.get("profitAmount")),
            "salesPerDay": float(request.form.get("salesPerDay")),
            "includeCategories": [],
            "excludeCategories": [],
            "sortBy": "lowestPrice",
            "petsOnly": petsOnly,
            "connectedRealmIDs": {},
        }

        response = requests.post(
            f"{api_url}/api/wow/import",
            headers=headers,
            json=json_data,
        ).json()

        if "data" not in response:
            return f"Error no matching data with given inputs {response}"
        response = response["data"]
        if len(response) == 0:
            return f"No item found with given inputs, try lowering price or sale amount {json_data}"

        for row in response:
            del row["itemID"]
            del row["lowestPriceRealmID"]
            realm = row["lowestPriceRealmName"]
            del row["lowestPriceRealmName"]
            row["lowestPriceRealmName"] = realm

            link = row["link"]
            del row["link"]
            row["link"] = link

            undermineLink = row["undermineLink"]
            del row["undermineLink"]
            row["undermineLink"] = undermineLink

            warcraftPetsLink = row["warcraftPetsLink"]
            del row["warcraftPetsLink"]
            row["warcraftPetsLink"] = warcraftPetsLink

        fieldnames = list(response[0].keys())

        return render_template(
            "petimport.html",
            results=response,
            fieldnames=fieldnames,
            len=len,
        )


@app.route("/ffxivsalehistory", methods=["GET", "POST"])
def ffxivsalehistory():
    return redirect("https://saddlebagexchange.com/ffxiv/extended-history")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("ffxiv_sale_history.html"))
    elif request.method == "POST":
        # json_data = {
        #     "home_server": request.form.get("home_server"),
        #     "item_id": int(request.form.get("item_id")),
        #     "initial_days": 7,
        #     "end_days": 0,
        #     "item_type": "all",
        # }
        region = request.form.get("region")
        item_id = int(request.form.get("item_id"))
        response = requests.get(
            "https://universalis.app/api/v2/history/" + f"{region}/{item_id}"
        ).json()

        if "entries" not in response:
            return "Error refresh the page or contact the devs on discord"
        if len(response["entries"]) == 0:
            return "Error no sales in past week"

        fixed_response = []
        for sale in response["entries"]:
            sale["date"] = datetime.utcfromtimestamp(sale["timestamp"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            for val in [
                "hq",
                "pricePerUnit",
                "quantity",
                "buyerName",
                "onMannequin",
                "worldID",
            ]:
                temp = sale[val]
                del sale[val]
                sale[val] = temp

            fixed_response.append(sale)
        fieldnames = list(fixed_response[0].keys())

        return return_safe_html(
            render_template(
                "ffxiv_sale_history.html",
                results=fixed_response,
                fieldnames=fieldnames,
                len=len,
            )
        )


@app.route("/ffxivscripexchange", methods=["GET", "POST"])
def ffxiv_scrip_exchange():
    return redirect("https://saddlebagexchange.com/ffxiv/scrip-exchange")

    # DEPRECIATED
    if request.method == "GET":
        return return_safe_html(render_template("ffxiv_scrip_exchange.html"))
    elif request.method == "POST":
        json_data = {
            "home_server": request.form.get("home_server"),
            "color": request.form.get("color"),
        }

        response = requests.post(
            f"{api_url}/ffxiv/scripexchange",
            headers={"Accept": "application/json"},
            json=json_data,
        ).json()

        if "data" not in response:
            return "Error refresh the page or contact the devs on discord"
        if len(response["data"]) == 0:
            return "Error no sales in past week"

        fieldnames = list(response["data"][0].keys())

        return return_safe_html(
            render_template(
                "ffxiv_scrip_exchange.html",
                results=response["data"],
                fieldnames=fieldnames,
                len=len,
            )
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0")

    # for testing

    ## http
    # app.run(host="0.0.0.0", debug=True)

    ## https
    # app.run(host='0.0.0.0',port=443,debug=True, ssl_context=("./certs/full_chain.crt","./certs/private.key"))
