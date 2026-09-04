import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.graph_objects as go


from project import (
    generate_transactions,
    reconcile_transactions,
    classify_exception,
    calculate_confidence,
    build_ai_context
)


from ai_explainer import (
    explain_exception,
    explain_finance_summary
)


# ============================================================
# TABLE STYLING
# ============================================================
def style_dataframe(df):
    """Apply a professional light table theme with consistently visible text."""
    display_df = df.copy()
    display_df = display_df.fillna("—")
    return (
        display_df.style
        .set_properties(**{
            "color": "#18202a",
            "background-color": "#ffffff",
            "border-color": "#d9dee7",
            "font-size": "13px"
        })
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#eef2f7"),
                    ("color", "#18202a"),
                    ("font-weight", "600"),
                    ("border-color", "#d9dee7")
                ]
            },
            {
                "selector": "tbody tr:nth-child(even) td",
                "props": [("background-color", "#f8fafc")]
            },
            {
                "selector": "tbody tr:hover td",
                "props": [("background-color", "#eef4ff")]
            }
        ])
    )


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Finance Operations | Reconciliation",
    page_icon="▣",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #f5f6f8;
    color: #18202a;
}

.main .block-container {
    max-width: 1380px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Normal page text */
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    color: #18202a !important;
}

.stApp h1 {
    font-size: 2rem !important;
    font-weight: 650 !important;
}

.stApp h2 {
    font-size: 1.35rem !important;
    font-weight: 620 !important;
}

.stApp h3 {
    font-size: 1.08rem !important;
    font-weight: 600 !important;
}

.stApp p,
.stApp label,
.stApp [data-testid="stMarkdownContainer"] {
    color: #18202a !important;
}

.section-note {
    color: #5f6b78 !important;
    font-size: 0.88rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #dfe3e8;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #26313c !important;
}

/* Clickable workspace navigation */
.sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 3px;
    margin: 4px 0 8px 0;
}

.sidebar-nav a {
    display: block;
    padding: 9px 10px;
    border-radius: 6px;
    color: #667085 !important;
    text-decoration: none !important;
    font-size: 0.92rem;
    font-weight: 500;
    transition: background 0.15s ease, color 0.15s ease;
}

.sidebar-nav a:hover {
    background: #eef4ff;
    color: #1d4ed8 !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #dfe3e8;
    border-radius: 7px;
    padding: 13px 15px;
    min-height: 100px;
    box-shadow: none;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #18202a !important;
}

/* Buttons - professional blue, with stable focus/active states */
.stButton > button,
.stDownloadButton > button,
button[kind="secondary"],
button[kind="primary"] {
    background: #1f5fbf !important;
    color: #ffffff !important;
    border: 1px solid #1f5fbf !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transition: background 0.15s ease, border-color 0.15s ease !important;
}

.stButton > button p,
.stButton > button span,
.stButton > button div,
.stDownloadButton > button p,
.stDownloadButton > button span,
.stDownloadButton > button div,
button[kind="secondary"] p,
button[kind="secondary"] span,
button[kind="secondary"] div,
button[kind="primary"] p,
button[kind="primary"] span,
button[kind="primary"] div {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stButton > button:focus,
.stDownloadButton > button:focus,
.stButton > button:active,
.stDownloadButton > button:active {
    background: #174a93 !important;
    border-color: #174a93 !important;
    color: #ffffff !important;
}

.stButton > button[kind="primary"],
button[kind="primary"] {
    background: #c43d35 !important;
    border-color: #c43d35 !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[kind="primary"]:focus,
.stButton > button[kind="primary"]:active,
button[kind="primary"]:hover,
button[kind="primary"]:focus,
button[kind="primary"]:active {
    background: #a92f29 !important;
    border-color: #a92f29 !important;
}

/* New transaction expander - never turns into a black bar when opened */
[data-testid="stExpander"] details summary {
    background: #eef2f7 !important;
    color: #18202a !important;
    border: 1px solid #d9dee7 !important;
    border-radius: 7px !important;
}

[data-testid="stExpander"] details summary:hover,
[data-testid="stExpander"] details[open] summary {
    background: #e7eef8 !important;
    color: #18202a !important;
}

[data-testid="stExpander"] details summary *,
[data-testid="stExpander"] details summary p,
[data-testid="stExpander"] details summary span {
    color: #18202a !important;
    -webkit-text-fill-color: #18202a !important;
}

/* Select boxes */
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border-radius: 6px !important;
}

div[data-baseweb="select"] * {
    color: #18202a !important;
}

/* Text inputs */
div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #18202a !important;
    border-radius: 6px !important;
}

