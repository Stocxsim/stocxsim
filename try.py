from SmartApi import SmartConnect
from datetime import datetime, timedelta
import numpy as np
import pyotp

API_KEY = "21E7rjit"
CLIENT_ID = "AACB894292"
CLIENT_PASSWORD  = "1408"
TOTP_SECRET = "WIEQHKYWVZYIQY3UKKHH7EGQPI"

obj = SmartConnect(api_key=API_KEY)

totp = pyotp.TOTP(TOTP_SECRET).now()
session = obj.generateSession(CLIENT_ID, CLIENT_PASSWORD, totp)

if not session or not session.get("status"):
    raise Exception("Angel One login failed")
# ===== Date Calculation =====
today = datetime.now()
from_date = today - timedelta(days=51)

fromdate_str = from_date.strftime("%Y-%m-%d 09:15")
todate_str = today.strftime("%Y-%m-%d 15:30")

# ===== Candle Params =====
historic_params = {
    "exchange": "NSE",
    "symboltoken": "3045",
    "interval": "ONE_DAY",
    "fromdate": fromdate_str,
    "todate": todate_str
}
result=obj.getCandleData(historic_params)['data']
np_result = np.array(result)

closes=np_result[:,4].astype(float)
print(closes)
# Step 1: Difference
delta = np.diff(closes)

# Step 2: Gain & Loss
gains = np.where(delta > 0, delta, 0)
losses = np.where(delta < 0, -delta, 0)

# Step 3: Average Gain/Loss (last 'period')
avg_gain = np.mean(gains[-14:])
avg_loss = np.mean(losses[-14:])

# Step 4: RS & RSI
if avg_loss == 0:
    rsi = 100.0

else:
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi= round(rsi, 2)

print(f"RSI: {rsi}")