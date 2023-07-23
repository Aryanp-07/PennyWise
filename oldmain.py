import streamlit as st
import webbrowser
st.set_page_config("PennyWise", ":moneybag:",initial_sidebar_state="collapsed")
st.markdown(
    """
<style>
    div[data-testid="collapsedControl"] {
        display: none;
    }
</style>
""",
    unsafe_allow_html=True,
)
st.title('PennyWise :moneybag:')
st.header("Your Personal Finance Tracker")
st.divider()

# col1,col2 = st.columns(2)
# with col1:
#     st.subheader("Sign Up")
#     sign_col1,sign_col2 = st.columns(2)
#     first_name = sign_col1.text_input("First name")
#     last_name = sign_col2.text_input("Last name")
#     signup = st.button("Sign Up")
    

# with col2:
#     st.subheader("Login")
#     username = st.text_input('Username')
#     password = st.text_input('Password',type='password')
#     submit = st.button("Submit")



with st.form("login_form"):
   st.subheader("Login")
   username = st.text_input('Username')
   password = st.text_input('Password',type='password')

   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
       st.write("Thank You")   
    #    webbrowser.open("http://localhost:8501/")
       
st.divider()
my_expander = st.expander("Don't have an account?")
my_expander.subheader("Sign Up")
with my_expander:
    sign_col1,sign_col2 = st.columns(2)
    first_name = sign_col1.text_input("First name")
    last_name = sign_col2.text_input("Last name")
    sign_username = st.text_input('Set Username')
    sign_password = st.text_input('Set Password',type='password')
    signup = st.button("Sign Up")
    if signup:
        st.balloons()







