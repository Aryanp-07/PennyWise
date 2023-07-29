import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import time
import pymongo
from datetime import datetime as dt, timedelta

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
    accounts_col = mydb['Accounts']

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
                    accounts_col.insert_one({'Username':sign_username,'Accounts':{}})
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
    record_col = mydb['Records']
    accounts_col = mydb['Accounts']
    bills_col = mydb['Bills']

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
        saved_accounts = accounts_col.find({'Username':get_username()[0]})[0]['Accounts']
        key_iter = iter(saved_accounts)
        val_iter = iter(saved_accounts.values())
        account_list = []
        # --------- FrontEnd --------- #
        st.title(f"Welcome, {user_col.find({'Email':get_username()[0]})[0]['First Name']}  👋")
        st.subheader("Get Tracking!")
        st.divider()

        mylist = st.columns((len(saved_accounts)) or 1)
        for i in range(0,len(saved_accounts)):
            name = next(key_iter)
            bal = next(val_iter)
            mylist[i].metric(label=name, value=bal) #, delta="₹500"
            account_list.append(name)

        st.divider()      
        sign_col1,sign_col2 = st.columns(2)
        record_type = sign_col1.selectbox("Pick type of record",["Income","Expense"])
        date = sign_col2.date_input(f"Date of {record_type}")
        amount = sign_col1.number_input('Amount')
        category = sign_col2.selectbox('Category',('❓ Others','🍔 Food & Drinks', '🛒 Shopping','🏚️ Housing','🚌 Transportation','🚗 Vehicle','💃 Life & Entertainment','📺 Communication & TV', '💳 Financial expense','💲 Investments','💸 Income'),index=1)
        account = sign_col1.selectbox("Select the account",account_list)
        if category=='❓ Others':
            other_cat = sign_col2.text_input("Enter the custom category")
        comments = st.text_area("Any comments?",placeholder="Spent on food at the store near school")
        submit = st.button("Submit Record",type='primary',use_container_width=True)

        if submit:
            if(amount==0.00):
                st.error('Please enter a non-zero amount!', icon="🚨")
            else:
                if(category!='❓ Others'):
                    record_col.insert_one({'Username':get_username()[0],'Date':str(date),'Type':record_type,'Category':category,'Account':account,'Amount':amount,'Comments':comments})
                else:
                    record_col.insert_one({'Username':get_username()[0],'Date':str(date),'Type':record_type,'Category':category,'Category Description':other_cat,'Account':account,'Amount':amount,'Comments':comments})
                
                if(record_type=='Expense'):
                    saved_accounts[account] -= amount
                elif(record_type=='Income'):
                     saved_accounts[account] += amount
                accounts_col.update_one({'Username':get_username()[0]},{'$set':{'Accounts':saved_accounts}})

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
        # --------- MongoDB  --------- #
        saved_accounts = accounts_col.find({'Username':get_username()[0]})[0]['Accounts']
        key_iter = iter(saved_accounts)
        val_iter = iter(saved_accounts.values())
        account_list = ['All']
        for i in range(0,len(saved_accounts)):
            name = next(key_iter)
            account_list.append(name)

        # --------- FrontEnd --------- #    
        st.title("🗃️ Record Archive")
        # Get the filter options from the user
        filter_check = st.checkbox("Do you want to apply filters?")
        col1,col2 = st.columns(2)
        filters = {}
        if filter_check:
            date_filter = col1.date_input("Search by date", key='date')
            if date_filter:
                filters['date'] = date_filter

            account_filter = col2.selectbox("Filter by account", account_list, key='account')
            if account_filter != "All":
                filters['account'] = account_filter

            type_filter = col1.selectbox("Filter by type", ["All", "Expense", "Income"], key='type')
            if type_filter != "All":
                filters['type'] = type_filter

            category_filter = col2.selectbox("Filter by category", ["All", '❓ Others','🍔 Food & Drinks', '🛒 Shopping','🏚️ Housing','🚌 Transportation','🚗 Vehicle','💃 Life & Entertainment','📺 Communication & TV', '💳 Financial expense','💲 Investments','💸 Income'], key='category')
            if category_filter != "All":
                filters['category'] = category_filter
        
        query = {'Username': get_username()[0]}

        # Update the query based on the user-selected filters
        if 'date' in filters:
            query['Date'] = str(filters['date'])

        if 'account' in filters:
            query['Account'] = filters['account']

        if 'type' in filters:
            query['Type'] = filters['type']

        if 'category' in filters:
            query['Category'] = filters['category']

        cursor = record_col.find(query, {"_id": 0, 'Username': 0}).sort("Date", pymongo.DESCENDING)
        
        # filter_check = st.checkbox("Do you want to search by date?")
        # if filter_check:
        #     date_filter = st.date_input("Search by date")
        records = list(cursor)
        if records:
            # Group the records by date
            grouped_records = {}
            for record in records:
                date = record["Date"]
                if date not in grouped_records:
                    grouped_records[date] = []
                grouped_records[date].append(record)

            if filter_check:
                # Display the records with date as heading
                for date, records in grouped_records.items():
                    if(date==str(date_filter)):
                        st.header(f"{date}")
                        for record in records:
                            with st.expander(f"{record['Comments']}"):
                                st.write(record)
                # display the following if no records exist for the searched date
                if(str(date_filter) not in grouped_records.keys()):
                    st.info("You have no records for this date", icon="🤖")
            else:
                    # Display the records with date as heading
                for date, records in grouped_records.items():
                    st.header(f"{date}")
                    for record in records:
                        with st.expander(f"{record['Comments']}"):
                            st.write(record)
        else:
            st.info("You have no records", icon="🤖")
                    # st.write("Type:", record["Type"])
                    # st.write("Category:", record["Category"])
                    # st.write("Account:", record["Account"])
                    # st.write("Amount:", record["Amount"])
                    # st.write("Comments:", record["Comments"])
                    # st.write("--------------")
        # st.markdown(
        #     """
        #     <style>
            
        #     </style>
        #     """,
        #     unsafe_allow_html=True,
        # )
        # st.subheader('24/7/2023')
        # col1,col2 = st.columns(2)
        # rec1 = col1.multiselect("Record #1",options=['Expense','🍔 Food & Drinks','₹525','Cash'],default=['Expense','🍔 Food & Drinks','₹525','Cash'],disabled=True)
        # rec2_button = col1.button("Edit Record #1")
        # rec2 = col2.multiselect("Record #2",options=['Income','💸 Income','₹1090','ICICI'],default=['Income','💸 Income','₹1090','ICICI'])
        # rec2_button = col2.button("Edit Record #2")

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
        if repeating:
            reminder = sign_col2.selectbox("Remind Me", ('Daily','Monthly','Yearly'))
        else:
            reminder = 'NA'
        comments = st.text_area("Any comments?",placeholder="Need to pay the Electricity bill")
        submit = st.button("Submit Bill",type='primary',use_container_width=True)

        if submit:
            if(amount==0.00):
                st.error('Please enter a non-zero amount!', icon="🚨")
            else:
                if(category!='❓ Others'):
                    bills_col.insert_one({'Username':get_username()[0],'Due Date':str(due_date),'Category':category,'Amount':amount,'Remind':reminder,'Comments':comments})
                else:
                    bills_col.insert_one({'Username':get_username()[0],'Due Date':str(due_date),'Category':category,'Category Description':other_cat,'Amount':amount,'Remind':reminder,'Comments':comments})

        st.divider()
        st.title("📆 Upcoming Bills")
        st.divider()
        query = {'Username': get_username()[0]}
        projection = {"_id": 0, 'Username': 0}
        cursor = bills_col.find(query, projection).sort("Due Date", pymongo.ASCENDING)
        bills = list(cursor)
        current_date = dt.now().date()
                
       
        if bills:
        # Group the bills by the number of days left
            grouped_bills = {}
            for bill in bills:
                date_due = dt.strptime(bill['Due Date'], "%Y-%m-%d").date()
                days_left = (date_due - current_date).days
                if days_left not in grouped_bills:
                    grouped_bills[days_left] = []
                grouped_bills[days_left].append(bill)

            # Display the bills grouped by days left using the expander widget
            for days_left, bills_list in sorted(grouped_bills.items()):
                if days_left == 0:
                    for bill in bills_list:
                        # Check for bills with "Monthly" or "Yearly" reminder and create a new bill for the next month/year
                        if bill["Remind"] == "Monthly" or bill["Remind"] == "Yearly":
                            create_next_bill(bill,bills_col)
                        # Delete the bills with 0 days left from the collection
                        bills_col.delete_one({"_id": bill["_id"]})
                st.header(f"{days_left} Days left for")
                for bill in bills_list:
                    with st.expander(f"{bill['Category']} - {bill['Due Date']}"):
                        st.write(bill)
        else:
            st.info("You have no bills due", icon="💡")


    elif selected == 'Settings':
        st.title("User Details")
        sign_col1, sign_col2 = st.columns(2)
        first_name = sign_col1.text_input("First name",value=user_col.find({'Email':get_username()[0]})[0]['First Name'])
        last_name = sign_col2.text_input("Last name",value=user_col.find({'Email':get_username()[0]})[0]['Last Name'])
        dob = st.date_input("When's your birthday",)
        email = st.text_input("Email ID", value=user_col.find({'Email':get_username()[0]})[0]['Email'],disabled=True)
        password = st.text_input("Change Password",type='password',value=login_col.find({'Username':get_username()[0]})[0]['Password'])
        bank_accounts = {}
        account_list = []
        saved_accounts = accounts_col.find({'Username':get_username()[0]})[0]['Accounts']
        num_accounts = st.number_input("Number of Accounts to Add", min_value=1, value=(len(saved_accounts) or 1))
        key_iter = iter(saved_accounts)
        val_iter = iter(saved_accounts.values())
        for i in range(1,num_accounts+1):
            acc_name, acc_bal = add_account(i,next(key_iter, None),next(val_iter, None))
            bank_accounts[acc_name] = acc_bal
            account_list.append(acc_name)

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
            user_col.update_one({'Email':get_username()[0]},{'$set':{'First Name':first_name,'Last Name':last_name, 'DOB':str(dob),'Email':email,'Accounts':account_list}})
            login_col.update_one({'Username':get_username()[0]},{'$set':{'Username':email,'Password':password}})
            accounts_col.update_one({'Username':get_username()[0]},{'$set':{'Accounts':bank_accounts}})


