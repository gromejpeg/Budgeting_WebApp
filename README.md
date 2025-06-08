1) Introduction:  The application I decided to do was a personal finance and budgeting dashboard.  The purpose of this application is that users can go in and see what their recent transactions are, have it grouped into spending categories to give the user a visual of what they are spending their money on. Then using that information to then make a budget based on how they spend their money in hopes that then can get organized and be more financially responsible.


2) Usability Goals Personal Finance/Budget Dashboard:

1) Ease of Navigation - Make the application visually appealing and easy to navigate 

2) Clarity of Financial Data - Display financial data in a way that gives the user more insight on their finances.

3) Data Entry Simplicity - Simply input budget data in a clear and concise way, giving the user a clear plan on how and what to spend their money on. 

4) Visual Feedback and Responsiveness - Having the app give feedback markers so the user knows how their input effects the app. 

5) Error Prevention and Recovery - Give the user proper error messages and giving a solution to proceed.

7) Overall User Satisfaction - Ensure application is up to standard on all set parameters 

3) Design Process:

I want my application to be a finance/budgeting application. 

I decided to use the YNAB API to be able to connect my bank information to my web application to see what transactions I have had and to then break them into categories to be able to visualize the financial data better so I can then plan a budget according. 

I want to have 3 tabs separated by a sidebar. 
- Dashboard - this will display a home page where it tells you what the application is for and how to use it.
- Transactions & Spending Categories - this tab will show user the data that is pulled form YNAB where you can see all your recent transactions and then in a sub - tab on the page I want to add the categories of those transaction so user can visualize where their money is going. This page will be an indicator on what the user is spending their money on so when they plan their budget they can see how much they have been spending. 
- Budgeting Plan - This tab will be where the user can plan a budget that they can follow. The goal is that the user can see how their spending is in the spending and category tab. Then take that information and design a budget that can best suit them. 

The overall is goal is that the user understands what the purpose of the application is for and to be able to navigate in a simple manner while still being effective. 

4) API INTEGRATION:

The API used again is YNAB the API. The API connects the web application to information from YNAB which is linked to user bank account. The web application pulls this data and shows an interactive table with recent transactions and breaks those transaction into categories provided by YNAB as well. 

5) Interactive Widgets:

Interactive widgets found in my code would be 

st.sidebar.radio - Pick one of the three main views: Dashboard, Transactions & Spending, or Budgeting Plan.

st.tabs - Switch between the two subtabs.

st.checkbox - Toggle whether account balances are displayed.

st.selectbox - Choose between Planned Income and Planned Expense (or leave blank). // Pick a spending category for the planned expense.

st.text_input - Enter the dollar amount for a planned income entry. // Type the dollar amount to plan for that category.

st.form / st.form_submit_button - Groups the category + amount inputs and provides a Submit button that commits them atomically.

st.button - Clears the local budget_tracker.json and resets all planning inputs.

st.dataframe - Users can scroll, sort, and filter the displayed data frames, though they don’t write data back.

6) HCI Design Principles:

- Visibility of system status
- Match between system & real world
- User control & freedom
- Consistency & standards
- Error prevention
- Recognition rather than recall
- Flexibility & efficiency of use
- Aesthetic & minimalist design
- Help users recognize, diagnose, recover from errors
- Offer informative feedback
- Permit easy reversal of action

7) Conclusion:
To conclude, This application allows me to view transaction data, breaks it into spending categories. Then allows me to build a budget based on data received to best help my finances. 

Some changes I would implement are to make it so any user can put in their YNAB info and do this for themselves. 
