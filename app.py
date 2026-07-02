import os
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

st.set_page_config(
    page_title="UniCredit ECM Intelligence Platform",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Styling
# ---------------------------
st.markdown(
    """
    <style>
    :root {
        --uc-red: #E30613;
        --uc-dark: #07182F;
        --uc-ink: #17212F;
        --uc-muted: #667085;
        --uc-line: #E5E7EB;
        --uc-bg: #F5F7FA;
        --uc-card: #FFFFFF;
        --uc-green: #168447;
        --uc-amber: #D98200;
    }
    .stApp { background: var(--uc-bg); }
    [data-testid="stSidebar"] { background: #161616; }
    [data-testid="stSidebar"] * { color: #F4F7FB !important; }
    [data-testid="stSidebar"] .stRadio label { font-weight: 800; }
    [data-testid="stSidebar"] .stSelectbox label { font-weight: 800; }
    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
    .uc-header {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 18px 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(7,24,47,0.04);
    }
    .uc-brand { display:flex; align-items:center; gap:13px; }
    .uc-logo img {
    height: 42px;
    width: auto;
    }
    .uc-title { font-size: 25px; font-weight: 900; letter-spacing:-0.5px; color: var(--uc-ink); line-height:1; }
    .uc-subtitle { font-size: 12px; color: var(--uc-muted); font-weight: 700; margin-top:4px; }
    .uc-pill { background:#FFF1F2; color:var(--uc-red); border:1px solid #FFD2D6; border-radius:99px; padding:7px 11px; font-weight:900; font-size:12px; }
    .hero {
        background: linear-gradient(135deg, #3A3A3A 0%, #BEBEBE 100%);
        border-radius: 10px;
        padding: 24px 26px;
        color: white;
        margin-bottom: 18px;
    }
    .hero h1 { margin:0; font-size:30px; color:white; }
    .hero p { margin:8px 0 0; color:#D8E0EA; font-size:15px; }
    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(7,24,47,0.04);
        min-height: 118px;
    }
    .metric-card small { color:#667085; text-transform:uppercase; font-weight:900; font-size:11px; }
    .metric-card b { display:block; color:#E30613; font-size:34px; margin-top:8px; line-height:1; }
    .metric-card span { display:block; color:#667085; margin-top:8px; font-size:13px; }
    .section-card {
        background:white; border:1px solid #E5E7EB; border-radius:10px; padding:18px;
        box-shadow: 0 2px 8px rgba(7,24,47,0.04);
        margin-bottom:16px;
    }
    .section-card h3 { margin-top:0; color:#17212F; }
    .score-high { color:#168447; background:#E8F5EE; padding:5px 10px; border-radius:999px; font-weight:900; }
    .score-watch { color:#D98200; background:#FFF3DF; padding:5px 10px; border-radius:999px; font-weight:900; }
    .score-low { color:#667085; background:#F1F3F6; padding:5px 10px; border-radius:999px; font-weight:900; }
    .ai-box {
        border-left: 4px solid #E30613;
        background: #FFF7F8;
        padding: 14px 15px;
        border-radius: 8px;
        color: #17212F;
        line-height: 1.48;
    }
    .kpi-ok { color:#168447; font-weight:900; }
    .kpi-no { color:#E30613; font-weight:900; }
    .small-muted { color:#667085; font-size:12px; }
    div[data-testid="stDataFrame"] { border:1px solid #E5E7EB; border-radius:8px; }
    .stButton>button { border-radius:8px; font-weight:800; border:1px solid #E5E7EB; }
    .stDownloadButton>button { border-radius:8px; font-weight:800; border:1px solid #E30613; color:#E30613; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Demo data
# ---------------------------

def demo_companies() -> pd.DataFrame:
    data = [
        ["Ferrari", "RACE", "Listed", "Italy", "Consumer Discretionary", 78500, 2400, 12, 1.2, 8, True, True, True, False, False, False, False, False, 0, 0, None, 24, 1.5, 6100, 0.9],
        ["Moncler", "MONC.MI", "Listed", "Italy", "Consumer Discretionary", 16300, 950, 16, 0.4, 13, True, True, True, False, False, False, False, False, 0, 0, None, 22, 2.1, 1800, 1.2],
        ["Stellantis", "STLAM.MI", "Listed", "Netherlands", "Consumer Discretionary", 61000, 24500, 4, 2.9, 7, True, False, True, True, True, False, True, False, 0, 0, None, 32, 6.8, 25000, 2.4],
        ["Telecom Italia", "TIT.MI", "Listed", "Italy", "Communication Services", 7300, 6200, -2, 3.8, 10, True, False, False, True, True, True, True, False, 0, 0, None, 55, 0.0, 19400, 4.1],
        ["Enel", "ENEL.MI", "Listed", "Italy", "Utilities", 69000, 22600, 3, 3.1, 23, False, False, False, False, True, False, False, False, 0, 0, None, 24, 6.2, 70000, 3.1],
        ["Leonardo", "LDO.MI", "Listed", "Italy", "Industrials", 14300, 1850, 9, 2.7, 30, False, True, False, True, True, False, False, False, 0, 0, None, 30, 0.8, 5200, 2.7],
        ["Prysmian", "PRY.MI", "Listed", "Italy", "Industrials", 17200, 2100, 7, 2.1, 4, False, True, False, True, False, False, False, False, 0, 0, None, 4, 1.6, 4300, 2.1],
        ["Saipem", "SPM.MI", "Listed", "Italy", "Energy", 5000, 980, 6, 3.3, 12, True, False, True, True, True, True, True, False, 0, 0, None, 12, 0.0, 3200, 3.3],
        ["Isar Aerospace", "Private", "Private", "Germany", "Industrials", None, 45, 55, 3.4, 0, False, False, False, True, True, False, False, True, 6, 270, "2025-03-12", 0, 0, 160, 3.4],
        ["Mistral AI", "Private", "Private", "France", "Information Technology", None, 38, 80, 1.2, 0, False, False, False, False, False, False, False, True, 3, 600, "2025-06-10", 0, 0, 620, 1.2],
        ["ICEYE", "Private", "Private", "Finland", "Industrials", None, 70, 45, 2.8, 0, False, False, False, True, False, False, False, False, 7, 1000, "2026-04-18", 0, 0, 1000, 2.8],
        ["Personio", "Private", "Private", "Germany", "Information Technology", None, 95, 28, 1.6, 0, False, False, False, False, False, False, False, True, 6, 200, "2024-11-04", 0, 0, 200, 1.6],
    ]
    cols = [
        "Company", "Ticker", "Type", "Country", "GICS Sector", "Market Cap EURm", "EBITDA EURm", "Revenue Growth %", "Net Debt / EBITDA",
        "Significant Shareholder %", "Non-Institutional Holder", "52 Week High Breach", "Previous ABB / Capital Increase", "M&A Rumor", "Leverage Deterioration",
        "Restructuring Rumor", "Frequent Issuer", "IPO Rumor", "PE Holding Years", "Last Raise Amount EURm", "Last Raise Date", "Shareholder Voting Rights %",
        "Dividend Yield %", "Net Debt EURm", "Leverage Multiple"
    ]
    df = pd.DataFrame(data, columns=cols)
    df["Last Raise Date"] = pd.to_datetime(df["Last Raise Date"], errors="coerce")
    reference_date = pd.Timestamp("2026-07-02")
    df["Months Since Last Raise"] = ((reference_date - df["Last Raise Date"]).dt.days / 30).fillna(0).round(1)
    return df


def demo_investors() -> pd.DataFrame:
    return pd.DataFrame([
        ["General Atlantic", "Growth Equity", "Information Technology;Industrials", "Series B+", "Europe;US", 150, 85000, "Late-stage growth, large tickets", "Mistral AI, Doctolib"],
        ["EQT Growth", "Growth", "Information Technology;Industrials", "Series B+", "Europe", 120, 73000, "European growth equity", "Wolt, Mambu"],
        ["General Catalyst", "Venture / Growth", "Information Technology", "Series A-C", "Europe;US", 80, 32000, "AI and software exposure", "Mistral AI, Helsing"],
        ["Atomico", "Venture Capital", "Information Technology", "Series A-C", "Europe", 45, 6000, "European tech VC", "Klarna, MessageBird"],
        ["BlackRock", "Public Equity", "All", "Listed ECM", "Global", 100, 10000000, "Long-only institutional investor", "Listed equity universe"],
        ["Capital Group", "Public Equity", "All", "Listed ECM", "Global", 90, 2500000, "Long-only institutional investor", "Global listed universe"],
        ["KKR", "Private Equity", "Consumer Discretionary;Industrials", "Late-stage / Buyout", "Global", 250, 500000, "Sponsor / potential seller", "Consumer and industrial assets"],
        ["Apollo", "Private Equity / Credit", "Industrials;Energy", "Late-stage / Credit", "Global", 220, 650000, "Sponsor and credit investor", "Industrial assets"],
    ], columns=["Investor", "Strategy", "Preferred Sector", "Stage", "Geography", "Average Ticket EURm", "AUM EURm", "Investment Preferences", "Portfolio Examples"])


def demo_settings() -> pd.DataFrame:
    rows = [
        ["ABB", "All", "shareholder", "Significant shareholder", "Significant Shareholder %", ">", 3, 20, True, "Flag if shareholder register includes significant holders above threshold."],
        ["ABB", "All", "non_institutional", "Non-institutional holder", "Non-Institutional Holder", "==", True, 20, True, "Flag PE, corporate, family office or individual investor."],
        ["ABB", "All", "52w_high", "52-week high breach", "52 Week High Breach", "==", True, 15, True, "Flag supportive share price window."],
        ["ABB", "All", "previous_abb", "Previous ABB / capital increase", "Previous ABB / Capital Increase", "==", True, 15, True, "Flag frequent seller or issuer."],
        ["ABB", "All", "ma", "M&A announced or rumored", "M&A Rumor", "==", True, 15, True, "Flag if M&A event may require capital or liquidity event."],
        ["ABB", "All", "leverage_det", "Leverage deterioration", "Leverage Deterioration", "==", True, 15, True, "Flag worsening leverage for possible primary ABB."],
        ["Rights Issue", "All", "leverage_det", "Leverage deterioration", "Leverage Deterioration", "==", True, 30, True, "Flag possible capital need."],
        ["Rights Issue", "All", "frequent_issuer", "Frequent issuer", "Frequent Issuer", "==", True, 25, True, "Flag previous primary ABB/capital increase."],
        ["Rights Issue", "All", "ma", "M&A announced or rumored", "M&A Rumor", "==", True, 25, True, "Flag potential capital need linked to M&A."],
        ["Rights Issue", "All", "restructuring", "Restructuring rumors", "Restructuring Rumor", "==", True, 20, True, "Flag restructuring-related equity need."],
        ["IPO", "All", "ipo_rumor", "IPO rumors", "IPO Rumor", "==", True, 20, True, "News run identifies IPO rumors."],
        ["IPO", "All", "pe_holding", "PE holding period", "PE Holding Years", ">", 5, 20, True, "Private equity or private investor has held company for more than threshold years."],
        ["IPO", "All", "ebitda", "EBITDA threshold", "EBITDA EURm", ">", 30, 20, True, "Strong profitability threshold."],
        ["IPO", "All", "growth", "Strong growth", "Revenue Growth %", ">", 20, 20, True, "Strong growth supports IPO readiness."],
        ["IPO", "All", "leverage", "High leverage", "Net Debt / EBITDA", ">", 3, 20, True, "High leverage after M&A activity may indicate transaction need."],
        ["PCM Fundraising", "All", "last_raise", "Recent large fundraising", "Last Raise Amount EURm", ">", 15, 10, True, "Series A+ with minimum capital raised EUR 15m."],
        ["PCM Fundraising", "All", "growth", "Growth momentum", "Revenue Growth %", ">", 25, 25, True, "Growth supports probability of new round."],
        ["PCM Fundraising", "All", "time_since", "Holding / elapsed time", "PE Holding Years", ">", 3, 10, True, "Distance from previous raise or sponsor holding period."],
        ["PCM Fundraising", "All", "ma", "Strategic activity", "M&A Rumor", "==", True, 20, True, "M&A/news activity may signal capital need."],
    ["PCM Fundraising", "All", "funding_timing", "Funding timing", "Months Since Last Raise", ">", 6, 35, True, "Companies that raised capital very recently are less likely to raise again immediately."],
        ["SES SSL", "All", "control", "Voting rights above threshold", "Shareholder Voting Rights %", ">", 50, 50, True, "Italian listed companies with controlling shareholder above threshold."],
        ["SES SSL", "All", "marketcap", "Market cap above threshold", "Market Cap EURm", ">", 800, 25, True, "Market cap filter for strategic situation lending."],
        ["SES SSL", "All", "leverage", "Net Debt / EBITDA", "Net Debt / EBITDA", ">", 2.5, 25, True, "Financial metric shown for potential SSL relevance."],
    ]
    return pd.DataFrame(rows, columns=["Product", "GICS Sector", "KPI ID", "KPI Name", "Data Field", "Comparator", "Threshold", "Weight", "Active", "Description"])


def demo_system_settings() -> pd.DataFrame:
    return pd.DataFrame([
        ["High Opportunity Threshold", 85, "Minimum score required to classify a company as High Opportunity"],
        ["Watch Threshold", 50, "Minimum score required to classify a company as Watch"],
    ], columns=["Setting", "Value", "Description"])


# ---------------------------
# Utility functions
# ---------------------------

def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if pd.isna(x):
        return False
    if isinstance(x, (int, float)):
        return bool(x)
    return str(x).strip().lower() in ["true", "yes", "y", "1", "x"]


def compare(value, comparator, threshold):
    if pd.isna(value):
        return False
    comp = str(comparator).strip()
    if isinstance(threshold, str) and threshold.lower() in ["true", "false"]:
        threshold = threshold.lower() == "true"
    if isinstance(value, str) and value.lower() in ["true", "false"]:
        value = value.lower() == "true"
    try:
        if isinstance(threshold, bool) or isinstance(value, bool):
            value_bool = normalize_bool(value)
            threshold_bool = normalize_bool(threshold)
            return value_bool == threshold_bool if comp == "==" else value_bool != threshold_bool
        v = float(value)
        t = float(threshold)
        if comp == ">": return v > t
        if comp == ">=": return v >= t
        if comp == "<": return v < t
        if comp == "<=": return v <= t
        if comp == "==": return v == t
        if comp == "!=": return v != t
    except Exception:
        if comp == "==": return str(value) == str(threshold)
        if comp == "!=": return str(value) != str(threshold)
    return False


def applicable_rules(settings: pd.DataFrame, product: str, sector: str) -> pd.DataFrame:
    product_rules = settings[settings["Product"].astype(str) == product].copy()
    if product_rules.empty:
        return product_rules
    exact = product_rules[product_rules["GICS Sector"].astype(str) == sector]
    generic = product_rules[product_rules["GICS Sector"].astype(str).isin(["All", "all", "ALL", ""])].copy()
    if exact.empty:
        return generic
    # exact sector rules override generic rules with same KPI ID
    override_ids = set(exact["KPI ID"].astype(str))
    generic = generic[~generic["KPI ID"].astype(str).isin(override_ids)]
    return pd.concat([generic, exact], ignore_index=True)


def calculate_company_score(row: pd.Series, settings: pd.DataFrame, product: str) -> tuple[int, list, list]:
    sector = row.get("GICS Sector", "All")
    rules = applicable_rules(settings, product, sector)
    if rules.empty:
        return 0, [], []
    active = rules[rules["Active"].apply(normalize_bool)].copy()
    if active.empty:
        return 0, [], []
    triggered, missing = [], []
    total_weight = 0
    earned_weight = 0
    for _, rule in active.iterrows():
        weight = float(rule.get("Weight", 0) or 0)
        field = rule["Data Field"]
        ok = field in row.index and compare(row[field], rule["Comparator"], rule["Threshold"])
        total_weight += weight
        item = {
            "KPI": rule["KPI Name"],
            "Description": rule["Description"],
            "Weight": weight,
            "Field": field,
            "Value": row.get(field, None),
            "Threshold": rule["Threshold"],
            "Comparator": rule["Comparator"],
        }
        if ok:
            earned_weight += weight
            triggered.append(item)
        else:
            missing.append(item)
    score = round((earned_weight / total_weight) * 100) if total_weight else 0
    return score, triggered, missing


def get_opportunity_thresholds():
    system = st.session_state.get("system_settings", demo_system_settings()).copy()

    def get_value(setting_name, default):
        try:
            value = system.loc[system["Setting"] == setting_name, "Value"].iloc[0]
            return float(value)
        except Exception:
            return float(default)

    high = get_value("High Opportunity Threshold", 85)
    watch = get_value("Watch Threshold", 50)

    if watch >= high:
        watch = high - 1

    return high, watch


def classify_status(score: int) -> str:
    high, watch = get_opportunity_thresholds()
    if score >= high:
        return "High Opportunity"
    if score >= watch:
        return "Watch"
    return "Low Priority"


def score_dataframe(companies: pd.DataFrame, settings: pd.DataFrame, product: str) -> pd.DataFrame:
    rows = []
    for _, row in companies.iterrows():
        score, triggered, missing = calculate_company_score(row, settings, product)
        new = row.to_dict()
        new["Opportunity Score"] = score
        new["Triggered KPIs"] = len(triggered)
        new["Missing KPIs"] = len(missing)
        new["Status"] = classify_status(score)
        rows.append(new)
    return pd.DataFrame(rows).sort_values("Opportunity Score", ascending=False)


def score_badge(score: int) -> str:
    status = classify_status(score)
    klass = "score-high" if status == "High Opportunity" else "score-watch" if status == "Watch" else "score-low"
    return f'<span class="{klass}">{score}%</span>'


def ai_explanation(company, product, score, triggered, missing, question):
    triggered_names = [x["KPI"] for x in triggered]
    missing_names = [x["KPI"] for x in missing]

    key_drivers = ", ".join(triggered_names[:3]) if triggered_names else "limited triggered KPIs"
    key_caveats = ", ".join(missing_names[:3]) if missing_names else "no major missing KPI"

    if score >= 85:
        priority = "High priority"
        action = "Prepare banker outreach and review transaction feasibility."
        confidence = "High"
    elif score >= 50:
        priority = "Watch"
        action = "Maintain coverage, monitor the missing drivers and reassess timing."
        confidence = "Medium"
    else:
        priority = "Low priority"
        action = "No immediate action; keep the company in the monitoring universe."
        confidence = "Low"

    timing_note = ""
    if product == "PCM Fundraising":
        timing_missing = any("Funding timing" in x["KPI"] for x in missing)
        timing_triggered = any("Funding timing" in x["KPI"] for x in triggered)

        if timing_missing:
            timing_note = (
                " The key caveat is timing: the company appears to have raised capital recently, "
                "which reduces the short-term probability of another fundraising process."
            )
        elif timing_triggered:
            timing_note = (
                " Funding timing is supportive, suggesting enough time has passed since the last capital raise."
            )

    fallback = f"""
<b>Investment Summary</b><br>
{company} is classified as <b>{priority}</b> for <b>{product}</b> with an opportunity score of <b>{score}%</b>.<br><br>

<b>Key Positive Signals</b><br>
{key_drivers}.<br><br>

<b>Key Caveats</b><br>
{key_caveats}.{timing_note}<br><br>

<b>Recommended Banker Action</b><br>
{action}<br><br>

<b>Confidence</b><br>
{confidence} confidence based on the number and quality of triggered KPIs.
"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return fallback + "<br><br><span class='small-muted'>Demo mode: rule-based AI Banker explanation shown because no OPENAI_API_KEY is configured.</span>"

    try:
        client = OpenAI(api_key=api_key)
        prompt = f"""
You are an ECM/PCM/SES banker copilot for UniCredit.
Write a concise banker-style note using only the provided structured data.

Company: {company}
Product: {product}
Score: {score}%
Triggered KPIs: {triggered}
Missing KPIs: {missing}
User question: {question}

Return the answer in five short sections:
1. Investment Summary
2. Key Positive Signals
3. Key Caveats
4. Recommended Banker Action
5. Confidence

Do not invent external facts.
Mention timing caveats clearly if Funding Timing is missing.
Keep it concise.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        return fallback + f"<br><br><span class='small-muted'>Real AI mode failed, fallback response shown. Error: {e}</span>"


def to_excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=name[:31])
    return output.getvalue()


def read_uploaded_excel(uploaded, expected_sheet=None):
    if uploaded is None:
        return None
    try:
        return pd.read_excel(uploaded, sheet_name=expected_sheet or 0)
    except Exception as e:
        st.error(f"Could not read uploaded Excel file: {e}")
        return None

# ---------------------------
# Session state
# ---------------------------
if "companies" not in st.session_state:
    st.session_state.companies = demo_companies()
if "investors" not in st.session_state:
    st.session_state.investors = demo_investors()
if "settings" not in st.session_state:
    st.session_state.settings = demo_settings()
if "selected_company" not in st.session_state:
    st.session_state.selected_company = st.session_state.companies.iloc[0]["Company"]
if "system_settings" not in st.session_state:
    st.session_state.system_settings = demo_system_settings()

# ---------------------------
# Header
# ---------------------------
st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

st.image("unicredit_logo.png", width=170)

st.markdown(
    """
    <div style="
        font-size:18px;
        font-weight:600;
        color:#667085;
        margin-top:-8px;
        margin-bottom:18px;
    ">
        ECM Intelligence Platform · MVP
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="display:flex; justify-content:flex-end; margin-top:-70px; margin-bottom:40px;">
        <span class="uc-pill">Product → Sector → KPI → Score → AI</span>
    </div>
    """,
    unsafe_allow_html=True,
)
# ---------------------------
# Sidebar navigation
# ---------------------------
with st.sidebar:
    st.markdown("### UniCredit ECM")
    module = st.radio("Module", ["Dashboard", "ECM Cash", "PCM", "SES", "Settings / Thresholds", "Data Upload"], index=0)

    if module == "ECM Cash":
        product = st.radio("ECM Cash Product", ["ABB", "Rights Issue", "IPO"])
    elif module == "PCM":
        product = st.radio("PCM Product", ["PCM Fundraising", "Investor Matching"])
    elif module == "SES":
        product = st.radio("SES Product", ["SES SSL", "LTIP Tracker", "Derivatives Tracker"])
    else:
        product = "ABB"

    st.markdown("---")
    st.caption("Demo dataset is used unless Excel files are uploaded.")

companies = st.session_state.companies.copy()
investors_df = st.session_state.investors.copy()
settings_df = st.session_state.settings.copy()

# ---------------------------
# Dashboard
# ---------------------------
if module == "Dashboard":
    st.markdown('<div class="hero"><h1>ECM Opportunity Engine</h1><p>Enterprise-style MVP for product-specific KPI scoring, threshold configuration, Excel-based data upload and AI Banker explanations.</p></div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    dashboard_products = ["ABB", "Rights Issue", "IPO", "PCM Fundraising", "SES SSL"]
    for col, prod in zip([c1, c2, c3, c4, c5], dashboard_products):
        sdf = score_dataframe(companies, settings_df, prod)
        high_count = int((sdf["Status"] == "High Opportunity").sum())
        with col:
            st.markdown(f'<div class="metric-card"><small>{prod}</small><b>{high_count}</b><span>High-priority opportunities</span></div>', unsafe_allow_html=True)

    top_rows = []
    for prod in dashboard_products:
        sdf = score_dataframe(companies, settings_df, prod)
        if prod in ["IPO", "PCM Fundraising"]:
            sdf = sdf[sdf["Type"] == "Private"]
        elif prod in ["ABB", "Rights Issue", "SES SSL"]:
            sdf = sdf[sdf["Type"] == "Listed"]
        for _, r in sdf.head(3).iterrows():
            top_rows.append([prod, r["Company"], r["Country"], r["GICS Sector"], r["Opportunity Score"], r["Status"]])
    top_df = pd.DataFrame(top_rows, columns=["Product", "Company", "Country", "GICS Sector", "Opportunity Score", "Status"]).sort_values("Opportunity Score", ascending=False).head(12)
    st.write("")
    st.markdown(
    '''
    <div class="section-card" style="padding:12px 15px; margin-bottom:10px;">
        <h3 style="margin:0;">Top Opportunities Across Products</h3>
    ''',
    unsafe_allow_html=True,
)
    st.dataframe(top_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Product modules
# ---------------------------
elif module in ["ECM Cash", "PCM", "SES"]:
    st.markdown(f'<div class="hero"><h1>{product}</h1><p>Scores are calculated from editable KPI thresholds and representative dummy data / uploaded Excel data.</p></div>', unsafe_allow_html=True)

    if product == "LTIP Tracker":
        st.info("MVP demo using structured dummy disclosure fields. In production, this could be populated from remuneration reports, annual reports and company disclosures.")
        ltip_data = pd.DataFrame([
            ["Ferrari", "Italy", "Consumer Discretionary", "Yes", "Performance Shares", 180, 2027, "Physical", "High Opportunity"],
            ["Moncler", "Italy", "Consumer Discretionary", "Yes", "Restricted Shares", 75, 2026, "Physical", "Watch"],
            ["Stellantis", "Netherlands", "Consumer Discretionary", "Yes", "Options + Shares", 240, 2028, "Mixed", "High Opportunity"],
            ["Enel", "Italy", "Utilities", "Yes", "Performance Shares", 95, 2026, "Cash", "Watch"],
            ["Prysmian", "Italy", "Industrials", "No", "-", 0, "-", "-", "Low Priority"],
            ["Saipem", "Italy", "Energy", "Yes", "Share-Based Plan", 60, 2025, "Physical", "Watch"],
        ], columns=["Company", "Country", "GICS Sector", "LTIP Flag", "Plan Type", "Estimated Size EURm", "Expiry / Vesting Year", "Settlement", "Opportunity Status"])

        st.markdown('<div class="section-card"><h3>Long Term Incentive Plan Tracker</h3>', unsafe_allow_html=True)
        st.dataframe(ltip_data, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    if product == "Derivatives Tracker":
        st.info("MVP demo using structured dummy disclosure fields. In production, this could be populated from annual reports, financial notes and own-share derivative disclosures.")
        deriv_data = pd.DataFrame([
            ["Ferrari", "Italy", "No", "-", 0, "-", "-", "Low Priority"],
            ["Stellantis", "Netherlands", "Yes", "Equity Swap", 250, "BNP Paribas", 2026, "High Opportunity"],
            ["Telecom Italia", "Italy", "Yes", "Equity Collar", 120, "UniCredit", 2027, "Watch"],
            ["Enel", "Italy", "Yes", "Own-share Swap", 180, "Intesa Sanpaolo", 2026, "Watch"],
            ["Leonardo", "Italy", "No", "-", 0, "-", "-", "Low Priority"],
            ["Saipem", "Italy", "Yes", "Call Option Structure", 90, "JP Morgan", 2025, "Watch"],
        ], columns=["Company", "Country", "Own-share Derivative Flag", "Instrument Type", "Estimated Size EURm", "Bank / Counterparty", "Maturity", "Opportunity Status"])

        st.markdown('<div class="section-card"><h3>Own-Share Derivatives Tracker</h3>', unsafe_allow_html=True)
        st.dataframe(deriv_data, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    if product == "Investor Matching":
        st.markdown('<div class="section-card"><h3>Investor Matching Tool</h3>', unsafe_allow_html=True)

        private_companies = companies[companies["Type"] == "Private"]["Company"].tolist()
        target = st.selectbox("Target company", private_companies)
        target_row = companies[companies["Company"] == target].iloc[0]

        st.caption(
            f'Target: {target_row["Company"]} · {target_row["Country"]} · '
            f'{target_row["GICS Sector"]} · {target_row["Type"]}'
        )

        scored_investors = investors_df.copy()

        def investor_match_details(inv):
            score = 0
            reasons = []

            # Sector fit
            if str(target_row["GICS Sector"]) in str(inv["Preferred Sector"]) or "All" in str(inv["Preferred Sector"]):
                score += 30
                reasons.append("Sector fit")

            # Geography fit
            if str(target_row["Country"]) in str(inv["Geography"]) or "Europe" in str(inv["Geography"]):
                score += 20
                reasons.append("Geography fit")

            # Stage fit
            if target_row["Type"] == "Private" and ("Series" in str(inv["Stage"]) or "Growth" in str(inv["Strategy"])):
                score += 20
                reasons.append("Stage fit")

            # Ticket size fit
            last_raise = float(target_row.get("Last Raise Amount EURm", 0) or 0)
            ticket = float(inv.get("Average Ticket EURm", 0) or 0)
            if ticket >= last_raise * 0.25:
                score += 20
                reasons.append("Ticket size fit")

            # Strategy fit
            if target_row["Type"] == "Private" and any(x in str(inv["Strategy"]) for x in ["Growth", "Venture", "Private Equity"]):
                score += 10
                reasons.append("Strategy fit")

            return min(score, 100), ", ".join(reasons) if reasons else "Limited fit"

        scored_investors[["Match Score", "Why Matched"]] = scored_investors.apply(
            lambda r: pd.Series(investor_match_details(r)),
            axis=1
        )

        display_cols = [
            "Investor", "Strategy", "Preferred Sector", "Stage", "Geography",
            "Average Ticket EURm", "Match Score", "Why Matched"
        ]

        st.dataframe(
            scored_investors.sort_values("Match Score", ascending=False)[display_cols],
            use_container_width=True,
            hide_index=True
        )

        top_match = scored_investors.sort_values("Match Score", ascending=False).iloc[0]
        st.markdown(
            f'''
            <div class="ai-box">
            <b>Top investor rationale:</b><br>
            {top_match["Investor"]} is the strongest match for {target_row["Company"]} 
            with a match score of {int(top_match["Match Score"])}%. 
            Main reasons: {top_match["Why Matched"]}.
            </div>
            ''',
            unsafe_allow_html=True
        )

        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    product_df = companies.copy()
    if product in ["ABB", "Rights Issue", "SES SSL"]:
        product_df = product_df[product_df["Type"] == "Listed"]
    if product in ["IPO", "PCM Fundraising"]:
        product_df = product_df[product_df["Type"] == "Private"]

    scored = score_dataframe(product_df, settings_df, product)
    left, right = st.columns([2.2, 1])
    with left:
        st.markdown('<div class="section-card"><h3>Opportunity Radar</h3>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        country_filter = fc1.selectbox("Country", ["All"] + sorted(scored["Country"].dropna().unique().tolist()))
        sector_filter = fc2.selectbox("GICS Sector", ["All"] + sorted(scored["GICS Sector"].dropna().unique().tolist()))
        score_filter = fc3.selectbox("Score", ["All", "High Opportunity", "Watch", "Low Priority"])
        filtered = scored.copy()
        if country_filter != "All": filtered = filtered[filtered["Country"] == country_filter]
        if sector_filter != "All": filtered = filtered[filtered["GICS Sector"] == sector_filter]
        if score_filter != "All": filtered = filtered[filtered["Status"] == score_filter]
        display_cols = ["Company", "Ticker", "Country", "GICS Sector", "Opportunity Score", "Status", "Triggered KPIs", "Missing KPIs"]
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        selected = st.selectbox("Select company for detail panel", filtered["Company"].tolist() if not filtered.empty else scored["Company"].tolist())
        st.session_state.selected_company = selected

    with right:
        selected_row = companies[companies["Company"] == st.session_state.selected_company].iloc[0]
        score, triggered, missing = calculate_company_score(selected_row, settings_df, product)
        #st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader(selected_row["Company"])
        st.caption(f'{selected_row["Ticker"]} · {selected_row["Country"]} · {selected_row["GICS Sector"]}')
        st.markdown(f"### Opportunity Score: {score}%")
        st.progress(score / 100)

        st.markdown("**Score Breakdown**")

        earned = sum([float(x["Weight"]) for x in triggered])
        total = earned + sum([float(x["Weight"]) for x in missing])

        all_kpis = []
        for item in triggered:
            all_kpis.append((item, True))
        for item in missing:
            all_kpis.append((item, False))

        for item, is_triggered in all_kpis:
            icon = "✓" if is_triggered else "✕"
            klass = "kpi-ok" if is_triggered else "kpi-no"
            contribution = int(float(item["Weight"])) if is_triggered else 0

            st.markdown(
                f'''
                <div style="border:1px solid #E5E7EB; border-radius:8px; padding:8px 10px; margin-bottom:6px; background:#FFFFFF;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="{klass}">{icon} {item["KPI"]}</span>
                        <b>{contribution}</b>
                    </div>
                    <div class="small-muted">{item["Field"]}: {item["Value"]} vs {item["Comparator"]} {item["Threshold"]}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

        st.caption(f"Earned {int(earned)} / {int(total)} weighted points")
        
        st.markdown('</div>', unsafe_allow_html=True)


    st.markdown(
    '''
    <div class="section-card">
        <h3 style="margin-bottom:4px;">AI Banker Recommendation</h3>
        <p class="small-muted" style="margin-top:0;">
            AI-generated explanation based on configurable business rules.
        </p>
    ''',
    unsafe_allow_html=True,
)
    question = st.text_input("Ask AI", value="Why is this company flagged?")
    if st.button("Generate AI Banker Note", type="primary"):
        answer = ai_explanation(selected_row["Company"], product, score, triggered, missing, question)
        st.markdown(f'<div class="ai-box">{answer}</div>', unsafe_allow_html=True)
    else:
        preview = ai_explanation(selected_row["Company"], product, score, triggered, missing, question)
        st.markdown(f'<div class="ai-box">{preview}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Settings
# ---------------------------
elif module == "Settings / Thresholds":
    st.markdown('<div class="hero"><h1>Threshold Module</h1><p>Edit product-specific KPI rules, GICS-sector rules and opportunity classification thresholds.</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card"><h3>Opportunity Classification Settings</h3><p class="small-muted">Define how scores are classified as High Opportunity, Watch or Low Priority.</p>', unsafe_allow_html=True)

    current_high, current_watch = get_opportunity_thresholds()
    col_a, col_b = st.columns(2)
    with col_a:
        high_input = st.number_input("High Opportunity Threshold", min_value=0, max_value=100, value=int(current_high), step=1)
    with col_b:
        watch_input = st.number_input("Watch Threshold", min_value=0, max_value=100, value=int(current_watch), step=1)

    if st.button("Save Opportunity Classification Settings", type="primary"):
        if watch_input >= high_input:
            st.error("Watch Threshold must be lower than High Opportunity Threshold.")
        else:
            st.session_state.system_settings = pd.DataFrame([
                ["High Opportunity Threshold", high_input, "Minimum score required to classify a company as High Opportunity"],
                ["Watch Threshold", watch_input, "Minimum score required to classify a company as Watch"],
            ], columns=["Setting", "Value", "Description"])
            st.success("Opportunity classification thresholds saved. Dashboard and product scores will be recalculated.")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    selected_product = st.selectbox("Product", sorted(settings_df["Product"].unique().tolist()))
    selected_sector = st.selectbox("GICS Sector", ["All"] + sorted(companies["GICS Sector"].dropna().unique().tolist()))
    mask = (settings_df["Product"] == selected_product) & (settings_df["GICS Sector"].isin([selected_sector, "All"]))
    editable = settings_df[mask].copy().reset_index()
    editable["Threshold"] = editable["Threshold"].astype(str)
    editable["Weight"] = pd.to_numeric(editable["Weight"], errors="coerce").fillna(0)
    editable["Active"] = editable["Active"].apply(normalize_bool)

    st.markdown('<div class="section-card"><h3>Editable KPI Rules</h3>', unsafe_allow_html=True)
    edited = st.data_editor(
        editable[["index", "Product", "GICS Sector", "KPI ID", "KPI Name", "Data Field", "Comparator", "Threshold", "Weight", "Active", "Description"]],
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        disabled=["index"],
    )
    if st.button("Save Threshold Configuration", type="primary"):
        updated = settings_df.copy()
        for _, row in edited.iterrows():
            idx = row.get("index")
            if pd.notna(idx) and int(idx) in updated.index:
                for col in ["Product", "GICS Sector", "KPI ID", "KPI Name", "Data Field", "Comparator", "Threshold", "Weight", "Active", "Description"]:
                    updated.loc[int(idx), col] = row[col]
        st.session_state.settings = updated
        st.success("Settings saved. Scores will be recalculated using the updated thresholds.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Preview score impact
    st.markdown('<div class="section-card"><h3>Score Preview</h3>', unsafe_allow_html=True)
    preview_df = score_dataframe(companies, st.session_state.settings, selected_product)
    st.dataframe(preview_df[["Company", "Type", "GICS Sector", "Opportunity Score", "Status"]].head(10), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Data upload
# ---------------------------
elif module == "Data Upload":
    st.markdown('<div class="hero"><h1>Excel Data Upload</h1><p>Use demo data or upload Excel datasets for companies, investors and KPI settings.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card"><h3>Download Excel Templates</h3>', unsafe_allow_html=True)
    template_bytes = to_excel_bytes({"Companies": demo_companies(), "Investors": demo_investors(), "KPI_Settings": demo_settings()})
    st.download_button("Download full demo Excel workbook", template_bytes, file_name="unicredit_ecm_mvp_demo_data.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        comp_file = st.file_uploader("Upload companies.xlsx", type=["xlsx"], key="companies_upload")
    with col2:
        inv_file = st.file_uploader("Upload investors.xlsx", type=["xlsx"], key="investors_upload")
    with col3:
        set_file = st.file_uploader("Upload kpi_settings.xlsx", type=["xlsx"], key="settings_upload")

    if st.button("Apply uploaded files", type="primary"):
        cdf = read_uploaded_excel(comp_file)
        idf = read_uploaded_excel(inv_file)
        sdf = read_uploaded_excel(set_file)
        if cdf is not None:
            st.session_state.companies = cdf
            st.success(f"Companies loaded: {len(cdf)} rows")
        if idf is not None:
            st.session_state.investors = idf
            st.success(f"Investors loaded: {len(idf)} rows")
        if sdf is not None:
            st.session_state.settings = sdf
            st.success(f"KPI settings loaded: {len(sdf)} rows")

    st.markdown('<div class="section-card"><h3>Current Data Preview</h3>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Companies", "Investors", "KPI Settings"])
    with tab1:
        st.dataframe(st.session_state.companies, use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(st.session_state.investors, use_container_width=True, hide_index=True)
    with tab3:
        st.dataframe(st.session_state.settings, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