def create_next_bill(bill,bills_col):
    if bill["Remind"] == "Monthly":
        # Calculate the next month's due date
        next_due_date = (dt.strptime(bill["Due Date"], "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
    elif bill["Remind"] == "Yearly":
        # Calculate the next year's due date
        next_due_date = (dt.strptime(bill["Due Date"], "%Y-%m-%d") + timedelta(days=365)).strftime("%Y-%m-%d")

    # Create a new bill with the next due date
    if(bill['Category']=='❓ Others'):
        new_bill = {
            "Username": bill["Username"],
            "Due Date": next_due_date,
            "Category": bill["Category"],
            "Category Description": bill["Category Description"],
            "Amount": bill["Amount"],
            "Remind": bill["Remind"],
            "Comments": bill["Comments"]
        }
    else:
        new_bill = {
            "Username": bill["Username"],
            "Due Date": next_due_date,
            "Category": bill["Category"],
            "Amount": bill["Amount"],
            "Remind": bill["Remind"],
            "Comments": bill["Comments"]
        }

    # Insert the new bill into the collection
    bills_col.insert_one(new_bill)

def add_account(i,acc,bal):
    col1, col2 = st.columns(2)
    new_account = col1.text_input(f"Account {i}",value=(acc or ""))
    new_balance = col2.number_input(f"Total Balance for Account {i}",value=(bal or 0.00),min_value=0.00)
    return new_account,new_balance
    # You can add more pages to the sidebar here (they will only be visible after login)

if __name__ == "__main__":
    main()
