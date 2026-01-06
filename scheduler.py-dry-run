import schedule
import time
import pytz
from datetime import datetime, time as dtime, timedelta


from db import (
    get_pending_orders,
    get_all_orders,
    save_order_ids,
    mark_cancelled,
    mark_exited
)

from trader import (
    place_entry,
    wait_for_entry_execution,
    place_stop_loss,
    get_order_status,
    has_open_position,
    test_upstox_connectivity
)

# ===============================
# CONFIG
# ===============================
TIMEZONE = pytz.timezone("Asia/Kolkata")

DRY_RUN = True   # 🔥 IMPORTANT: Dry run mode

# 🔁 Trigger in 1 minute from now (for testing)
ENTRY_TIME = (datetime.now(TIMEZONE) + timedelta(minutes=1)).time()

WINDOW_SECONDS = 30
entry_done_today = False


# ===============================
# ENTRY FLOW
# ===============================
def run_orders():
    now = datetime.now(TIMEZONE).strftime("%H:%M:%S")
    print(f"[{now}] 🚀 Scheduler started (ENTRY FLOW)", flush=True)

    # ===============================
    # CONNECTIVITY + FUNDS CHECK
    # ===============================
    conn_info = test_upstox_connectivity()

    if conn_info["status"] != "OK":
        print("❌ Upstox connectivity FAILED", conn_info, flush=True)
        print("⛔ ENTRY ABORTED", flush=True)
        return

    print(
        f"✅ Upstox OK | User={conn_info['user']} | "
        f"Positions={conn_info['positions_count']}",
        flush=True
    )


    # ===============================
    # FETCH ORDERS
    # ===============================
    orders = get_pending_orders()

    if not orders:
        print("ℹ️ No pending orders found", flush=True)
        return

    for order in orders:
        db_id, instrument, qty, trigger, limit_price, sl = order

        print(f"📥 Processing DB ID {db_id}", flush=True)
        print(
            f"    Instrument={instrument}, Qty={qty}, "
            f"Trigger={trigger}, Limit={limit_price}, SL={sl}",
            flush=True
        )

        if DRY_RUN:
            print(
                f"🧪 DRY RUN → Order validated, NOT sent to Upstox (DB ID {db_id})",
                flush=True
            )
            continue

        # ===============================
        # LIVE TRADING FLOW
        # ===============================
        entry_order_id = place_entry(order)
        executed = wait_for_entry_execution(entry_order_id)

        if not executed:
            print(f"❌ Entry failed for DB ID {db_id}", flush=True)
            mark_cancelled(db_id)
            continue

        sl_order_id = place_stop_loss(instrument, qty, sl)
        save_order_ids(db_id, entry_order_id, sl_order_id)

        print(
            f"✅ LIVE ENTRY DONE | DB:{db_id} ENTRY:{entry_order_id} SL:{sl_order_id}",
            flush=True
        )



# ===============================
# ENTRY GUARD
# ===============================
def entry_guard():
    global entry_done_today

    now = datetime.now(TIMEZONE)

    target_time = now.replace(
        hour=ENTRY_TIME.hour,
        minute=ENTRY_TIME.minute,
        second=ENTRY_TIME.second,
        microsecond=0
    )

    diff_seconds = abs((now - target_time).total_seconds())

    if diff_seconds <= WINDOW_SECONDS and not entry_done_today:
        print("🚀 ENTRY WINDOW HIT", flush=True)
        run_orders()
        entry_done_today = True


# ===============================
# RECONCILIATION (UNCHANGED)
# ===============================
def reconcile_with_upstox():
    now = datetime.now(TIMEZONE).strftime("%H:%M:%S")
    print(f"[{now}] 🔄 Reconciliation started", flush=True)

    orders = get_all_orders()

    for o in orders:
        (
            db_id,
            instrument,
            qty,
            trigger,
            limit_price,
            sl,
            entry_order_id,
            sl_order_id,
            status
        ) = o

        try:
            if status == "PENDING" and entry_order_id:
                broker_status = get_order_status(entry_order_id)
                if broker_status in ("CANCELLED", "REJECTED"):
                    mark_cancelled(db_id)

            if status == "EXECUTED":
                if not has_open_position(instrument):
                    mark_exited(db_id)

        except Exception as e:
            print(f"❌ RECON ERROR DB ID {db_id} → {e}", flush=True)


# ===============================
# SCHEDULER SETUP
# ===============================
schedule.every(5).seconds.do(entry_guard)
schedule.every(1).minutes.do(reconcile_with_upstox)

print("⏳ Scheduler running (ENTRY + RECONCILIATION) [DRY RUN MODE]", flush=True)

while True:
    schedule.run_pending()
    time.sleep(1)
