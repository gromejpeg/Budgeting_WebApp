import streamlit as st
import pandas as pd
import requests
import ynab
import json
import os

# ── YNAB Access Token ─────────────────────────────────────────────────────────
ACCESS_TOKEN = st.secrets["YNAB_ACCESS_TOKEN"]
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# Sanity‑check the token
response = requests.get("https://api.ynab.com/v1/budgets", headers=headers)
print("Status Code:", response.status_code)
print("Response:", response.json())

# ── Local JSON store for manual budget planning only ─────────────────────────
if not os.path.exists("budget_tracker.json"):
    with open("budget_tracker.json", "w") as f:
        json.dump({"income": [], "expenses": []}, f, indent=2)

# ── Streamlit page config ─────────────────────────────────────────────────────
st.set_page_config(page_title="Personal Budget Dashboard", layout="wide")

# ── Connect to YNAB API and pull base data─────────────────────────
configuration = ynab.Configuration(access_token=ACCESS_TOKEN)
with ynab.ApiClient(configuration) as client:
    budgets_api = ynab.BudgetsApi(client)
    budgets_resp = budgets_api.get_budgets()
    budgets = budgets_resp.data.budgets

# Use the first budget returned
    budget_id = budgets[0].id if budgets else None

    accounts_api = ynab.AccountsApi(client)
    transactions_api = ynab.TransactionsApi(client)

    accounts = (
        accounts_api.get_accounts(budget_id).data.accounts if budget_id else []
    )
    transactions = (
        transactions_api.get_transactions(budget_id).data.transactions
        if budget_id
        else []
    )

# Helper map: account‑id → account‑name
account_map = {acc.id: acc.name for acc in accounts}

# ── Sidebar navigation ────────────────────────────
st.sidebar.title("Overview")
page = st.sidebar.radio(
    "Go to",
    (
        "Dashboard",
        "Transactions & Spending",  # combined view
        "Budgeting Plan",
    ),
    index=0,
)

# ── Dashboard (overview) ───────────────────────────────
if page == "Dashboard":
    st.title("Personal Budget Dashboard")
    st.header("This dashboard gives you a visual representation of your finances.")
    st.markdown(
        """
        <p style='font-size: 22px; line-height: 1.6;'>
            The Personal Budget Dashboard puts every dollar at your fingertips. Connected to YNAB for live balances, add cash income or expenses on the fly, and watch the numbers refresh in real time.<br/><br/>
            Here’s what you can explore:
            <ul>
                <li>📂 <b>Transactions</b> – Track what’s coming in and going out, neatly grouped by account so nothing slips through the cracks.</li>
                <li>📊 <b>Spending Categories</b> – See exactly where your money goes each month with a crisp, color‑coded breakdown.</li>
                <li>💡 <b>Budgeting Plan</b> – Draft a forward‑looking income & expense plan without affecting historical reporting.</li>
            </ul>
            Clean charts, bold numbers, and a distraction‑free layout mean less digging for information and more confident, smarter money moves.
        </p>
        """,
        unsafe_allow_html=True,
    )

# ── Transactions & Spending Tab ────────────────────────────────────────
elif page == "Transactions & Spending":
    st.title("Transactions & Spending Overview")

    tabs = st.tabs(["Transactions", "Spending Categories"])

    # ───────────── Transactions Tab ───────────────────────────────────────────
    with tabs[0]:
        st.subheader("YNAB Linked Accounts")
        show_bal = st.checkbox("Show account balances", value=False)
        if show_bal:
            for acc in accounts:
                st.write(f"Account: {acc.name} — Balance: ${acc.balance / 1000:.2f}")

        # Group transactions by account
        tx_by_account = {}
        for tx in transactions:
            td = tx.to_dict()
            acct_name = account_map.get(td["account_id"], "Unknown Account")
            tx_by_account.setdefault(acct_name, []).append(
                {
                    "Date": td.get("date", "N/A"),
                    "Payee": td.get("payee_name", "Unlabeled"),
                    "Amount ($)": td.get("amount", 0) / 1000,
                }
            )

        st.subheader("Recent Transactions by Account")
        for acct_name, tx_list in tx_by_account.items():
            st.markdown(f"### {acct_name}")
            df_tx = (
                pd.DataFrame(tx_list)
                .sort_values("Date", ascending=False)
                .head(10)
            )
            st.dataframe(df_tx, hide_index=True)


    # ───────────── Spending Categories Tab ────────────────────────────────────
    with tabs[1]:
        st.subheader("Spending by Category")

        # Pull outflows from YNAB transactions
        ynab_tx = pd.DataFrame(
            [
                {
                    "category": tx.to_dict().get("category_name", "Uncategorized"),
                    "amount": abs(tx.to_dict().get("amount", 0)) / 1000,
                }
                for tx in transactions
                if tx.to_dict().get("amount", 0) < 0  # only outflows
            ]
        )

        ynab_tx = ynab_tx[~ynab_tx["category"].str.startswith("Inflow", na=False)]

        if ynab_tx.empty:
            st.info("No spending data yet.")
        else:
            totals = (
                ynab_tx.groupby("category", dropna=False)["amount"]
                .sum()
                .reset_index()
                .rename(columns={"amount": "Total ($)"})
                .sort_values("Total ($)", ascending=False)
            )

            st.bar_chart(totals.set_index("category")["Total ($)"])
            st.dataframe(totals, hide_index=True)

