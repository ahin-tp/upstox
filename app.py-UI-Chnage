from flask import Flask, render_template, request, redirect

# DB imports
from db import (
    add_order,
    get_pending_orders,
    get_order_by_id,
    mark_cancelled,
    mark_exited
)

# Trader actions
from trader import cancel_order, force_exit

# Upstox connectivity imports
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
        add_order((
            request.form["instrument"],
            int(request.form["qty"]),
            float(request.form["trigger"]),
            float(request.form["limit"]),
            float(request.form["sl"])
        ))
        return redirect("/")

    orders = get_pending_orders()
    return render_template("index.html", orders=orders)


# ===============================
# CANCEL ORDER (before execution)
# ===============================
@app.route("/cancel/<int:order_id>")
def cancel(order_id):
    order = get_order_by_id(order_id)

    if not order:
        return "Order not found", 404

    instrument, qty, entry_order_id, sl_order_id, status = order

    # Allow cancel ONLY if still pending
    if status != "PENDING":
        return redirect("/")

    # Cancel on Upstox only if entry was placed
    if entry_order_id:
        try:
            cancel_order(entry_order_id)
        except Exception as e:
            print(f"Upstox cancel failed: {e}")

    mark_cancelled(order_id)
    return redirect("/")


# ===============================
# FORCE EXIT (market sell)
# ===============================
@app.route("/exit/<int:order_id>")
def exit_trade(order_id):
    order = get_order_by_id(order_id)

    if not order:
        return "Order not found", 404

    instrument, qty, entry_order_id, sl_order_id, status = order

    # Exit allowed ONLY if trade executed
    if status != "EXECUTED":
        return redirect("/")

    try:
        force_exit(instrument, qty)
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
    app.run(host="0.0.0.0", port=5000, debug=True)
