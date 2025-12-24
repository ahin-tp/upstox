import schedule
import time
import pytz
from datetime import datetime

from db import (
    get_pending_orders,
    save_order_ids
)
from trader import (
    place_entry,
    wait_for_entry_execution,
    place_stop_loss
)

TIMEZONE = pytz.timezone("Asia/Kolkata")
RUN_TIME = "09:15:05"


def run_orders():
    now = datetime.now(TIMEZONE).strftime("%H:%M:%S")
    print(f"[{now}] Scheduler started")

    orders = get_pending_orders()

    for order in orders:
        try:
            db_id, instrument, qty, trigger, limit_price, sl = order

            print(f"Placing ENTRY for DB ID {db_id}")

            # 1️⃣ Place ENTRY
            entry_order_id = place_entry(order)

            print(f"ENTRY placed: {entry_order_id}")

            # 2️⃣ Wait for execution
            executed = wait_for_entry_execution(entry_order_id)

            if not executed:
                print(f"ENTRY not executed for DB ID {db_id}")
                continue

            print(f"ENTRY executed for DB ID {db_id}")

            # 3️⃣ Place STOP LOSS
            sl_order_id = place_stop_loss(instrument, qty, sl)

            # 4️⃣ Save order IDs
            save_order_ids(db_id, entry_order_id, sl_order_id)

            print(
                f"DB:{db_id} ENTRY:{entry_order_id} SL:{sl_order_id}"
            )

        except Exception as e:
            print(f"❌ Error for DB ID {order[0]} → {e}")


schedule.every().day.at(RUN_TIME).do(run_orders)

print("⏳ Waiting for 9:15 AM IST...")

while True:
    schedule.run_pending()
    time.sleep(1)
