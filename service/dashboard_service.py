import plotly.graph_objects as go

from database.order_dao import get_orders_sorted, get_weekly_orders
from database.stockdao import get_stock_short_name_by_token


def weekly_orders_chart(user_id):

    orders = get_weekly_orders(user_id)

    x = orders.get("week_start", [])
    y = orders.get("total_orders", [])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x,
        y=y,
        marker_color="#4fad96",
        text=y,
        textposition="outside",
        hovertemplate="<b>Week</b>: %{x}<br><b>Orders</b>: %{y}<extra></extra>"
    ))

    fig.update_layout(
        template="plotly_white",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        title=dict(
            text="Weekly Orders",
            x=0.02,
            font=dict(size=18, weight=600)
        ),
        xaxis=dict(
            title="Week Starting",
            showgrid=False
        ),
        yaxis=dict(
            title="Total Orders",
            gridcolor="#e5e7eb"
        )
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


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
            buy_queues.setdefault(symbol, []).append(
                {"qty": qty, "price": price})
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

    wins = int(results.get("wins", 0))
    losses = int(results.get("losses", 0))

    total = wins + losses

    # No trades case
    if total == 0:

        fig = go.Figure()

        fig.add_annotation(
            text="No closed trades yet",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="#6b7280")
        )

        fig.update_layout(
            template="plotly_white",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
            title=dict(
                text="Win Rate",
                x=0.02,
                font=dict(size=18)
            )
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    fig = go.Figure()

    fig.add_trace(go.Pie(

        labels=["Wins", "Losses"],

        values=[wins, losses],

        hole=0.55,

        marker=dict(
            colors=["#22c55e", "#ef4444"]
        ),

        textinfo="percent",

        hovertemplate="<b>%{label}</b><br>"
        "Trades: %{value}<br>"
        "Percentage: %{percent}<extra></extra>"

    ))

    # Center text
    fig.add_annotation(

        text=f"<b>{total}</b><br>Trades",

        x=0.5,
        y=0.5,

        showarrow=False,

        font=dict(
            size=20,
            color="#111827"
        )

    )

    fig.update_layout(

        template="plotly_white",

        height=320,

        margin=dict(l=20, r=20, t=40, b=20),

        title=dict(
            text="Win Rate",
            x=0.02,
            font=dict(size=18)
        ),

        showlegend=True,

        legend=dict(
            orientation="v",
            y=0.9,
            x=1
        )

    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def profit_loss_chart(user_id):

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

    fig = go.Figure()

    fig.add_trace(go.Bar(

        x=["Profit", "Loss"],

        y=[total_profit, total_loss],

        marker_color=["#22c55e", "#ef4444"],

        text=[
            f"{total_profit:.2f}",
            f"{total_loss:.2f}"
        ],

        textposition="outside",

        hovertemplate="<b>%{x}</b><br>"
        "Amount: ₹%{y:.2f}<extra></extra>"

    ))

    fig.update_layout(

        template="plotly_white",

        height=300,

        margin=dict(l=20, r=20, t=40, b=20),

        title=dict(
            text="Profit / Loss",
            x=0.02,
            font=dict(size=18)
        ),

        yaxis=dict(
            title="Amount",
            gridcolor="#e5e7eb"
        )

    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def top_traded_chart(user_id, limit=5):

    orders = get_orders_sorted(user_id)

    counts = {}

    name_cache = {}

    for o in orders:

        token = str(o.get("symbol_token"))

        if token not in name_cache:

            row = get_stock_short_name_by_token(token)

            name_cache[token] = row if row else token

        name = name_cache[token]

        counts[name] = counts.get(name, 0) + 1

    top = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]

    labels = [x[0] for x in top]

    values = [x[1] for x in top]

    # No data case
    if not labels:

        fig = go.Figure()

        fig.add_annotation(

            text="No orders yet",

            x=0.5,
            y=0.5,

            showarrow=False,

            font=dict(size=16)

        )

        fig.update_layout(

            template="plotly_white",

            height=320,

            title=dict(
                text="Top Traded",
                x=0.02
            )

        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    fig = go.Figure()

    fig.add_trace(go.Bar(

        x=labels,

        y=values,

        marker_color="#3b82f6",

        text=values,

        textposition="outside",

        hovertemplate="<b>%{x}</b><br>"
        "Orders: %{y}<extra></extra>"

    ))

    fig.update_layout(

        template="plotly_white",

        height=320,

        margin=dict(l=20, r=20, t=40, b=20),

        title=dict(
            text="Top Traded",
            x=0.02,
            font=dict(size=18)
        ),

        yaxis=dict(
            title="Orders",
            gridcolor="#e5e7eb"
        )

    )

    return fig.to_html(full_html=False, include_plotlyjs=False)
