import streamlit as st
import pandas as pd
import requests
import ynab
import json
import os


# Ynab Access Key - Secured-
ACCESS_TOKEN = st.secrets["YNAB_ACCESS_TOKEN"]

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

response = requests.get("https://api.ynab.com/v1/budgets", headers=headers)

print("Status Code:", response.status_code)
print("Response:", response.json())

# ----------------------------------------

if not os.path.exists("budget_tracker.json"):
    with open("budget_tracker.json", "w") as f:
        json.dump({"income": [], "expenses": []}, f, indent=2)

# MUST be the first Streamlit command
st.set_page_config(page_title="Personal Budget Dashboard", layout="wide")

# ----- CONFIGURATION -----
ACCESS_TOKEN = "g8_VguDBKmT2zSukz82OPJmUp9izDnnLulpAr35Nnhk"  # Replace with your full token in quotes


configuration = ynab.Configuration(
    access_token= "g8_VguDBKmT2zSukz82OPJmUp9izDnnLulpAr35Nnhk"
)

# ----- Connect to YNAB API -----
with ynab.ApiClient(configuration) as client:
    budgets_api = ynab.BudgetsApi(client)
    budgets_response = budgets_api.get_budgets()
    budgets = budgets_response.data.budgets

    for budget in budgets:
        print(budget.name)

# ----- Streamlit App -----
st.title("Personal Budget Dashboard")
st.header("Are you ready to save money?")
st.subheader("This dashboard gives you a visual representation of your finances.")
st.info("Organize your monthly budget below!")

#  Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ("Transactions", "Spending Categories", "Budgeting"),
    index=0
)

#  Let user log manual income / expense
transaction = st.selectbox(
    "Select a transaction type",
    options=["", "Add Monthly Income", "Add Monthly Expense"]
)

def write_json(transaction_type, new_data, filename="budget_tracker.json"):
    with open(filename, "r+") as file:
        data = json.load(file)
        data[transaction_type].append(new_data)
        file.seek(0)
        json.dump(data, file, indent=2)

if transaction == "Add Monthly Income":
    income = st.text_input("Enter your income:")
    if income:
        write_json("income", float(income))

elif transaction == "Add Monthly Expense":
    with st.form("expense", clear_on_submit=True):
        category = st.selectbox(
            "Select a category",
            ["", "Entertainment", "Utilities", "School", "Rent", "Transportation",
             "Health", "Groceries"]
        )
        amount = st.text_input("Enter your expense amount:")
        if st.form_submit_button("Submit") and amount:
            write_json("expenses", {"category": category, "amount": float(amount)})

#  Load local JSON data (needed for two of the tabs)
with open("budget_tracker.json", "r") as f:
    local_data = json.load(f)

#   YNAB data (accounts + transactions)
budget_id = budgets[0].id
accounts_api = ynab.AccountsApi(client)
transactions_api = ynab.TransactionsApi(client)

accounts = accounts_api.get_accounts(budget_id).data.accounts
transactions = transactions_api.get_transactions(budget_id).data.transactions

account_map = {acc.id: acc.name for acc in accounts}

# Page-specific content
if page == "Transactions":
    st.subheader("YNAB Linked Accounts")
    for acc in accounts:
        st.write(f"Account: {acc.name} — Balance: ${acc.balance / 1000:.2f}")

    # group transactions by account
    tx_by_account = {}
    for tx in transactions:
        txd = tx.to_dict()
        acct_name = account_map.get(txd["account_id"], "Unknown Account")
        tx_by_account.setdefault(acct_name, []).append({
            "Date": txd.get("date", "N/A"),
            "Payee": txd.get("payee_name", "Unlabeled"),
            "Amount ($)": txd.get("amount", 0) / 1000
        })

    st.subheader("Recent Transactions by Account")
    for acct_name, tx_list in tx_by_account.items():
        st.markdown(f"### {acct_name}")
        df_tx = (
            pd.DataFrame(tx_list)
              .sort_values("Date", ascending=False)
              .head(10)                      # ⬅️ change here if you want >10
        )
        st.dataframe(df_tx, hide_index=True)

# ────────────────────────────────────────────────────
elif page == "Spending Categories":
    st.subheader("Spending by Category (YNAB + Manual)")

    # Combine manual expenses with YNAB outflows
    manual_exp = (
        pd.DataFrame(local_data["expenses"])
        if local_data["expenses"]
        else pd.DataFrame(columns=["category", "amount"])
    )

    ynab_tx = pd.DataFrame([
        {
            "category": tx.to_dict().get("category_name", "Uncategorized"),
            "amount": abs(tx.to_dict().get("amount", 0)) / 1000  # milli-units → $
        }
        for tx in transactions
        if tx.to_dict().get("amount", 0) < 0                    # only outflows
    ])

    combined = pd.concat([manual_exp, ynab_tx], ignore_index=True)

    if combined.empty:
        st.info("No spending data yet.")
    else:
        # Sum by category
        totals = (
            combined.groupby("category", dropna=False)["amount"]
                    .sum()
                    .reset_index()
                    .rename(columns={"amount": "Total ($)"})
                    .sort_values("Total ($)", ascending=False)
        )

        # # Pie chart with Altair
        # import altair as alt
        #
        # pie = (
        #     alt.Chart(totals)
        #        .mark_arc(innerRadius=50)
        #        .encode(
        #            theta="`Total ($)`:Q",
        #            color="category:N",
        #            tooltip=["category:N", "`Total ($)`:Q"]
        #        )
        #        .properties(width=400, height=400)
        # )
        # st.altair_chart(pie, use_container_width=True)
        #
        # # Optional: numeric table
        # st.dataframe(totals, hide_index=True)



# ─────────────────────────────────────
elif page == "Budgeting":
    st.subheader("Budget Summary")
    income_total = sum(local_data["income"])
    spent_total = sum(e["amount"] for e in local_data["expenses"])
    remaining = income_total - spent_total

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${income_total:,.2f}")
    col2.metric("Money Spent", f"${spent_total:,.2f}")
    col3.metric("Amount Left", f"${remaining:,.2f}")

    st.caption("Income and expenses above come from the manual entries feature.")
