# ----------- Documentations ----------- #
# Streamlit documentation- https://docs.streamlit.io/
# Streamlit main page- https://streamlit.io/
# Streamlit emojis- https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
# Streamlit Menubar icons - https://icons.getbootstrap.com/

# ----------- Imports ----------- #
import streamlit as st
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import time
import pymongo
import os
from datetime import datetime as dt, timedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def configure():
    load_dotenv()
#function to connect to mongodb
def connect_to_mongodb():
    uri = "mongodb+srv://"+os.getenv('user')+":"+os.getenv('pass')+"@"+os.getenv('url')+"/?retryWrites=true&w=majority"
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        # Create a new client and connect to the server
        mydb = client['PennyWise']
        return mydb
        # conn = pymongo.MongoClient("mongodb://localhost:27017")
        # mydb = conn['PennyWise']
        # return mydb

    except:
            print("Error")


# function to find the current user details and cache the result
@st.cache_resource()
def get_username():
    return [None]

# function to store the current user details
def set_username(user):
    username = get_username()
    username[0] = user

# function to check the login status and cache the result
@st.cache_resource()
def get_login_status():
    return [False]

# function to set the login_status to know if user has logged in
def set_login_status(logged_in):
    login_status = get_login_status()
    login_status[0] = logged_in

# function to create a new bill every month/year for the recurring bills
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


# function to add a new account input in the frontend for Settings page
def add_account(i,acc,bal):
    col1, col2 = st.columns(2)
    # insert new text_input for account name
    new_account = col1.text_input(f"Account {i}",value=(acc or ""))
    # insert new number_input for account balance 
    new_balance = col2.number_input(f"Total Balance for Account {i}",value=(float(bal) or 0.00),min_value=0.00)
    return new_account,new_balance

# Marks start of execution
def main():
    configure()
    # Check if user is logged in
    logged_in = get_login_status()[0]

    # If the user is not logged in, show the login page
    if not logged_in:
        render_login_page()
    else:
        # If the user is logged in, show the main app page
        render_main_page()

# function to render the login page on start up or when user logs out
def render_login_page():
    # connect to mongodb database and load all collections required in login page
    mydb = connect_to_mongodb()
    user_col = mydb['User']
    login_col = mydb['Login']
    accounts_col = mydb['Accounts']

    st.title('PennyWise :moneybag:')
    st.header("Your Personal Finance Tracker")
    st.divider()

    # create a form for taking login credentials
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")

        # if form is submitted
        if submitted:
            try:
                # check if login credentials are correct
                if(username == login_col.find({"Username":username})[0]['Username'] and password==login_col.find({"Username":username})[0]['Password']):
                    # save the current user's details
                    set_username(username)
                    # set the login_status to True to render the main_page
                    set_login_status(True)
                    st.experimental_rerun()

                # if credentails are wrong, show error message
                elif(password!=login_col.find({"Username":username})[0]['Password']):
                    st.error(
                        'The entered username/password is incorrect. Please try again.', icon="🚨")
                    
            # if user doesnt exist, show error message
            except IndexError as e:
                st.error(
                        'The User doesnt exist. Please Sign Up.', icon="🚨")
                

    st.divider()
    my_expander = st.expander("Don't have an account?")
    my_expander.subheader("Sign Up")

    # create an expander to let user sign up
    with my_expander:
        sign_col1, sign_col2 = st.columns(2)
        # take user input for creating new user
        first_name = sign_col1.text_input("First name")
        last_name = sign_col2.text_input("Last name")
        sign_username = st.text_input('Set Username')
        sign_password = st.text_input('Set Password', type='password')
        signup = st.button("Sign Up")

        # if user tried to sign up, do the following
        if signup:
            # check whether the user already exists
            names = [name['Username'] for name in (record for record in login_col.find({},{"Username":1,"_id":0}))]
            
            # if user doesnt exist
            if(sign_username not in names):
                # if sign up details not provided, show error message
                if(first_name.strip()=="" or last_name.strip()=="" or sign_username.strip()=="" or sign_password.strip()==""):
                    st.error(
                        'Please fill the above details before proceeding!', icon="🚨")
                
                # else create user
                else:
                    # create a new document for user in user details
                    user_col.insert_one({"First Name":first_name, "Last Name":last_name, "Email":sign_username,"Accounts":{}})
                    # create a new document for user in login details
                    login_col.insert_one({"Username":sign_username,"Password":sign_password})
                    # create a new document for user in account details
                    accounts_col.insert_one({'Username':sign_username,'Accounts':{}})
                    # show success message that user is created and ask them to login
                    st.success('User successfully created. Please Log in!', icon="✅")
                    # set_login_status(True)
                    # st.experimental_rerun()
            
            # else user already exists
            else:
                st.error(
                        'User already exists!', icon="🚨")


