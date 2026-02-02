'''
CORRUPTED CONTENT (kept for reference only). This entire block is ignored.
'''

'''
import io
import base64
import matplotlib.pyplot as plt
from database.order_dao import get_weekly_orders,get_orders_sorted
def weekly_orders_chart(user_id): 
    orders = get_weekly_orders(user_id) 
    x = orders["week_start"] 
    y = orders["total_orders"] # 🔥 VERY IMPORTANT 

        # IMPORTANT: force non-GUI backend for Flask/threads (prevents Tkinter "main loop" crashes)
        matplotlib.use("Agg")

        import matplotlib.pyplot as plt

        with plt.style.context("dark_background"):
            fig, ax = plt.subplots(figsize=(7, 3))
            ax.bar(x, y, color="#4ade80")
            ax.set_xlabel("Week Starting")
            ax.set_ylabel("Total Orders")
            ax.set_title("Weekly Orders")
            ax.tick_params(axis="x", rotation=45)

            debug_path = f"weekly_orders_debug_user_{user_id}.png"
            fig.savefig(debug_path, bbox_inches="tight")
            return _fig_to_base64(fig)
def calculate_win_loss(user_id):
    orders = get_orders_sorted(user_id)  
    # ORDER BY created_at ASC

    buy_stack = {}
    wins = 0
    losses = 0

    for o in orders:
        key = o["symbol_token"]

        if o["transaction_type"] == "BUY":
            buy_stack.setdefault(key, []).append(o)

        elif o["transaction_type"] == "SELL":
            if key in buy_stack and buy_stack[key]:
                buy = buy_stack[key].pop(0)  # FIFO

                profit = (o["price"] - buy["price"]) * min(
                    o["quantity"], buy["quantity"]
                )

                if profit > 0:
                    wins += 1
                else:
                    losses += 1

    return {
        "wins": wins,
        "losses": losses
    }

def win_rate_chart(user_id):
    results = calculate_win_loss(user_id)
    wins = results["wins"]
    losses = results["losses"]

        # If user has no closed trades yet (or all profit computations are 0), pie chart will break.
        if (wins + losses) == 0:
            with plt.style.context("dark_background"):
                import base64
                import io

                import matplotlib

                # Force a non-GUI backend so charts can be rendered from Flask request threads.
                matplotlib.use("Agg")

                import matplotlib.pyplot as plt

                from database.order_dao import get_orders_sorted, get_weekly_orders


                def _fig_to_base64(fig) -> str:
                    img = io.BytesIO()
                    fig.savefig(img, format="png", bbox_inches="tight")
                    plt.close(fig)
                    img.seek(0)
                    return base64.b64encode(img.getvalue()).decode("utf-8")


                def weekly_orders_chart(user_id):
                    orders = get_weekly_orders(user_id)
                    x = orders.get("week_start", [])
                    y = orders.get("total_orders", [])

                    with plt.style.context("dark_background"):
                        fig, ax = plt.subplots(figsize=(7, 3))
                        ax.bar(x, y, color="#4ade80")
                        ax.set_xlabel("Week Starting")
                        ax.set_ylabel("Total Orders")
                        ax.set_title("Weekly Orders")
                        ax.tick_params(axis="x", rotation=45)
                        fig.savefig(f"weekly_orders_debug_user_{user_id}.png", bbox_inches="tight")
                        return _fig_to_base64(fig)


                def calculate_win_loss(user_id):
                    orders = get_orders_sorted(user_id)

                    buy_stack = {}
                    wins = 0
                    losses = 0

                    for o in orders:
                        key = o["symbol_token"]
                        side = str(o["transaction_type"]).upper()

                        if side == "BUY":
                            buy_stack.setdefault(key, []).append({
                                "quantity": float(o["quantity"]),i
                                "price": float(o["price"]),
                            })
                            continue

                        if side == "SELL":
                            if key in buy_stack and buy_stack[key]:
                                buy = buy_stack[key].pop(0)  # FIFO
                                sell_qty = float(o["quantity"])
                                buy_qty = float(buy["quantity"])
                                profit = (float(o["price"]) - float(buy["price"])) * min(sell_qty, buy_qty)
                                if profit > 0:
                                    wins += 1
                                else:
                                    losses += 1

                    return {"wins": wins, "losses": losses}


                def win_rate_chart(user_id):
                    results = calculate_win_loss(user_id)
                    wins = int(results.get("wins", 0) or 0)
                    losses = int(results.get("losses", 0) or 0)

                    if (wins + losses) == 0:
                        with plt.style.context("dark_background"):
                            fig, ax = plt.subplots(figsize=(5, 3))
                            ax.set_title("Win Rate")
                            ax.text(0.5, 0.5, "No closed trades yet", ha="center", va="center")
                            ax.axis("off")
                            return _fig_to_base64(fig)

                    labels = ["Wins", "Losses"]
                    sizes = [wins, losses]
                    colors = ["#22c55e", "#ef4444"]

                    with plt.style.context("dark_background"):
                        fig, ax = plt.subplots(figsize=(5, 5))
                        ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140)
                        ax.set_title("Win Rate", fontsize=12, fontweight="bold", pad=10)
                        fig.savefig(f"win_rate_debug_user_{user_id}.png", bbox_inches="tight")
                        return _fig_to_base64(fig)


                def profit_loss_chart(user_id):
                    """Realized P/L by symbol (FIFO matching of BUY/SELL orders)."""
                    orders = get_orders_sorted(user_id)

                    lots_by_symbol = {}
                    pnl_by_symbol = {}

                    for o in orders:
                        symbol = str(o.get("symbol_token"))
                        side = str(o.get("transaction_type") or "").upper()
                        qty = float(o.get("quantity") or 0)
                        price = float(o.get("price") or 0)
                        if qty <= 0:
                            continue

                        if side == "BUY":
                            lots_by_symbol.setdefault(symbol, []).append({"qty": qty, "price": price})
                            continue

                        if side == "SELL":
                            remaining = qty
                            lots = lots_by_symbol.get(symbol, [])
                            while remaining > 0 and lots:
                                lot = lots[0]
                                matched = min(remaining, lot["qty"])
                                pnl_by_symbol[symbol] = pnl_by_symbol.get(symbol, 0.0) + (price - lot["price"]) * matched
                                lot["qty"] -= matched
                                remaining -= matched
                                if lot["qty"] <= 0:
                                    lots.pop(0)

                    labels = list(pnl_by_symbol.keys())
                    values = [pnl_by_symbol[k] for k in labels]

                    with plt.style.context("dark_background"):
                        fig, ax = plt.subplots(figsize=(7, 3))
                        ax.set_title("Profit / Loss")
                        if not labels:
                            ax.text(0.5, 0.5, "No realized P/L yet", ha="center", va="center")
                            ax.axis("off")
                            return _fig_to_base64(fig)

                        bar_colors = ["#22c55e" if v >= 0 else "#ef4444" for v in values]
                        ax.bar(labels, values, color=bar_colors)
                        ax.set_ylabel("P/L")
                        ax.tick_params(axis="x", rotation=45)
                        return _fig_to_base64(fig)
'''

