import time
from upstox_client import Configuration, ApiClient
from upstox_client.api.order_api import OrderApi
from upstox_client.api.portfolio_api import PortfolioApi
from upstox_client.models.place_order_request import PlaceOrderRequest
from config import ACCESS_TOKEN


# ===============================
# API CLIENT
# ===============================
def get_api():
    cfg = Configuration()
    cfg.access_token = ACCESS_TOKEN
    return ApiClient(cfg)


# ===============================
# PLACE ENTRY (SL-LIMIT → TRIGGER PENDING)
# ===============================
def place_entry(instrument, qty, trigger, limit_price):
    """
    Places BUY SL-LIMIT order.
    Appears as TRIGGER PENDING in Upstox.
    """
    client = get_api()
    api = OrderApi(client)

    entry = PlaceOrderRequest(
        instrument_token=instrument,
        quantity=qty,
        disclosed_quantity=0,
        order_type="SL",
        transaction_type="BUY",
        product="I",
        price=limit_price,
        trigger_price=trigger,
        validity="DAY",
        is_amo=False
    )

    resp = api.place_order(api_version="2.0", body=entry)
    return resp.data.order_id


# ===============================
# PLACE STOP LOSS (AFTER ENTRY COMPLETE)
# ===============================
def place_stop_loss(instrument, qty, sl):
    client = get_api()
    api = OrderApi(client)

    sl_order = PlaceOrderRequest(
        instrument_token=instrument,
        quantity=qty,
        disclosed_quantity=0,
        order_type="SL",
        transaction_type="SELL",
        product="I",
        price=round(sl - 0.2, 2),
        trigger_price=sl,
        validity="DAY",
        is_amo=False
    )

    resp = api.place_order(api_version="2.0", body=sl_order)
    return resp.data.order_id


# ===============================
# ORDER STATUS
# ===============================
def get_order_status(order_id):
    client = get_api()
    api = OrderApi(client)

    resp = api.get_order_details(api_version="2.0", order_id=order_id)

    if not resp.data:
        return "UNKNOWN"

    return resp.data[0].status


# ===============================
# POSITION CHECK
# ===============================
def has_open_position(instrument):
    client = get_api()
    portfolio_api = PortfolioApi(client)

    positions = portfolio_api.get_positions(api_version="2.0")

    for p in positions.data:
        if p.instrument_token == instrument and p.quantity != 0:
            return True

    return False

# ===============================
# CANCEL ORDER (USED BY app.py)
# ===============================
def cancel_order(order_id):
    """
    Cancels an open order in Upstox.
    Used by web UI.
    """
    if not order_id:
        return

    client = get_api()
    api = OrderApi(client)

    api.cancel_order(
        api_version="2.0",
        order_id=order_id
    )

# ===============================
# FORCE EXIT (MARKET) – USED BY app.py
# ===============================
def force_exit(instrument, qty):
    """
    Force exit a position using MARKET order.
    Used by web UI.
    """
    client = get_api()
    api = OrderApi(client)

    exit_order = PlaceOrderRequest(
        instrument_token=instrument,
        quantity=qty,
        disclosed_quantity=0,
        order_type="MARKET",
        transaction_type="SELL",
        product="I",
        validity="DAY",
        is_amo=False
    )

    resp = api.place_order(
        api_version="2.0",
        body=exit_order
    )

    return resp.data.order_id