# function to render the main_page of the project
def render_main_page():

    # connect to mongodb and open all collections
    mydb = connect_to_mongodb()
    user_col = mydb['User']
    login_col = mydb['Login']
    record_col = mydb['Records']
    accounts_col = mydb['Accounts']
    bills_col = mydb['Bills']

    # categories stored in a variable
    categories_list = ('❓ Others','🍔 Food & Drinks', '🛒 Shopping','🏚️ Housing','🚌 Transportation','🚗 Vehicle','💃 Life & Entertainment','📺 Communication & TV', '💳 Financial expense','💲 Investments','💸 Income')
    # customize the logout button using CSS
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

    # You can add more pages to the sidebar here (they will only be visible after login)
    with st.sidebar:
        selected = option_menu("Main Menu", ["Home", "Records", "Edit Record","Bills", "Dashboard", 'Settings'],
                               icons=['house', 'journals', 'pencil-square','newspaper', 'graph-up-arrow', 'gear'], menu_icon="coin", default_index=0)
        logout_button = st.button("Logout")
    
    # if Logout button is clicked, globally set login_status False so that Login page is rendered
    if logout_button:
        set_login_status(False)
        st.experimental_rerun()

    # if Home is selected in menubar
    if selected == 'Home':
        # --------- MongoDB  --------- #
        # retrieve all the accounts of user
        saved_accounts = accounts_col.find({'Username':get_username()[0]})[0]['Accounts']
        # iterate through the account name
        key_iter = iter(saved_accounts)
        # iterate through the account balance
        val_iter = iter(saved_accounts.values())
        account_list = []
        # --------- FrontEnd --------- #
        st.title(f"Welcome, {user_col.find({'Email':get_username()[0]})[0]['First Name']}  👋")
        st.subheader("Get Tracking!")
        st.divider()
        # create as many columns as there are accounts or if no accounts, create 1 column
        mylist = st.columns((len(saved_accounts)) or 1)
        for i in range(0,len(saved_accounts)):
            name = next(key_iter)
            bal = next(val_iter)
            # display the account names with their current balance using cards
            mylist[i].metric(label=name, value=bal) #, delta="₹500"
            account_list.append(name)

        st.divider()      
        sign_col1,sign_col2 = st.columns(2)

        # take user inputs
        record_type = sign_col1.selectbox("Pick type of record",["Income","Expense"])
        date = sign_col2.date_input(f"Date of {record_type}")
        amount = sign_col1.number_input('Amount')
        category = sign_col2.selectbox('Category',categories_list,index=1)
        account = sign_col1.selectbox("Select the account",account_list)
        if category=='❓ Others':
            other_cat = sign_col2.text_input("Enter the custom category")
        comments = st.text_area("Any comments?",placeholder="Spent on food at the store near school")
        submit = st.button("Submit Record",type='primary',use_container_width=True)

        # if submit button clicked, do the following
        if submit:
            if(amount==0.00):
                st.error('Please enter a non-zero amount!', icon="🚨")
            else:
                # if category is others, add record data with category description
                if(category!='❓ Others'):
                    record_col.insert_one({'Username':get_username()[0],'Date':str(date),'Type':record_type,'Category':category,'Account':account,'Amount':amount,'Comments':comments})
                # else add record data as is
                else:
                    record_col.insert_one({'Username':get_username()[0],'Date':str(date),'Type':record_type,'Category':category,'Category Description':other_cat,'Account':account,'Amount':amount,'Comments':comments})
                
                # if record type is Expense, subtract amount from account
                if(record_type=='Expense'):
                    saved_accounts[account] -= amount

                # if record type is Income, add amount to account
                elif(record_type=='Income'):
                     saved_accounts[account] += amount

                # update the accounts collection with new amounts
                accounts_col.update_one({'Username':get_username()[0]},{'$set':{'Accounts':saved_accounts}})
                st.experimental_rerun()

        # st.error('This is an error', icon="🚨")
        # st.warning('This is a warning', icon="⚠️")
        # st.info('This is a purely informational message', icon="ℹ️")
        # st.success('This is a success message!', icon="✅")
        # e = RuntimeError('This is an exception of type RuntimeError')
        # st.exception(e)

        

    # if Records selected in Menubar
    elif selected == 'Records':
        # --------- MongoDB  --------- #
        # retrieve all the accounts of user
        saved_accounts = accounts_col.find({'Username':get_username()[0]})[0]['Accounts']
        # iterate through the account name
        key_iter = iter(saved_accounts)
        # create a list for all the account names without 'All'
        filtered_account_list = []
        # create a list for all the account names
        account_list = ['All']
        # append all account names into account_list
        for i in range(0,len(saved_accounts)):
            name = next(key_iter)
            account_list.append(name)
            filtered_account_list.append(name)

        # --------- FrontEnd --------- #    
        st.title("🗃️ Record Archive")
        # Get the filter options from the user
        filter_check = st.checkbox("Do you want to apply filters?")
        col1,col2 = st.columns(2)
        # create a dictionary to keep track of all filters applied
        filters = {}
        # if user chooses to filter
        if filter_check:
            # filter by date
            date_filter = col1.date_input("Search by date", key='date')
            if date_filter:
                filters['date'] = date_filter

            # filter by account name
            account_filter = col2.selectbox("Filter by account", account_list, key='account')
            if account_filter != "All":
                filters['account'] = account_filter

            # filter by type of record
            type_filter = col1.selectbox("Filter by type", ["All", "Expense", "Income"], key='type')
            if type_filter != "All":
                filters['type'] = type_filter

            # filter by category of record
            category_filter = col2.selectbox("Filter by category", ["All", '❓ Others','🍔 Food & Drinks', '🛒 Shopping','🏚️ Housing','🚌 Transportation','🚗 Vehicle','💃 Life & Entertainment','📺 Communication & TV', '💳 Financial expense','💲 Investments','💸 Income'], key='category')
            if category_filter != "All":
                filters['category'] = category_filter
        
        #create a query to search for the user logged in
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

        # find all records for user according to filter and sort according to date
        cursor = record_col.find(query,{}).sort("Date", pymongo.DESCENDING)
        
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
                # Display the records with date as heading for filtered record
                for date, records in grouped_records.items():
                    if(date==str(date_filter)):
                        st.header(f"{date}")
                        for record in records:
                            # create a filtered record with _id and Username excluded for the display
                            filtered_record = {key:value for key,value in record.items() if key not in ['_id','Username']}
                            with st.expander(f"{record['Category']} - {record['Comments']}"):
                                st.write(filtered_record)
                # display the following if no records exist for the searched date
                if(str(date_filter) not in grouped_records.keys()):
                    st.info("You have no records for this date", icon="🤖")
            else:
                # Display the records with date as heading
                for date, records in grouped_records.items():
                    st.header(f"{date}")
                    for record in records:
                        # create a filtered record with _id and Username excluded for the display
                        filtered_record = {key:value for key,value in record.items() if key not in ['_id','Username']}
                        with st.expander(f"{record['Category']} - {record['Comments']}"):
                            st.write(filtered_record)


        else:
            # Display if no records exist
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
    
    # if Edit Record selected in Menubar
    elif selected == 'Edit Record':
        # retrieve all the accounts of user
        saved_accounts = accounts_col.find({'Username':get_username()[0]})[0]['Accounts']
        # iterate through the account name
        key_iter = iter(saved_accounts)
        # create a list for all the account names without 'All'
        filtered_account_list = []
        # append all account names into account_list
        for i in range(0,len(saved_accounts)):
            name = next(key_iter)
            filtered_account_list.append(name)

        st.title("📝 Edit Past Record")
        st.divider()
        # create a new list to store records
        record_list = ['Select record']
        # take user input for date of record to be edited
        edit_date = st.date_input("Which date does the record belong to?")
        # filter the records available for that date
        cursor = record_col.find({'Username': get_username()[0],'Date':str(edit_date)})
        records = list(cursor)
        # if records exist for that date
        if records:
            for record in records:
                # append all records to record_list
                record_list.append(f"{record['Category']} - {record['Comments']}")
            # take user input for record to edit
            selected_edit_record = st.selectbox("Which record do you wish to edit?",record_list)
            if selected_edit_record!='Select record':
                # find the record in mongodb and store in selected_record
                selected_record = record_col.find_one({'Username': get_username()[0], 'Date': str(edit_date), 'Category': selected_edit_record.split(' - ')[0], 'Comments': selected_edit_record.split(' - ')[1]})
                # save the account name before edit (incase the account is changed, balance will have to change) 
                old_account = selected_record['Account']
                # save the record type before edit (incase the type is changed, balance will have to change) 
                old_type = selected_record['Type']
                sign_col1,sign_col2 = st.columns(2)
                # take user inputs
                record_type = sign_col1.selectbox("Pick type of record",["Income","Expense"],index=(0 if selected_record['Type']=='Income' else 1))
                date = sign_col2.date_input(f"Date of {record_type}",value=dt.strptime(selected_record['Date'], '%Y-%m-%d'))
                amount = sign_col1.number_input('Amount',value=selected_record['Amount'])
                category = sign_col2.selectbox('Category',categories_list,index=categories_list.index(selected_record['Category']))
                account = sign_col1.selectbox("Select the account",filtered_account_list,index=filtered_account_list.index(selected_record['Account']))
                if category=='❓ Others':
                    other_cat = sign_col2.text_input("Enter the custom category",value=selected_record['Category Description'])
                comments = st.text_area("Any comments?",placeholder="Spent on food at the store near school",value=selected_record['Comments'])
                update = st.button("Update Record",type='primary',use_container_width=True)

                # if update record button is clicked
                if update:
                    # update the record in database
                    if category=='❓ Others':
                        record_col.update_one({'Username': get_username()[0],'_id':selected_record['_id']},{'$set':{'Date':str(date),'Type':record_type,'Category':category,'Category Description':other_cat,'Account':account,'Amount':amount,'Comments':comments}})
                    else:
                        record_col.update_one({'Username': get_username()[0],'_id':selected_record['_id']},{'$set':{'Date':str(date),'Type':record_type,'Category':category,'Account':account,'Amount':amount,'Comments':comments}})
                    # save the account name after edit (incase the account is changed, balance will have to change) 
                    new_account = selected_record['Account']
                    # save the record type after edit (incase the type is changed, balance will have to change) 
                    new_type = selected_record['Type']
                    # get list of all accounts of user
                    edit_saved_accounts = accounts_col.find({'Username':get_username()[0]})[0]['Accounts']

                    # compare accounts to check if account is changed
                    if old_account!=new_account and old_type==new_type:
                        # if record type is Expense
                        if selected_record['Type']=='Expense':
                            edit_saved_accounts[old_account] += amount
                            edit_saved_accounts[new_account] -= amount

                        # if record type is Income
                        elif selected_record['Type']=='Income':
                            edit_saved_accounts[old_account] -= amount
                            edit_saved_accounts[new_account] += amount

                    # compare types to check if type is changed
                    elif old_account==new_account and old_type!=new_type:
                        # if record type is Expense
                        if new_type=='Expense':
                            edit_saved_accounts[new_account] -= (2*amount)
                        # if record type is Income
                        elif new_type=='Income':
                            edit_saved_accounts[new_account] += (2*amount)
                    
                    # compare accounts and types to check if both have changed is changed
                    elif old_account!=new_account and old_type!=new_type:
                        # if record type is Expense
                        if new_type=='Expense':
                            edit_saved_accounts[old_account] -= amount
                            edit_saved_accounts[new_account] -= amount

                        # if record type is Income
                        elif new_type=='Income':
                            edit_saved_accounts[old_account] += amount
                            edit_saved_accounts[new_account] += amount

                        
                    # update the accounts collection with new amounts
                    accounts_col.update_one({'Username':get_username()[0]},{'$set':{'Accounts':edit_saved_accounts}})
                    st.success("Record Successfully Updated",icon='✅')

                    st.experimental_rerun()

        else:
            st.info("You have no records for this date", icon="🤖")


    # If Bills is selected in Menubar
    elif selected == 'Bills':
        st.title("📆 Remind My Bills")
        st.divider()
        sign_col1,sign_col2 = st.columns(2)

        # take user input
        due_date = sign_col1.date_input("Due Date of Bill",min_value=dt.now().date())
        category = sign_col2.selectbox('Category',categories_list,index=1)
        amount = sign_col1.number_input('Amount')
        if category=='❓ Others':
            other_cat = sign_col2.text_input("Enter the custom category")
        repeating = sign_col1.checkbox('This is a Recurring Bill')
        if repeating:
            reminder = sign_col2.selectbox("Remind Me", ('Monthly','Yearly'))
        else:
            reminder = 'NA'
        comments = st.text_area("Any comments?",placeholder="Need to pay the Electricity bill")
        submit = st.button("Submit Bill",type='primary',use_container_width=True)

        #if submit button is clicked, do the following
        if submit:
            if(amount==0.00):
                st.error('Please enter a non-zero amount!', icon="🚨")
            else:
                # if category is not others, add bill data as is
                if(category!='❓ Others'):
                    bills_col.insert_one({'Username':get_username()[0],'Due Date':str(due_date),'Category':category,'Amount':amount,'Remind':reminder,'Comments':comments})
                
                # else add bill data with category description
                else:
                    bills_col.insert_one({'Username':get_username()[0],'Due Date':str(due_date),'Category':category,'Category Description':other_cat,'Amount':amount,'Remind':reminder,'Comments':comments})

        st.divider()
        st.title("📆 Upcoming Bills")
        st.divider()

        #create a query to search for the user logged in
        query = {'Username': get_username()[0]}

        #hide _id and username from display data
        projection = {}
        # projection = {"_id": 0, 'Username': 0}
        
        # find all bills for user but sorted according to due date
        cursor = bills_col.find(query, projection).sort("Due Date", pymongo.ASCENDING)
        bills = list(cursor)

        # find today's date
        current_date = dt.now().date()
                
       # if bills exist for user
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
                # if the due date is crossed
                if days_left < 0:
                    for bill in bills_list:
                        # Check for bills with "Monthly" or "Yearly" reminder and create a new bill for the next month/year
                        if bill["Remind"] == "Monthly" or bill["Remind"] == "Yearly":
                            create_next_bill(bill,bills_col)

                        # Delete the bills with 0 days left from the collection
                        bills_col.delete_one({"_id": bill["_id"]})
                st.header(f"{days_left} Days left for")
                for bill in bills_list:
                    # create a filtered bill with _id and Username excluded for the display
                    filtered_bill = {key:value for key,value in bill.items() if key not in ['_id','Username']}
                    with st.expander(f"{bill['Category']} - {bill['Comments']}"):
                        st.write(filtered_bill)
        else:
            st.info("You have no bills due", icon="💡")

    # if Dashboard selected in Menubar
    elif selected == 'Dashboard':
        st.title("📈 Review Time")
        st.divider()
        st.subheader("Income vs. Expense")
        chart_data = pd.DataFrame(
        np.random.randn(20, 2),columns=['Income', 'Expense'])

        st.line_chart(chart_data)
    
    # If Settings is selected in Menubar
    elif selected == 'Settings':
        st.title("User Details")
        sign_col1, sign_col2 = st.columns(2)

        # display the user details but also allow edits
        first_name = sign_col1.text_input("First name",value=user_col.find({'Email':get_username()[0]})[0]['First Name'])
        last_name = sign_col2.text_input("Last name",value=user_col.find({'Email':get_username()[0]})[0]['Last Name'])
        dob = st.date_input("When's your birthday",)
        email = st.text_input("Email ID", value=user_col.find({'Email':get_username()[0]})[0]['Email'],disabled=True)
        password = st.text_input("Change Password",type='password',value=login_col.find({'Username':get_username()[0]})[0]['Password'])
        
        # create a dictionary for account_name:account_balance pair
        bank_accounts = {}
        # create a list for all account names
        account_list = []
        # retrieve all saved accounts from the collection for that user
        saved_accounts = accounts_col.find({'Username':get_username()[0]})[0]['Accounts']
        # ask/set the number of accounts the user has
        num_accounts = st.number_input("Number of Accounts to Add", min_value=1, value=(len(saved_accounts) or 1))
        # iterate through all the account names
        key_iter = iter(saved_accounts)
        # iterate through all the account balances
        val_iter = iter(saved_accounts.values())
        # for the number of accounts the user has
        for i in range(1,num_accounts+1):
            # call add_account to create a new account input in frontend
            acc_name, acc_bal = add_account(i,next(key_iter, None),next(val_iter, None))
            # append the account details pair to bank_accounts
            bank_accounts[acc_name] = acc_bal
            # append the account name to account_list
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

        #if the submit button is clicked, do the following
        if submitted:
            # update the user details in user collection
            user_col.update_one({'Email':get_username()[0]},{'$set':{'First Name':first_name,'Last Name':last_name, 'DOB':str(dob),'Email':email,'Accounts':account_list}})
            # update the login details of user in login collection
            login_col.update_one({'Username':get_username()[0]},{'$set':{'Username':email,'Password':password}})
            # update the account details in accounts collection
            accounts_col.update_one({'Username':get_username()[0]},{'$set':{'Accounts':bank_accounts}})



if __name__ == "__main__":
    main()
