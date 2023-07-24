import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np

import time

@st.cache_resource()
def get_login_status():
    return [False]


def set_login_status(logged_in):
    login_status = get_login_status()
    login_status[0] = logged_in


def main():
    # Check if user is logged in
    logged_in = get_login_status()[0]

    # If the user is not logged in, show the login page
    if not logged_in:
        render_login_page()
    else:
        # If the user is logged in, show the main app page
        render_main_page()


def render_login_page():
    st.title('PennyWise :moneybag:')
    st.header("Your Personal Finance Tracker")
    st.divider()

    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            if username == "123" and password == "123":
                set_login_status(True)
                st.experimental_rerun()
            else:
                st.error(
                    'The entered username/password is incorrect. Please try again.', icon="🚨")

    st.divider()
    my_expander = st.expander("Don't have an account?")
    my_expander.subheader("Sign Up")

    with my_expander:
        sign_col1, sign_col2 = st.columns(2)
        first_name = sign_col1.text_input("First name")
        last_name = sign_col2.text_input("Last name")
        sign_username = st.text_input('Set Username')
        sign_password = st.text_input('Set Password', type='password')
        signup = st.button("Sign Up")
        if signup:
            set_login_status(True)
            st.experimental_rerun()


def render_main_page():

    st.markdown(
        """
    <style>
    section[data-testid="stSidebar"] div.stButton button {
    width: 300px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        selected = option_menu("Main Menu", ["Home", "Records", "Bills", "Dashboard", 'Settings'],
                               icons=['house', 'journals', 'newspaper', 'graph-up-arrow', 'gear'], menu_icon="coin", default_index=0)
        logout_button = st.button("Logout")
    # Logout button
    if logout_button:
        set_login_status(False)
        st.experimental_rerun()

    if selected == 'Home':
        st.title("Welcome, User")
        st.subheader("Get Tracking!")
        st.divider()
        sign_col1,sign_col2 = st.columns(2)
        sign_col1.metric(label="Cash", value="₹5000", delta="-₹500")        
        sign_col2.metric(label="ICICI", value="₹12000", delta="₹700")  
        st.divider()      
        sign_col1,sign_col2 = st.columns(2)
        record_type = sign_col1.selectbox("Pick type of record",["Income","Expense"])
        date = sign_col2.date_input(f"Date of {record_type}")
        amount = sign_col1.number_input('Amount')
        category = sign_col2.selectbox('Category',('❓ Others','🍔 Food & Drinks', '🛒 Shopping','🏚️ Housing','🚌 Transportation','🚗 Vehicle','💃 Life & Entertainment','📺 Communication & TV', '💳 Financial expense','💲 Investments','💸 Income'),index=1)
        account = sign_col1.selectbox("Select the account",['Cash','ICICI'])
        if category=='❓ Others':
            other_cat = sign_col2.text_input("Enter the custom category")
        comments = st.text_area("Any comments?",placeholder="Spent on food at the store near school")
        submit = st.button("Submit Record",type='primary',use_container_width=True)

        


        # st.error('This is an error', icon="🚨")
        # st.warning('This is a warning', icon="⚠️")
        # st.info('This is a purely informational message', icon="ℹ️")
        # st.success('This is a success message!', icon="✅")
        # e = RuntimeError('This is an exception of type RuntimeError')
        # st.exception(e)

    elif selected == 'Dashboard':
        st.title("📈 Review Time")
        st.divider()
        st.subheader("Income vs. Expense")
        chart_data = pd.DataFrame(
        np.random.randn(20, 2),columns=['Income', 'Expense'])

        st.line_chart(chart_data)
        

    elif selected == 'Records':
        st.title("🗃️ Record Archive")
        st.markdown(
            """
            <style>
            
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.subheader('24/7/2023')
        col1,col2 = st.columns(2)
        rec1 = col1.multiselect("Record #1",options=['Expense','🍔 Food & Drinks','₹525','Cash'],default=['Expense','🍔 Food & Drinks','₹525','Cash'])
        rec2_button = col1.button("Edit Record #1")
        rec2 = col2.multiselect("Record #2",options=['Income','💸 Income','₹1090','ICICI'],default=['Income','💸 Income','₹1090','ICICI'])
        rec2_button = col2.button("Edit Record #2")

    elif selected == 'Bills':
        st.title("📆 Remind My Bills")
        st.divider()
        sign_col1,sign_col2 = st.columns(2)
        due_date = sign_col1.date_input(f"Due Date of Bill")
        category = sign_col2.selectbox('Category',('❓ Others','🍔 Food & Drinks', '🛒 Shopping','🏚️ Housing','🚌 Transportation','🚗 Vehicle','💃 Life & Entertainment','📺 Communication & TV', '💳 Financial expense','💲 Investments','💸 Income'),index=1)
        amount = sign_col1.number_input('Amount')
        if category=='❓ Others':
            other_cat = sign_col2.text_input("Enter the custom category")
        repeating = sign_col1.checkbox('This is a Recurring Bill')
        if repeating==True:
            reminder = sign_col2.selectbox("Remind Me", ('Daily','Monthly','Yearly'))
        comments = st.text_area("Any comments?",placeholder="Need to pay the Electricity bill")
        submit = st.button("Submit Bill",type='primary',use_container_width=True)


    elif selected == 'Settings':
        st.title("User Details")
        sign_col1, sign_col2 = st.columns(2)
        first_name = sign_col1.text_input("First name")
        last_name = sign_col2.text_input("Last name")
        dob = st.date_input("When's your birthday",)
        email = st.text_input("Email ID")
        bank_accounts = {}
        num_accounts = st.number_input("Number of Accounts to Add", min_value=1, value=1)
        for i in range(1,num_accounts+1):
            acc_name, acc_bal = add_account(i)
            bank_accounts[acc_name] = acc_bal

        st.write("Bank Account Names:")
        for account in bank_accounts:
            st.write(f"{account} : {bank_accounts[account]}")

        submitted = st.button("Update Details",type='primary',use_container_width=True)


def add_account(i):
    col1, col2 = st.columns(2)
    new_account = col1.text_input(f"Account {i}")
    new_balance = col2.number_input(f"Total Balance for Account {i}")
    return new_account,new_balance
    # You can add more pages to the sidebar here (they will only be visible after login)


if __name__ == "__main__":
    main()
