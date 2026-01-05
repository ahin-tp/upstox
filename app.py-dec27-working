from flask import Flask, render_template, request, redirect

# ===============================
# DB imports
# ===============================
from db import (
    add_order,
    get_all_orders,
    get_order_by_id,
    mark_cancelled,
    mark_exited
)

# ===============================
# Trader actions
# ===============================
from trader import cancel_order, force_exit

# ===============================
# Upstox connectivity imports
# ===============================
from upstox_client import Configuration, ApiClient
from upstox_client.api.user_api import UserApi
from config import ACCESS_TOKEN

app = Flask(__name__)


# ===============================
# HOME / ADD ORDER
# ===============================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        instrument = request.form["instrument"].strip()

        # HARD SAFETY CHECK
        if not instrument.startswith("NSE_"):
            return "Invalid instrument token. Example: NSE_EQ|INE002A01018", 400

        add_order((
            instrument,
            int(request.form["qty"]),
            float(request.form["trigger"]),
            float(request.form["limit"]),
            float(request.form["sl"])
        ))
        return redirect("/")

    orders = get_all_orders()
    return render_template("index.html", orders=orders)


# ===============================
# CANCEL ORDER (only if PENDING)
# ===============================
@app.route("/cancel/<int:order_id>")
def cancel(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return "Order not found", 404

    # ✅ Access by column name
    if order["status"] != "PENDING":
        return redirect("/")

    entry_order_id = order["entry_order_id"]

    if entry_order_id:
        try:
            cancel_order(entry_order_id)
        except Exception as e:
            print(f"Upstox cancel failed: {e}")

    mark_cancelled(order_id)
    return redirect("/")


# ===============================
# FORCE EXIT (only if EXECUTED)
# ===============================
@app.route("/exit/<int:order_id>")
def exit_trade(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return "Order not found", 404

    # ✅ Access by column name
    if order["status"] != "EXECUTED":
        return redirect("/")

    try:
        force_exit(order["instrument"], order["qty"])
    except Exception as e:
        print(f"Upstox exit failed: {e}")

    mark_exited(order_id)
    return redirect("/")


# ===============================
# UPSTOX CONNECTIVITY CHECK
# ===============================
@app.route("/upstox-health")
def upstox_health():
    try:
        cfg = Configuration()
        cfg.access_token = ACCESS_TOKEN

        client = ApiClient(cfg)
        user_api = UserApi(client)

        profile = user_api.get_profile(api_version="2.0")

        return {
            "status": "CONNECTED",
            "user": profile.data.user_name
        }

    except Exception as e:
        return {
            "status": "FAILED",
            "error": str(e)
        }, 500


# ===============================
# APP START
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
