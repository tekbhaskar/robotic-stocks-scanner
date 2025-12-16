import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Robotics Market Screener", layout="wide")
st.title("🤖 Robotics Stock Screener (Small, Mid, Large Cap, ETF's)")

# Auto refresh every 30 seconds
_ = st_autorefresh(interval=90000, key="refresh")

# -------------------------------------------------------
# ROBOTICS STOCK GROUPS
# -------------------------------------------------------
LARGE_CAP = {
    "ISRG": "Intuitive Surgical",
    "NVDA": "NVIDIA",
    "AMZN": "Amazon Robotics",
    "TSLA": "Tesla Robotics/AI",
    "ROK": "Rockwell Automation",
    "ABBNY": "ABB Ltd",
}

MID_CAP = {
    "CGNX": "Cognex",
    "TER": "Teradyne / UR",
    "PATH": "UiPath",
    "FANUY": "Fanuc",
}

SMALL_CAP = {
    "KITT": "Robotic Research",
    "ARBE": "Arbe Robotics",
    "ROBO": "ROBO ETF",
    "BOTZ": "BOTZ ETF",
    "VICR": "Vicor",
    "RR": "Ritch Tech Robotics",
    "SERV": "Servotronics",
    "SYM": "Service Robotics",
    "MYO": "Myo Robotics",
    "BBAI": "BigBear.ai",
    "EVLV": "Evolv Technologies",
    "AMCI": "AMC Industrial Robotics",
    
    
}

ETF_CAP = {
    "ROBO": "ROBO Global Robotics & Automation ETF",
    "BOTZ": "Global X Robotics & Artificial Intelligence ETF",
    "ARKQ": "ARK Autonomous Technology & Robotics ETF",
    "IRBO": "iRobot Corporation ETF",
     
}

ALL_TICKERS = list(LARGE_CAP.keys()) + list(MID_CAP.keys()) + list(SMALL_CAP.keys()) + list(ETF_CAP.keys())

GROUP_MAP = {
    **{k: "Large Cap Robotics" for k in LARGE_CAP},
    **{k: "Mid Cap Robotics" for k in MID_CAP},
    **{k: "Small Cap Robotics" for k in SMALL_CAP},
    **{k: "Robotics ETF" for k in ETF_CAP},
}

NAME_MAP = {**LARGE_CAP, **MID_CAP, **SMALL_CAP, **ETF_CAP}


# -------------------------------------------------------
# FETCH LIVE PRICES
# -------------------------------------------------------
def fetch_data(tickers):
    rows = []

    hist = yf.download(
        tickers=" ".join(tickers),
        period="5d",
        interval="1d",
        group_by="ticker",
        progress=False,
    )

    for tk in tickers:
        prev_close = np.nan
        price = np.nan
        pct = np.nan

        # Previous Close
        try:
            closes = hist[tk]["Close"].dropna()
            if len(closes) >= 2:
                prev_close = closes.iloc[-2]
        except:
            pass

        # Live price (safe fallback)
        t = yf.Ticker(tk)
        try:
            price = t.fast_info.last_price
        except:
            price = t.info.get("regularMarketPrice", np.nan)

        # % Change
        try:
            pct = ((price - prev_close) / prev_close) * 100
        except:
            pct = np.nan

        rows.append({
            "Symbol": tk,
            "Company": NAME_MAP.get(tk, ""),
            "Group": GROUP_MAP.get(tk, ""),
            "Prev Close ($)": round(prev_close, 2) if prev_close == prev_close else np.nan,
            "Live Price ($)": round(price, 2) if price == price else np.nan,
            "% Change": round(pct, 2) if pct == pct else np.nan,
        })

    return pd.DataFrame(rows)


df = fetch_data(ALL_TICKERS)


# -------------------------------------------------------
# COLOR HIGHLIGHT FUNCTION
# -------------------------------------------------------
def highlight_change(val):
    try:
        if val > 0:
            return "color: green; font-weight: bold;"
        elif val < 0:
            return "color: red; font-weight: bold;"
    except:
        pass
    return ""


styled = df.style.applymap(highlight_change, subset=["% Change"])


# -------------------------------------------------------
# DISPLAY TABLE
# -------------------------------------------------------
st.subheader("📡 Real-Time Robotics Screener")
#st.dataframe(styled, use_container_width=True)


    


# create tabs for each group
tabs = st.tabs(["Large Cap Robotics", "Mid Cap Robotics", "Small Cap Robotics", "Robotics ETFs"])
group_names = ["Large Cap Robotics", "Mid Cap Robotics", "Small Cap Robotics", "Robotics ETF"]
for tab, group in zip(tabs, group_names):
    with tab:
        st.subheader(f"📡 {group} Stocks")
        df_group = df[df["Group"] == group]
        styled_group = df_group.style.applymap(highlight_change, subset=["% Change"])
        st.dataframe(styled_group, use_container_width=True)    
    # with st.expander("Debug Data"):
    #      st.write(df_group)
# -------------------------
# Manulal refresh button
if st.button("🔄 Refresh Data"):    
    st.experimental_rerun()
