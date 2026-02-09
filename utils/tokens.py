# Shared token lists (kept import-light to avoid circular deps)

# Index tokens are exchange-specific. Sensex is BSE_CM (exchangeType=3).
NSE_INDEX_TOKENS = ["26000", "26009", "26037", "53886"]
BSE_INDEX_TOKENS = ["19000"]  # SENSEX (BSE INDEX)

INDEX_TOKENS = NSE_INDEX_TOKENS + BSE_INDEX_TOKENS