# --- Clean implementation below ---

import base64
import io

import matplotlib

# Force a non-GUI backend so charts can be rendered from Flask request threads.
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from database.order_dao import get_orders_sorted, get_weekly_orders


def _fig_to_base64(fig) -> str:
    img = io.BytesIO()
    fig.savefig(img, format="png", bbox_inches="tight")
    plt.close(fig)
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode("utf-8")


def weekly_orders_chart(user_id):
    orders = get_weekly_orders(user_id)
    x = orders.get("week_start", [])
    y = orders.get("total_orders", [])

    fig, ax = plt.subplots(figsize=(7, 3))

    # --- White background ---
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # --- Bar chart with soft color ---
    bars = ax.bar(x, y, color="#4fad96", edgecolor="#166534", linewidth=0.6)

    # --- Labels & title ---
    ax.set_xlabel("Week Starting", fontsize=10, labelpad=8)
    ax.set_ylabel("Total Orders", fontsize=10, labelpad=8)
    ax.set_title("Weekly Orders", fontsize=12, fontweight="bold", pad=10)

    # --- Grid (light & clean) ---
    ax.set_axisbelow(True)

    # --- X ticks rotation ---
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)

    # --- Remove extra borders (modern look) ---
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # --- Value labels on bars (attractive touch) ---
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=8
        )

    # # --- Save figure ---
    # fig.savefig(
    #     f"weekly_orders_user_{user_id}.png",
    #     dpi=150,
    #     bbox_inches="tight",
    #     facecolor="white"
    # )

    return _fig_to_base64(fig)


def calculate_win_loss(user_id):
    orders = get_orders_sorted(user_id)
    buy_queues = {}
    wins = 0
    losses = 0

    for o in orders:
        symbol = o.get("symbol_token")
        side = str(o.get("transaction_type") or "").upper()
        qty = float(o.get("quantity") or 0)
        price = float(o.get("price") or 0)
        if qty <= 0:
            continue

        if side == "BUY":
            buy_queues.setdefault(symbol, []).append({"qty": qty, "price": price})
            continue

        if side == "SELL":
            q = buy_queues.get(symbol, [])
            if not q:
                continue

            lot = q[0]
            matched = min(qty, lot["qty"])
            profit = (price - lot["price"]) * matched

            if profit > 0:
                wins += 1
            else:
                losses += 1

            lot["qty"] -= matched
            if lot["qty"] <= 0:
                q.pop(0)

    return {"wins": wins, "losses": losses}


