#### FFXIV RESELLING SEARCH ####
# just used for initial test of temp flask pod not maintained

# @app.route("/scan", methods=["GET", "POST"])
# def scan():
#     if request.method == "GET":
#         return render_template("oldscan.html")
#     elif request.method == "POST":
#         scan_hours = request.form.get("scan_hours")
#         sale_amt = request.form.get("sale_amt")
#         roi = request.form.get("roi")
#         home_server = request.form.get("home_server")
#         stack_size = request.form.get("stack_size")
#         hq_only = request.form.get("hq_only")
#         profit_amt = request.form.get("profit_amt")
#         min_desired_avg_ppu = request.form.get("min_desired_avg_ppu")
#         game_wide = request.form.get("game_wide")
#         include_vendor = request.form.get("include_vendor")
#         out_stock = request.form.get("out_stock")
#         filters = [int(request.form.get("filters"))]
#         headers = {"Accept": "application/json"}
#         json_data = {
#             "preferred_roi": int(roi),
#             "min_profit_amount": int(profit_amt),
#             "min_desired_avg_ppu": int(min_desired_avg_ppu),
#             "min_stack_size": int(stack_size),
#             "hours_ago": int(scan_hours),
#             "min_sales": int(sale_amt),
#             "hq": str_to_bool(hq_only),
#             "home_server": home_server,
#             "filters": filters,
#             "region_wide": str_to_bool(game_wide),
#             "include_vendor": str_to_bool(include_vendor),
#             "show_out_stock": str_to_bool(out_stock),
#             "universalis_list_uid": "",
#         }
#         response = requests.post(
#             "http://api.saddlebagexchange.com/api/scan/",
#             headers=headers,
#             json=json_data,
#         ).json()
#         if "data" not in response:
#             return f"Error no matching data with given inputs {response}"
#         response = response["data"]
#         fieldnames = list(response[0].keys())
#         return render_template(
#             "oldscan.html", results=response, fieldnames=fieldnames, len=len
#         )

### FFXIV best server ####

# @app.route("/ffxivserverhistory", methods=["GET", "POST"])
# def ffxivserverhistory():
#     if request.method == "GET":
#         return return_safe_html(render_template("ffxiv_server_history.html"))
#     elif request.method == "POST":
#         json_data = {
#             "home_server": request.form.get("home_server"),
#             "item_id": int(request.form.get("item_id")),
#             "initial_days": 7,
#             "end_days": 0,
#             "item_type": "all",
#         }
#         response = requests.post(
#             "http://api.saddlebagexchange.com/history",
#             headers={"Accept": "application/json"},
#             json=json_data,
#         ).json()
#         if "server_distribution" not in response:
#             return "Error refresh the page or contact the devs on discord"
#         fixed_response = []
#         for server, sale_count in response["server_distribution"].items():
#             fixed_response.append(
#                 {
#                     "Server": server,
#                     "Sale Count": sale_count,
#                 }
#             )
#         fieldnames = list(fixed_response[0].keys())
#         return return_safe_html(render_template(
#             "ffxiv_server_history.html",
#             results=fixed_response,
#             fieldnames=fieldnames,
#             len=len,
#         ))

### FFXIV price check ###

# @app.route("/pricecheck", methods=["GET", "POST"])
# def ffxiv_pricecheck():
#     return redirect("https://saddlebagexchange.com/price-sniper")
#     # DEPRECIATED
#     if request.method == "GET":
#         return return_safe_html(render_template("ffxiv_pricecheck.html"))
#     elif request.method == "POST":
#         json_data = json.loads(request.form.get("jsonData"))
#         response = requests.post(
#             f"{api_url}/pricecheck",
#             headers={"Accept": "application/json"},
#             json=json_data,
#         ).json()
#         if "matching" not in response:
#             return "Error no matching data"
#         if len(response["matching"]) == 0:
#             return "Error no matching data"
#         fixed_response = []
#         for row in response["matching"]:
#             fixed_response.append(
#                 {
#                     "minPrice": row["minPrice"],
#                     "itemName": row["itemName"],
#                     "server": row["server"],
#                     "dc": row["dc"],
#                     "desired_state": row["desired_state"],
#                     "hq": row["hq"],
#                     "quantity": row["minListingQuantity"],
#                     "item-data": f"https://saddlebagexchange.com/queries/item-data/{row['itemID']}",
#                     "uniLink": f"https://universalis.app/market/{row['itemID']}",
#                 }
#             )
#         fieldnames = list(fixed_response[0].keys())
#         return return_safe_html(
#             render_template(
#                 "ffxiv_pricecheck.html",
#                 results=fixed_response,
#                 fieldnames=fieldnames,
#                 len=len,
#             )
#         )


### SECURITY STUFF ###

# @app.route("/2faca366-0ef0-4acb-9acc-3808e0470952.txt", methods=["GET", "POST"])
# def probely():
#     return Response(
#         "Probely",
#         headers={
#             "Content-Disposition": "attachment; filename=2faca366-0ef0-4acb-9acc-3808e0470952.txt"
#         },
#     )
#     # return "Probely"

### SECURITY STUFF ###

# @app.route(
#     "/GitLab-DAST-Site-Validation-a8f90252-4e3a-488d-be6e-584993462fe1.txt",
#     methods=["GET", "POST"],
# )
# def gitlab():
#     return Response(
#         "a8f90252-4e3a-488d-be6e-584993462fe1",
#         headers={
#             "Content-Disposition": "attachment; filename=GitLab-DAST-Site-Validation-a8f90252-4e3a-488d-be6e-584993462fe1.txt"
#         },
#     )
