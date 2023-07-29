import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import time
import pymongo

def connect_to_mongodb():
    try:
        conn = pymongo.MongoClient("mongodb://localhost:27017")
        mydb = conn['PennyWise']

        return mydb

    except:
            print("Error")


@st.cache_resource()
def get_username():
    return [None]

def set_username(user):
    username = get_username()
    username[0] = user

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
    mydb = connect_to_mongodb()
    user_col = mydb['User']
    login_col = mydb['Login']

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
            try:
                if(username == login_col.find({"Username":username})[0]['Username'] and password==login_col.find({"Username":username})[0]['Password']):
                    set_username(username)
                    set_login_status(True)
                    st.experimental_rerun()
                elif(password!=login_col.find({"Username":username})[0]['Password']):
                    st.error(
                        'The entered username/password is incorrect. Please try again.', icon="🚨")
                    
                    
            except IndexError as e:
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
            names = [name['Username'] for name in (record for record in login_col.find({},{"Username":1,"_id":0}))]
            if(sign_username not in names):
                if(first_name.strip()=="" or last_name.strip()=="" or sign_username.strip()=="" or sign_password.strip()==""):
                    st.error(
                        'Please fill the above details before proceeding!', icon="🚨")
                else:
                    user_col.insert_one({"First Name":first_name, "Last Name":last_name, "Email":sign_username,"Accounts":{}})
                    login_col.insert_one({"Username":sign_username,"Password":sign_password})
                    st.success('User successfully created. Please Log in!', icon="✅")
                    # set_login_status(True)
                    # st.experimental_rerun()
            else:
                st.error(
                        'User already exists!', icon="🚨")



def render_main_page():
    mydb = connect_to_mongodb()
    user_col = mydb['User']
    login_col = mydb['Login']

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
        # --------- MongoDB  --------- #
        saved_accounts = user_col.find({'Email':get_username()[0]})[0]['Accounts']
        key_iter = iter(saved_accounts)
        val_iter = iter(saved_accounts.values())
        # --------- FrontEnd --------- #
        st.title(f"Welcome, {user_col.find({'Email':get_username()[0]})[0]['First Name']}")
        st.subheader("Get Tracking!")
        st.divider()
        mylist = st.columns(len(saved_accounts))
        for i in range(0,len(saved_accounts)):
            mylist[i].metric(label=next(key_iter), value=next(val_iter), delta="₹500")
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
        rec1 = col1.multiselect("Record #1",options=['Expense','🍔 Food & Drinks','₹525','Cash'],default=['Expense','🍔 Food & Drinks','₹525','Cash'],disabled=True)
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
        first_name = sign_col1.text_input("First name",value=user_col.find({'Email':get_username()[0]})[0]['First Name'])
        last_name = sign_col2.text_input("Last name",value=user_col.find({'Email':get_username()[0]})[0]['Last Name'])
        dob = st.date_input("When's your birthday",)
        email = st.text_input("Email ID", value=user_col.find({'Email':get_username()[0]})[0]['Email'],disabled=True)
        password = st.text_input("Change Password",type='password',value=login_col.find({'Username':get_username()[0]})[0]['Password'])
        bank_accounts = {}
        saved_accounts = user_col.find({'Email':get_username()[0]})[0]['Accounts']
        num_accounts = st.number_input("Number of Accounts to Add", min_value=1, value=(len(saved_accounts) or 1))
        key_iter = iter(saved_accounts)
        val_iter = iter(saved_accounts.values())
        for i in range(1,num_accounts+1):
            acc_name, acc_bal = add_account(i,next(key_iter, None),next(val_iter, None))
            bank_accounts[acc_name] = acc_bal

        # st.write("Bank Account Names:")
        # st.write(bank_accounts)
        # for account in bank_accounts:
        #     st.write(f"{account} : {bank_accounts[account]}")
        # saved_accounts = user_col.find({'Email':get_username()[0]})[0]['Accounts']
        # st.write(saved_accounts)
        # for k in saved_accounts.keys():
        #     st.write(k)
        submitted = st.button("Update Details",type='primary',use_container_width=True)
        if submitted:
            if(num_accounts<len(bank_accounts)):
                pass
            user_col.update_one({'Email':get_username()[0]},{'$set':{'First Name':first_name,'Last Name':last_name, 'DOB':str(dob),'Email':email,'Accounts':bank_accounts}})
            login_col.update_one({'Username':get_username()[0]},{'$set':{'Username':email,'Password':password}})


def add_account(i,acc,bal):
    col1, col2 = st.columns(2)
    new_account = col1.text_input(f"Account {i}",value=(acc or ""))
    new_balance = col2.number_input(f"Total Balance for Account {i}",value=(bal or 0.00),min_value=0.00)
    return new_account,new_balance
    # You can add more pages to the sidebar here (they will only be visible after login)

if __name__ == "__main__":
    main()