def win_rate_chart(user_id):
    results = calculate_win_loss(user_id)
    wins = int(results.get("wins", 0) or 0)
    losses = int(results.get("losses", 0) or 0)

    # --- No trades case ---
    if (wins + losses) == 0:
        fig, ax = plt.subplots(figsize=(5, 3))

        # White background
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        ax.set_title("Win Rate", fontsize=12, fontweight="bold", pad=10)
        ax.text(
            0.5, 0.5,
            "No closed trades yet",
            ha="center",
            va="center",
            fontsize=10,
            color="#6b7280"
        )
        ax.axis("off")

        return _fig_to_base64(fig)

    # --- Data ---
    labels = ["Wins", "Losses"]
    sizes = [wins, losses]
    colors = ["#22c55e", "#ef4444"]  # green & red

    fig, ax = plt.subplots(figsize=(5, 5))

    # White background
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Pie chart (donut style → more attractive)
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops=dict(width=0.45, edgecolor="white")
    )

    # Text styling
    for text in texts:
        text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("black")

    # Center text (extra UI touch)
    ax.text(
        0, 0,
        f"{wins + losses}\nTrades",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="#374151"
    )

    ax.set_title("Win Rate", fontsize=12, fontweight="bold", pad=12)

    # fig.savefig(
    #     f"win_rate_user_{user_id}.png",
    #     dpi=150,
    #     bbox_inches="tight",
    #     facecolor="white"
    # )

    return _fig_to_base64(fig)



def profit_loss_chart(user_id):
    """Total realized Profit vs Loss using FIFO BUY/SELL matching."""
    orders = get_orders_sorted(user_id)

    lots_by_symbol = {}
    total_profit = 0.0
    total_loss = 0.0

    for o in orders:
        symbol = str(o.get("symbol_token"))
        side = str(o.get("transaction_type") or "").upper()
        qty = float(o.get("quantity") or 0)
        price = float(o.get("price") or 0)

        if qty <= 0:
            continue

        if side == "BUY":
            lots_by_symbol.setdefault(symbol, []).append({
                "qty": qty,
                "price": price
            })

        elif side == "SELL":
            remaining = qty
            lots = lots_by_symbol.get(symbol, [])

            while remaining > 0 and lots:
                lot = lots[0]
                matched = min(remaining, lot["qty"])

                pnl = (price - lot["price"]) * matched

                if pnl > 0:
                    total_profit += pnl
                else:
                    total_loss += abs(pnl)

                lot["qty"] -= matched
                remaining -= matched

                if lot["qty"] <= 0:
                    lots.pop(0)

    # --------- CHART PART ----------
    labels = ["Profit", "Loss"]
    values = [total_profit, total_loss]
    colors = ["#22c55e", "#ef4444"]  # green, red

    fig, ax = plt.subplots(figsize=(6, 3))

    # --- White background ---
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # --- Bars ---
    bars = ax.bar(labels, values, color=colors, width=0.45)

    # --- Title & labels ---
    ax.set_title("Total Profit / Loss", fontsize=12, fontweight="bold", pad=10)
    ax.set_ylabel("Amount", fontsize=10)

    # --- Grid (soft) ---
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    # --- Remove extra borders ---
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # --- Value labels on bars ---
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#111827"
        )

    # --- Ticks styling ---
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)

    # fig.savefig(
    #     "total_profit_loss.png",
    #     dpi=150,
    #     bbox_inches="tight",
    #     facecolor="white"
    # )

    return _fig_to_base64(fig)



def top_traded_chart(user_id, limit=5):
    orders = get_orders_sorted(user_id)
    counts = {}
    for o in orders:
        symbol = str(o.get("symbol_token"))
        counts[symbol] = counts.get(symbol, 0) + 1

    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[: max(0, int(limit))]
    labels = [k for k, _ in top]
    values = [v for _, v in top]

    fig, ax = plt.subplots(figsize=(7, 3))

    # --- White background ---
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.set_title("Top Traded", fontsize=12, fontweight="bold", pad=10)

    # --- No data case ---
    if not labels:
        ax.text(
            0.5, 0.5,
            "No orders yet",
            ha="center",
            va="center",
            fontsize=10,
            color="#6b7280"
        )
        ax.axis("off")
        return _fig_to_base64(fig)

    # --- Bars ---
    bars = ax.bar(labels, values, color="#60a5fa", width=0.5)

    # --- Y label ---
    ax.set_ylabel("Orders", fontsize=10)

    # --- Grid (soft & clean) ---
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    # --- Ticks styling ---
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)

    # --- Remove extra borders (modern look) ---
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # --- Value labels on bars (nice touch) ---
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#111827"
        )

    # fig.savefig(
    #     "top_traded.png",
    #     dpi=150,
    #     bbox_inches="tight",
    #     facecolor="white"
    # )

    return _fig_to_base64(fig)
