#import time
#from upstox_client import Configuration, ApiClient
#from upstox_client.apis import OrderApi
#from upstox_client.models import PlaceOrderRequest
#from config import ACCESS_TOKEN


import time
from upstox_client import Configuration, ApiClient
from upstox_client.api.order_api import OrderApi
from upstox_client.models.place_order_request import PlaceOrderRequest
from config import ACCESS_TOKEN



POLL_INTERVAL = 2        # seconds
MAX_WAIT_TIME = 60       # seconds


def get_api():
    cfg = Configuration()
    cfg.access_token = ACCESS_TOKEN
    return ApiClient(cfg)


# ===============================
# PLACE ENTRY ONLY
# ===============================
def place_entry(order):
    """
    Places BUY SL-LIMIT entry
    """
    _, instrument, qty, trigger, limit_price, _ = order

    with get_api() as client:
        api = OrderApi(client)

        entry = PlaceOrderRequest(
            instrument_token=instrument,
            quantity=qty,
            order_type="SL",
            transaction_type="BUY",
            product="I",
            price=limit_price,
            trigger_price=trigger,
            validity="DAY",
            is_amo=False
        )

        resp = api.place_order(entry)
        return resp.data.order_id


# ===============================
# WAIT FOR ENTRY EXECUTION
# ===============================
def wait_for_entry_execution(order_id):
    """
    Polls Upstox until entry is COMPLETE or timeout
    """
    with get_api() as client:
        api = OrderApi(client)

        waited = 0
        while waited < MAX_WAIT_TIME:
            order = api.get_order_details(order_id)
            status = order.data.status

            if status == "COMPLETE":
                return True

            if status in ("REJECTED", "CANCELLED"):
                return False

            time.sleep(POLL_INTERVAL)
            waited += POLL_INTERVAL

        return False


# ===============================
# PLACE STOP LOSS (ONLY AFTER ENTRY)
# ===============================
def place_stop_loss(instrument, qty, sl):
    """
    Places SELL SL after entry execution
    """
    with get_api() as client:
        api = OrderApi(client)

        sl_order = PlaceOrderRequest(
            instrument_token=instrument,
            quantity=qty,
            order_type="SL",
            transaction_type="SELL",
            product="I",
            price=round(sl - 0.2, 2),
            trigger_price=sl,
            validity="DAY",
            is_amo=False
        )

        resp = api.place_order(sl_order)
        return resp.data.order_id


# ===============================
# FORCE EXIT (MARKET)
# ===============================
def force_exit(instrument, qty):
    with get_api() as client:
        api = OrderApi(client)

        exit_order = PlaceOrderRequest(
            instrument_token=instrument,
            quantity=qty,
            order_type="MARKET",
            transaction_type="SELL",
            product="I",
            validity="DAY",
            is_amo=False
        )

        resp = api.place_order(exit_order)
        return resp.data.order_id
# ===============================
# CANCEL ORDER
# ===============================
def cancel_order(order_id):
    with get_api() as client:
        api = OrderApi(client)
        api.cancel_order(order_id)