# ── Budgeting Plan  ─────────────────────────────────────────────
elif page == "Budgeting Plan":
    st.header("Budgeting Plan")
    st.subheader("Monthly Forward‑Looking Budget Plan")
    st.info("Be Sure To Input Income/Expense by Month.")

    with open("budget_tracker.json", "r") as f:
        plan_data = json.load(f)

    trans_type = st.selectbox(
        "Add to budget plan:",
        options=["", "Planned Income", "Planned Expense"],
    )

    def write_plan(key, new_entry, filename="budget_tracker.json"):
        with open(filename, "r+") as file:
            data = json.load(file)
            data[key].append(new_entry)
            file.seek(0)
            json.dump(data, file, indent=2)

    if trans_type == "Planned Income":
        inc = st.text_input("Planned income amount ($):")
        if inc:
            try:
                income_val = float(inc)
                write_plan("income", income_val)
                st.success("Planned income added!")
            except ValueError:
                st.error("Please enter a valid number for income.")


    elif trans_type == "Planned Expense":
        ynab_categories = sorted({
            tx.to_dict().get("category_name", "Uncategorized")
            for tx in transactions
            if not str(tx.to_dict().get("category_name", "")).startswith("Inflow")
        })

        with st.form("plan_expense", clear_on_submit=True):
            cat = st.selectbox(
                "Select a spending category",
                ynab_categories,
                index=None,
                placeholder="Select a category"
            )
            amt = st.text_input("Planned expense amount ($):")
            if st.form_submit_button("Submit") and amt and cat:
                try:
                    amt_val = float(amt)
                    write_plan("expenses", {"category": cat, "amount": amt_val})
                    st.success("Planned expense added!")
                except ValueError:
                    st.error("Please enter a valid number for the expense amount.")

    # Refresh plan_data after potential writes
    with open("budget_tracker.json", "r") as f:
        plan_data = json.load(f)

    plan_income = sum(plan_data["income"])
    plan_exp   = sum(e["amount"] for e in plan_data["expenses"])
    plan_left  = plan_income - plan_exp

    st.markdown("### Plan Totals")
    ci, ce, cl = st.columns(3)
    ci.metric("Planned Income", f"${plan_income:,.2f}")
    ce.metric("Planned Expenses", f"${plan_exp:,.2f}")
    cl.metric("Planned Left", f"${plan_left:,.2f}")

    st.markdown("#### Detailed Planned Expenses")
    if plan_data["expenses"]:
        st.dataframe(pd.DataFrame(plan_data["expenses"]), hide_index=True)
    else:
        st.write("No planned expenses added yet.")

    # ──Reset-plan button ──────────────────────────────
    if st.button("Reset Plan ⟳", key="reset_plan"):
        with open("budget_tracker.json", "w") as f:
            json.dump({"income": [], "expenses": []}, f, indent=2)

        # Clear any text the user is still typing
        st.session_state["plan_income_input"] = ""
        st.session_state["plan_exp_amount"] = ""
        st.session_state["plan_exp_cat"] = None

        # Force a rerun so the UI shows the cleared state
        try:
            st.rerun()
        except AttributeError:
            st.rerun()


