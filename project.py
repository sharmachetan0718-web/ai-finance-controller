import pandas as pd
import random

from datetime import datetime, timedelta


# ============================================================
# AI FINANCE CONTROLLER
# DATA + RECONCILIATION ENGINE
# ============================================================


# ============================================================
# 1. GENERATE TRANSACTION DATA
# ============================================================

def generate_transactions(number_of_payments=120):

    random.seed(42)

    payments = []
    settlements = []

    start_date = datetime(2026, 8, 1)


    for i in range(
        1,
        number_of_payments + 1
    ):

        payment_id = f"P{i:04d}"

        merchant_id = (
            f"M{random.randint(1, 10):03d}"
        )

        amount = random.randint(
            500,
            10000
        )

        payment_date = (
            start_date
            + timedelta(
                days=random.randint(0, 20)
            )
        )


        payments.append({

            "payment_id":
                payment_id,

            "merchant_id":
                merchant_id,

            "amount":
                amount,

            "payment_date":
                payment_date.strftime(
                    "%Y-%m-%d"
                ),

            "status":
                "SUCCESS"
        })


        # 10% missing settlement
        if random.random() < 0.10:
            continue


        settlement_date = (
            payment_date
            + timedelta(
                days=random.randint(1, 3)
            )
        )


        # Processing fee
        fee = 0

        if random.random() < 0.35:

            fee = round(
                amount
                * random.uniform(
                    0.01,
                    0.03
                )
            )


        settled_amount = (
            amount - fee
        )


        settlements.append({

            "settlement_id":
                f"S{len(settlements) + 1:04d}",

            "payment_id":
                payment_id,

            "settled_amount":
                settled_amount,

            "fee":
                fee,

            "settlement_date":
                settlement_date.strftime(
                    "%Y-%m-%d"
                ),

            "settlement_status":
                "SETTLED"
        })


        # 5% duplicate settlement
        if random.random() < 0.05:

            settlements.append({

                "settlement_id":
                    f"S{len(settlements) + 1:04d}",

                "payment_id":
                    payment_id,

                "settled_amount":
                    settled_amount,

                "fee":
                    fee,

                "settlement_date":
                    settlement_date.strftime(
                        "%Y-%m-%d"
                    ),

                "settlement_status":
                    "SETTLED"
            })


    return (
        pd.DataFrame(payments),
        pd.DataFrame(settlements)
    )


# ============================================================
# 2. RECONCILIATION ENGINE
# ============================================================

def reconcile_transactions(
    payments,
    settlements
):

    settlement_summary = (

        settlements

        .groupby("payment_id")

        .agg(

            settlement_count=(
                "settlement_id",
                "count"
            ),

            settled_amount=(
                "settled_amount",
                "sum"
            ),

            total_fee=(
                "fee",
                "sum"
            ),

            settlement_date=(
                "settlement_date",
                "max"
            ),

            settlement_id=(
                "settlement_id",
                lambda x:
                    ", ".join(x)
            )
        )

        .reset_index()
    )


    reconciliation = payments.merge(

        settlement_summary,

        on="payment_id",

        how="left"
    )


    reconciliation[
        "settlement_count"
    ] = (

        reconciliation[
            "settlement_count"
        ]
        .fillna(0)
        .astype(int)
    )


    reconciliation[
        "duplicate_settlement"
    ] = (

        reconciliation[
            "settlement_count"
        ] > 1
    )


    reconciliation["difference"] = (

        reconciliation["amount"]

        - reconciliation["settled_amount"]
    )


    reconciliation["match_status"] = (

        reconciliation.apply(

            lambda row:

                "EXCEPTION"

                if (

                    pd.isna(
                        row["settlement_id"]
                    )

                    or
                    row[
                        "duplicate_settlement"
                    ]
                )

                else "MATCHED",

            axis=1
        )
    )


    return reconciliation


# ============================================================
# 3. EXCEPTION CLASSIFICATION
# ============================================================

def classify_exception(row):

    if row.get(
        "duplicate_settlement",
        False
    ):

        return "DUPLICATE SETTLEMENT"


    if pd.isna(
        row["settlement_id"]
    ):

        return "MISSING SETTLEMENT"


    if row["difference"] == 0:

        return "NO ISSUE"


    return "AMOUNT DIFFERENCE"


# ============================================================
# 4. CONFIDENCE SCORE
# ============================================================

def calculate_confidence(row):

    exception_type = (
        row["exception_type"]
    )


    if exception_type == (
        "MISSING SETTLEMENT"
    ):

        return 0


    if exception_type == (
        "DUPLICATE SETTLEMENT"
    ):

        return 20


    if exception_type == "NO ISSUE":

        return 100


    if exception_type == (
        "AMOUNT DIFFERENCE"
    ):

        difference = abs(
            row["difference"]
        )

        amount = row["amount"]


        if amount == 0:

            return 0


        percentage = (
            difference / amount
        ) * 100


        if percentage <= 1:

            return 95

        elif percentage <= 3:

            return 90

        elif percentage <= 5:

            return 80

        else:

            return 60


    return 0


# ============================================================
# 5. BUILD AI CONTEXT
# ============================================================

def build_ai_context(row):

    return {

        "payment_id":
            row["payment_id"],

        "merchant_id":
            row["merchant_id"],

        "payment_amount":
            int(row["amount"]),

        "settled_amount":

            None

            if pd.isna(
                row["settled_amount"]
            )

            else float(
                row["settled_amount"]
            ),

        "difference":

            None

            if pd.isna(
                row["difference"]
            )

            else float(
                row["difference"]
            ),

        "settlement_count":
            int(
                row["settlement_count"]
            ),

        "exception_type":
            row["exception_type"],

        "confidence_score":
            int(
                row["confidence_score"]
            ),

        "payment_date":
            row["payment_date"],

        "settlement_date":

            None

            if pd.isna(
                row["settlement_date"]
            )

            else row[
                "settlement_date"
            ]
    }