/* Tables - always use a clean professional light theme */
[data-testid="stDataFrame"] {
    border: 1px solid #dfe3e8 !important;
    border-radius: 7px !important;
    overflow: hidden !important;
    background: #ffffff !important;
}

[data-testid="stDataFrame"] iframe {
    background: #ffffff !important;
}

/* Add Transaction form - keep every control white and readable */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: #ffffff !important;
    border: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] details,
[data-testid="stSidebar"] [data-testid="stExpander"] details > div {
    background: #ffffff !important;
}

[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    background: #ffffff !important;
    color: #18202a !important;
    -webkit-text-fill-color: #18202a !important;
    border: 1px solid #aeb7c4 !important;
    border-radius: 7px !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {
    color: #9aa4b2 !important;
    -webkit-text-fill-color: #9aa4b2 !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
    background: #ffffff !important;
    color: #18202a !important;
    border: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stNumberInput"] button:hover {
    background: #f3f5f8 !important;
    color: #18202a !important;
}

/* Streamlit form submit button: stable blue in normal, hover, focus and active states */
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] button[kind] {
    background: #1f5fbf !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid #1f5fbf !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stFormSubmitButton"] button:focus,
[data-testid="stFormSubmitButton"] button:active,
[data-testid="stFormSubmitButton"] button:focus-visible {
    background: #174a93 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border-color: #174a93 !important;
}

[data-testid="stFormSubmitButton"] button p,
[data-testid="stFormSubmitButton"] button span,
[data-testid="stFormSubmitButton"] button div {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 6px !important;
}

[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
    color: inherit !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "payments" not in st.session_state:

    st.session_state.payments = None


if "settlements" not in st.session_state:

    st.session_state.settlements = None


if "audit_log" not in st.session_state:

    st.session_state.audit_log = []

if "custom_payments" not in st.session_state:
    st.session_state.custom_payments = []

if "custom_settlements" not in st.session_state:
    st.session_state.custom_settlements = []


# ============================================================
# GENERATE DATA
# ============================================================

if (

    st.session_state.payments is None

    or

    st.session_state.settlements is None

):

    (

        st.session_state.payments,

        st.session_state.settlements

    ) = generate_transactions(120)


payments = st.session_state.payments.copy()

settlements = st.session_state.settlements.copy()

# Merge transactions entered from the dashboard.
if st.session_state.custom_payments:
    payments = pd.concat(
        [payments, pd.DataFrame(st.session_state.custom_payments)],
        ignore_index=True
    )

if st.session_state.custom_settlements:
    settlements = pd.concat(
        [settlements, pd.DataFrame(st.session_state.custom_settlements)],
        ignore_index=True
    )


# ============================================================
# OPERATIONS CONTEXT
# ============================================================

with st.sidebar:
    st.markdown("### Finance Operations")
    st.caption("Payment matching & exception review")
    st.divider()
    st.markdown("**Workspace**")

    # Clickable in-page navigation. These links jump to the matching
    # section without changing the existing dashboard logic.
    st.markdown("""
    <div class="sidebar-nav">
        <a href="#finance-overview">Overview</a>
        <a href="#exception-queue">Exception queue</a>
        <a href="#transaction-review">Transaction review</a>
        <a href="#activity-log">Activity log</a>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Use **Add transaction** below to test a new payment.")

    st.divider()
    st.markdown("**Add transaction**")

    with st.expander("➕ New transaction", expanded=False):
        with st.form("add_transaction_form", clear_on_submit=True):
            new_payment_id = st.text_input(
                "Payment ID",
                placeholder="PAY-1001"
            )
            new_merchant_id = st.text_input(
                "Merchant ID",
                placeholder="MER-1001"
            )
            new_amount = st.number_input(
                "Payment Amount (₹)",
                min_value=0.0,
                value=5000.0,
                step=100.0
            )
            new_settled_amount = st.number_input(
                "Settled Amount (₹)",
                min_value=0.0,
                value=5000.0,
                step=100.0
            )
            new_settlement_count = st.number_input(
                "Settlement Count",
                min_value=0,
                value=1,
                step=1
            )

            add_transaction = st.form_submit_button(
                "Add Transaction",
                use_container_width=True
            )

            if add_transaction:
                payment_id = new_payment_id.strip()
                merchant_id = new_merchant_id.strip()

                if not payment_id or not merchant_id:
                    st.error("Payment ID and Merchant ID are required.")
                elif payment_id in payments["payment_id"].astype(str).tolist():
                    st.error("That Payment ID already exists.")
                else:
                    today = datetime.now().strftime("%Y-%m-%d")

                    new_payment = {
                        "payment_id": payment_id,
                        "merchant_id": merchant_id,
                        "amount": float(new_amount),
                        "payment_date": today,
                        "status": "SUCCESS"
                    }

                    # The reconciliation engine expects the same settlement
                    # columns as the generated dataset. Keep every field
                    # populated so its settlement_id join/aggregation works.
                    if int(new_settlement_count) > 0:
                        for i in range(int(new_settlement_count)):
                            st.session_state.custom_settlements.append({
                                "settlement_id": f"SC{len(st.session_state.custom_settlements) + 1:04d}",
                                "payment_id": payment_id,
                                "settled_amount": float(new_settled_amount),
                                "fee": 0.0,
                                "settlement_date": today,
                                "settlement_status": "SETTLED"
                            })
                    else:
                        st.session_state.custom_settlements = [
                            s for s in st.session_state.custom_settlements
                            if str(s["payment_id"]) != payment_id
                        ]

                    st.session_state.custom_payments.append(new_payment)
                    st.session_state.audit_log.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "TRANSACTION ADDED",
                        "payment_id": payment_id,
                        "severity": "INFO",
                        "action": "Transaction added through dashboard input."
                    })

                    st.success(f"{payment_id} added successfully.")
                    st.rerun()

    st.divider()
    st.markdown("**System status**")
    st.success("Reconciliation ready")
    st.caption("Data: current session")
    st.caption(f"Last refreshed: {datetime.now().strftime('%d %b %Y, %H:%M')}")

# ============================================================
# HEADER
# ============================================================

st.title("Finance Operations")

st.subheader("Reconciliation Control Center")

st.write("Match payments with settlements, review exceptions, and check transactions that need attention.")


# ============================================================
# REGENERATE
# ============================================================

if st.button(
    "Refresh transactions"
):

    (

        st.session_state.payments,

        st.session_state.settlements

    ) = generate_transactions(120)

    st.session_state.audit_log = []
    st.session_state.custom_payments = []
    st.session_state.custom_settlements = []

    st.rerun()


# ============================================================
# RECONCILIATION
# ============================================================

reconciliation = reconcile_transactions(

    payments,

    settlements

)


reconciliation["exception_type"] = (

    reconciliation.apply(

        classify_exception,

        axis=1

    )
)

# Any classified issue is an exception. This ensures that
# amount-difference transactions also appear in the Exception Queue.
reconciliation["match_status"] = reconciliation["exception_type"].apply(
    lambda value: "MATCHED" if value == "NO ISSUE" else "EXCEPTION"
)


reconciliation["confidence_score"] = (

    reconciliation.apply(

        calculate_confidence,

        axis=1

    )
)


# ============================================================
# PRIORITY
# ============================================================

def calculate_priority(row):

    exception = str(
        row["exception_type"]
    ).upper()


    if exception == "MISSING SETTLEMENT":

        return "HIGH"


    if exception == "DUPLICATE SETTLEMENT":

        return "HIGH"


    if exception == "AMOUNT DIFFERENCE":

        difference = row["difference"]


        if pd.notna(difference):

            if abs(
                float(difference)
            ) >= 1000:

                return "HIGH"


            return "MEDIUM"


        return "MEDIUM"


    return "LOW"


reconciliation["priority"] = (

    reconciliation.apply(

        calculate_priority,

        axis=1

    )
)


# ============================================================
# METRICS
# ============================================================

total_payments = len(payments)


matched = (

    reconciliation["match_status"]

    == "MATCHED"

).sum()


exception_count = (

    reconciliation["match_status"]

    == "EXCEPTION"

).sum()


match_rate = (

    matched / total_payments * 100

    if total_payments

    else 0

)


missing = (

    reconciliation["exception_type"]

    == "MISSING SETTLEMENT"

).sum()


duplicates = (

    reconciliation["exception_type"]

    == "DUPLICATE SETTLEMENT"

).sum()


amount_differences = (

    reconciliation["exception_type"]

    == "AMOUNT DIFFERENCE"

).sum()


high_risk = (

    reconciliation["priority"]

    == "HIGH"

).sum()


medium_risk = (

    reconciliation["priority"]

    == "MEDIUM"

).sum()


low_risk = (

    reconciliation["priority"]

    == "LOW"

).sum()


# ============================================================
st.markdown('<div id="finance-overview"></div>', unsafe_allow_html=True)

# FINANCE OVERVIEW
# ============================================================

st.markdown(
    "## Finance Overview"
)
st.markdown('<div class="section-note">A quick view of the current reconciliation run.</div>', unsafe_allow_html=True)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Payments",
        total_payments
    )


with col2:

    st.metric(
        "Matched",
        matched
    )


with col3:

    st.metric(
        "Exceptions",
        exception_count
    )


with col4:

    st.metric(
        "Match Rate",
        f"{match_rate:.2f}%"
    )


st.progress(

    min(
        max(
            match_rate / 100,
            0
        ),
        1
    ),

    text=(
        f"Reconciliation Match Rate: "
        f"{match_rate:.2f}%"
    )
)


# ============================================================
# EXCEPTION BREAKDOWN
# ============================================================

st.markdown(
    "## Exception Breakdown"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Missing Settlements",
        missing
    )


with col2:

    st.metric(
        "Duplicate Settlements",
        duplicates
    )


with col3:

    st.metric(
        "Amount Differences",
        amount_differences
    )


# ============================================================
# RISK DASHBOARD
# ============================================================

st.markdown(
    "## Risk & Priority"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "High priority",
        high_risk
    )


with col2:

    st.metric(
        "Medium priority",
        medium_risk
    )


with col3:

    st.metric(
        "Low priority",
        low_risk
    )


with col4:

    st.metric(
        "Total exceptions",
        exception_count
    )


st.caption("Priority guide: LOW = monitor  |  MEDIUM = review  |  HIGH = act first  |  CRITICAL = urgent")


# ============================================================
st.markdown('<div id="exception-queue"></div>', unsafe_allow_html=True)

# EXCEPTIONS
# ============================================================

exceptions_df = reconciliation[

    reconciliation["match_status"]
    == "EXCEPTION"

].copy()


st.markdown(
    "## Exception Queue"
)
st.markdown('<div class="section-note">Review unmatched or inconsistent transactions before taking action.</div>', unsafe_allow_html=True)


if len(exceptions_df) == 0:

    st.success(
        "No exceptions in this run."
    )

else:

    priority_order = {

        "HIGH": 0,

        "MEDIUM": 1,

        "LOW": 2

    }


    exceptions_df[
        "priority_order"
    ] = (

        exceptions_df[
            "priority"
        ].map(priority_order)

    )


    exceptions_df = (
        exceptions_df
        .sort_values(
            "priority_order"
        )
    )


    # ========================================================
    # FILTERS
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        selected_priority = st.selectbox(

            "Priority",

            [
                "ALL",
                "HIGH",
                "MEDIUM",
                "LOW"
            ]

        )


    with col2:

        exception_options = [

            "ALL"

        ] + sorted(

            exceptions_df[
                "exception_type"
            ]
            .dropna()
            .unique()
            .tolist()

        )


        selected_exception = st.selectbox(

            "Exception Type",

            exception_options

        )


    filtered_df = (
        exceptions_df.copy()
    )


    if selected_priority != "ALL":

        filtered_df = filtered_df[

            filtered_df["priority"]

            == selected_priority

        ]


    if selected_exception != "ALL":

        filtered_df = filtered_df[

            filtered_df[
                "exception_type"
            ]

            == selected_exception

        ]


    st.caption(

        f"Showing {len(filtered_df)} "
        f"of {len(exceptions_df)} exceptions"

    )


    display_columns = [

        "payment_id",

        "merchant_id",

        "amount",

        "settled_amount",

        "difference",

        "exception_type",

        "priority",

        "confidence_score"

    ]


    st.dataframe(

        style_dataframe(
            filtered_df[
                display_columns
            ]
        ),

        use_container_width=True,

        hide_index=True

    )


    # ========================================================
    # EXCEPTION ANALYTICS + TOP RISKS
    # ========================================================

    st.markdown("### Exception Analytics")

    analytics_col1, analytics_col2 = st.columns(2)

    # --------------------------------------------------------
    # EXCEPTIONS BY TYPE
    # --------------------------------------------------------
    with analytics_col1:
        type_counts = (
            exceptions_df["exception_type"]
            .value_counts()
            .reindex([
                "MISSING SETTLEMENT",
                "DUPLICATE SETTLEMENT",
                "AMOUNT DIFFERENCE"
            ])
            .fillna(0)
            .astype(int)
        )

        fig_exception = go.Figure(
            go.Bar(
                x=["DUPLICATE", "MISSING", "AMOUNT"],
                y=[
                    int(type_counts["DUPLICATE SETTLEMENT"]),
                    int(type_counts["MISSING SETTLEMENT"]),
                    int(type_counts["AMOUNT DIFFERENCE"])
                ],
                text=[
                    int(type_counts["DUPLICATE SETTLEMENT"]),
                    int(type_counts["MISSING SETTLEMENT"]),
                    int(type_counts["AMOUNT DIFFERENCE"])
                ],
                textposition="outside",
                marker=dict(
                    color=["#2F6FED", "#18A873", "#9AA4B2"]
                ),
                width=0.68
            )
        )

        fig_exception.update_layout(
            height=300,
            margin=dict(l=45, r=20, t=15, b=55),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font=dict(color="#18202a", size=11),
            xaxis=dict(
                title=None,
                tickfont=dict(color="#18202a", size=11),
                showgrid=False,
                zeroline=False,
                showline=True,
                linecolor="#9aa4b2",
                linewidth=1,
                fixedrange=True
            ),
            yaxis=dict(
                title="Number of Exceptions",
                title_font=dict(color="#18202a", size=11),
                tickfont=dict(color="#18202a", size=10),
                showgrid=True,
                gridcolor="#e5e7eb",
                dtick=10,
                range=[0, 50],
                fixedrange=True
            ),
            showlegend=False,
            bargap=0.22
        )

        st.caption("By exception type")
        st.plotly_chart(
            fig_exception,
            width="stretch",
            config={"displayModeBar": False}
        )

    # --------------------------------------------------------
    # EXCEPTIONS BY PRIORITY
    # --------------------------------------------------------
    with analytics_col2:
        priority_counts = (
            exceptions_df["priority"]
            .value_counts()
            .reindex(["HIGH", "MEDIUM", "LOW"])
            .fillna(0)
            .astype(int)
        )

        fig_priority = go.Figure(
            go.Bar(
                x=["HIGH", "MEDIUM", "LOW"],
                y=[
                    int(priority_counts["HIGH"]),
                    int(priority_counts["MEDIUM"]),
                    int(priority_counts["LOW"])
                ],
                text=[
                    int(priority_counts["HIGH"]),
                    int(priority_counts["MEDIUM"]),
                    int(priority_counts["LOW"])
                ],
                textposition="outside",
                marker=dict(
                    color=["#E5484D", "#F59E0B", "#9AA4B2"]
                ),
                width=0.68
            )
        )

        fig_priority.update_layout(
            height=300,
            margin=dict(l=45, r=20, t=15, b=55),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font=dict(color="#18202a", size=11),
            xaxis=dict(
                title=None,
                tickfont=dict(color="#18202a", size=11),
                showgrid=False,
                zeroline=False,
                showline=True,
                linecolor="#9aa4b2",
                linewidth=1,
                fixedrange=True
            ),
            yaxis=dict(
                title="Number of Exceptions",
                title_font=dict(color="#18202a", size=11),
                tickfont=dict(color="#18202a", size=10),
                showgrid=True,
                gridcolor="#e5e7eb",
                dtick=10,
                range=[0, 50],
                fixedrange=True
            ),
            showlegend=False,
            bargap=0.22
        )

        st.caption("By priority")
        st.plotly_chart(
            fig_priority,
            width="stretch",
            config={"displayModeBar": False}
        )


    st.markdown("### Top-Risk Transactions")

    top_risk_df = exceptions_df[
        [
            "payment_id",
            "merchant_id",
            "amount",
            "exception_type",
            "priority",
            "confidence_score"
        ]
    ].copy()

    priority_rank = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2
    }

    top_risk_df["_priority_rank"] = top_risk_df[
        "priority"
    ].map(priority_rank).fillna(3)

    top_risk_df = (
        top_risk_df
        .sort_values(
            ["_priority_rank", "confidence_score"],
            ascending=[True, False]
        )
        .drop(columns=["_priority_rank"])
        .head(5)
    )

    st.dataframe(
        style_dataframe(top_risk_df),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# EXPORT REPORTS
# ============================================================

st.markdown(
    "## Reports & Exports"
)


col1, col2 = st.columns(2)


with col1:

    full_csv = reconciliation.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(

        "Download reconciliation CSV",

        data=full_csv,

        file_name="reconciliation_report.csv",

        mime="text/csv"

    )


with col2:

    exception_csv = exceptions_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(

        "Download exception report",

        data=exception_csv,

        file_name="exception_report.csv",

        mime="text/csv"

    )


# ============================================================
# AI FINANCE SUMMARY
# ============================================================

st.markdown(
    "## Finance Risk Summary"
)


st.write(
    "Ask the AI analyst to review the complete "
    "reconciliation situation and identify the "
    "most important finance-operations risk."
)


if st.button(

    "Review overall risk",

    type="primary"

):

    with st.spinner(
        "Reviewing the current run..."
    ):

        try:

            amount_at_risk = (

                pd.to_numeric(

                    exceptions_df["amount"],

                    errors="coerce"

                )
                .fillna(0)
                .sum()

            )


            summary_context = {

                "total_payments":
                    int(total_payments),

                "matched_payments":
                    int(matched),

                "exceptions":
                    int(exception_count),

                "match_rate":
                    round(
                        float(match_rate),
                        2
                    ),

                "missing_settlements":
                    int(missing),

                "duplicate_settlements":
                    int(duplicates),

                "amount_differences":
                    int(amount_differences),

                "high_priority":
                    int(high_risk),

                "medium_priority":
                    int(medium_risk),

                "low_priority":
                    int(low_risk),

                "amount_at_risk":
                    round(
                        float(amount_at_risk),
                        2
                    )

            }


            ai_input = (

                "Analyze this finance "
                "reconciliation summary.\n\n"

                + json.dumps(
                    summary_context,
                    indent=2
                )

            )


            result = explain_finance_summary(
                ai_input
            )


            if not isinstance(
                result,
                dict
            ):

                st.error(
                    "The investigation returned an unexpected response. Please retry."
                )

                st.stop()


            severity = str(

                result.get(
                    "severity",
                    "UNKNOWN"
                )

            ).upper()


            st.markdown(
                "### Risk Assessment"
            )


            if severity == "CRITICAL":

                st.error(
                    f"Overall severity: {severity}"
                )

            elif severity == "HIGH":

                st.warning(
                    f"Overall severity: {severity}"
                )

            elif severity == "MEDIUM":

                st.info(
                    f"Overall severity: {severity}"
                )

            elif severity == "LOW":

                st.success(
                    f"Overall severity: {severity}"
                )

            else:

                st.info(
                    f"Overall severity: {severity}"
                )


            st.markdown(
                "**Current finding**"
            )


            explanation = result.get(

                "explanation",

                "No explanation returned."

            )


            st.write(
                explanation
            )


            st.markdown(
                "**Recommended next step**"
            )


            action = result.get(

                "recommended_action",

                "Manual review required."

            )


            st.write(
                action
            )


            # Audit
            st.session_state.audit_log.append({

                "timestamp":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "type":
                    "BATCH AI SUMMARY",

                "payment_id":
                    "ALL",

                "severity":
                    severity,

                "action":
                    action

            })


        except Exception as error:

            st.error(
                f"Risk summary failed: {error}"
            )


# ============================================================
st.markdown('<div id="transaction-review"></div>', unsafe_allow_html=True)

# INDIVIDUAL AI INVESTIGATION
# ============================================================

if len(exceptions_df) > 0:

    st.markdown(
        "## Transaction Investigation"
    )


    transaction_options = reconciliation["payment_id"].tolist()

    selected_payment = st.selectbox(
        "Transaction",
        transaction_options,
        key="individual_transaction_selector"
        )

    selected = reconciliation[

        reconciliation["payment_id"].astype(str)
          == str(selected_payment)
                 ].iloc[0]


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.write("**Payment ID**")

        st.write(
            selected["payment_id"]
        )


    with col2:

        st.write("**Merchant**")

        st.write(
            selected["merchant_id"]
        )


    with col3:

        st.write("**Payment Amount**")

        st.write(

            f"₹{selected['amount']:,.2f}"

        )


    with col4:

        st.write("**Exception**")

        st.write(
            selected["exception_type"]
        )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.write(
            "**Settlement Amount**"
        )


        if pd.notna(
            selected["settled_amount"]
        ):

            st.write(

                f"₹{selected['settled_amount']:,.2f}"

            )

        else:

            st.write(
                "No settlement"
            )


    with col2:

        st.write(
            "**Difference**"
        )


        if pd.notna(
            selected["difference"]
        ):

            st.write(

                f"₹{abs(selected['difference']):,.2f}"

            )

        else:

            st.write(
                "N/A"
            )


    with col3:

        st.write(
            "**Priority**"
        )

        st.write(
            selected["priority"]
        )


    if st.button(

        "Analyze transaction",

        type="primary"

    ):

        with st.spinner(
            "Analyzing transaction..."
        ):

            try:

                context = build_ai_context(
                    selected
                )


                result = explain_exception(
                    context
                )


                if not isinstance(
                    result,
                    dict
                ):

                    st.error(
                        "The investigation returned an unexpected response. Please retry."
                    )

                    st.stop()


                severity = str(

                    result.get(
                        "severity",
                        "UNKNOWN"
                    )

                ).upper()


                st.markdown(
                    "### Investigation Result"
                )


                # ------------------------------------------------
                # RISK SCORE + COLOR LEGEND
                # ------------------------------------------------

                risk_scores = {
                    "LOW": 25,
                    "MEDIUM": 50,
                    "HIGH": 75,
                    "CRITICAL": 95
                }

                risk_score = risk_scores.get(
                    severity,
                    0
                )

                risk_labels = {
                    "LOW": "LOW RISK",
                    "MEDIUM": "MEDIUM RISK",
                    "HIGH": "HIGH RISK",
                    "CRITICAL": "CRITICAL RISK",
                    "UNKNOWN": "UNKNOWN RISK"
                }

                st.metric(
                    "Risk Score",
                    f"{risk_score}/100"
                )

                st.progress(
                    risk_score / 100,
                    text=risk_labels.get(
                        severity,
                        "UNKNOWN RISK"
                    )
                )

                st.caption("Priority guide: LOW = monitor  |  MEDIUM = review  |  HIGH = act first  |  CRITICAL = urgent")


                # ------------------------------------------------
                # CONFIDENCE + HUMAN REVIEW
                # ------------------------------------------------

                transaction_confidence = pd.to_numeric(
                    selected.get(
                        "confidence_score",
                        0
                    ),
                    errors="coerce"
                )

                if pd.isna(transaction_confidence):
                    transaction_confidence = 0

                transaction_confidence = float(
                    transaction_confidence
                )

                review_required = (
                    transaction_confidence < 80
                    or severity in [
                        "HIGH",
                        "CRITICAL",
                        "UNKNOWN"
                    ]
                )

                confidence_col, review_col = st.columns(2)

                with confidence_col:
                    st.metric(
                        "Reconciliation Confidence",
                        f"{transaction_confidence:.0f}%"
                    )

                with review_col:
                    if review_required:
                        st.warning(
                            "Human review recommended"
                        )
                    else:
                        st.success(
                            "No additional review indicated"
                        )


                # ------------------------------------------------
                # TRANSACTION SNAPSHOT
                # ------------------------------------------------

                st.markdown(
                    "#### Transaction Snapshot"
                )

                snap1, snap2, snap3, snap4 = st.columns(4)

                with snap1:
                    st.metric(
                        "Payment",
                        str(selected["payment_id"])
                    )

                with snap2:
                    st.metric(
                        "Merchant",
                        str(selected["merchant_id"])
                    )

                with snap3:
                    st.metric(
                        "Amount",
                        f"₹{selected['amount']:,.2f}"
                    )

                with snap4:
                    st.metric(
                        "Exception",
                        str(selected["exception_type"])
                    )


                # ------------------------------------------------
                # EXPLANATION
                # ------------------------------------------------

                explanation = result.get(
                    "explanation",
                    "No explanation returned."
                )

                st.markdown("#### What Happened")
                st.info(explanation)


                # ------------------------------------------------
                # FINANCIAL IMPACT + ACTION
                # ------------------------------------------------

                financial_impact = result.get(
                    "financial_impact",
                    "Financial impact could not be determined."
                )

                action = result.get(
                    "recommended_action",
                    "Manual review required."
                )

                impact_col, action_col = st.columns(2)

                with impact_col:
                    st.markdown("#### Financial Impact")
                    st.warning(financial_impact)

                with action_col:
                    st.markdown("#### Recommended Action")
                    st.success(action)


                # ------------------------------------------------
                # PREVENTION
                # ------------------------------------------------

                prevention = result.get(
                    "prevention",
                    "No prevention recommendation returned."
                )

                st.markdown(
                    "#### Prevention Recommendation"
                )
                st.info(prevention)


                # ------------------------------------------------
                # DOWNLOAD INVESTIGATION REPORT
                # ------------------------------------------------

                report_data = {
                    "timestamp": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "payment_id": selected["payment_id"],
                    "merchant_id": selected["merchant_id"],
                    "payment_amount": selected["amount"],
                    "settled_amount": selected["settled_amount"],
                    "difference": selected["difference"],
                    "exception_type": selected["exception_type"],
                    "priority": selected["priority"],
                    "confidence_score": transaction_confidence,
                    "ai_risk_score": risk_score,
                    "severity": severity,
                    "explanation": explanation,
                    "financial_impact": financial_impact,
                    "recommended_action": action,
                    "prevention": prevention,
                    "human_review": (
                        "RECOMMENDED"
                        if review_required
                        else "NOT REQUIRED"
                    )
                }

                report_csv = pd.DataFrame(
                    [report_data]
                ).to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    "Download investigation report",
                    data=report_csv,
                    file_name=(
                        f"AI_investigation_"
                        f"{selected['payment_id']}.csv"
                    ),
                    mime="text/csv",
                    key=(
                        f"download_investigation_"
                        f"{selected['payment_id']}"
                    )
                )


                st.session_state.audit_log.append({

                    "timestamp":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "type":
                        "TRANSACTION AI ANALYSIS",

                    "payment_id":
                        selected["payment_id"],

                    "severity":
                        severity,

                    "action":
                        action

                })


            except Exception as error:

                st.error(
                    f"Transaction investigation failed: {error}"
                )


# ============================================================
st.markdown('<div id="activity-log"></div>', unsafe_allow_html=True)

# AUDIT TRAIL
# ============================================================

st.markdown("---")

st.markdown(
    "## AI Audit Trail"
)


if len(
    st.session_state.audit_log
) == 0:

    st.info(
        "No investigations have been recorded in this session."
    )

else:

    audit_df = pd.DataFrame(

        st.session_state.audit_log

    )


    st.dataframe(

        style_dataframe(audit_df),

        use_container_width=True,

        hide_index=True

    )


    audit_csv = audit_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(

        "Download Audit Trail",

        data=audit_csv,

        file_name="ai_audit_trail.csv",

        mime="text/csv"

    )


# ============================================================
# RAW DATA
# ============================================================

st.markdown("---")


with st.expander(
    "View payment data"
):

    st.dataframe(

        style_dataframe(payments),

        use_container_width=True,

        hide_index=True

    )


with st.expander(
    "View settlement data"
):

    st.dataframe(

        style_dataframe(settlements),

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(

    "Finance Operations | "
    "Payment reconciliation | "
    "Exception review | "
    "Transaction analysis & activity"

)