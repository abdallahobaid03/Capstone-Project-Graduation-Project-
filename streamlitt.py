import streamlit as st
import pandas as pd
import json
import os

# ✅ MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="LOGIN SYSTEM", layout="centered")

# --- Load game feedback data ---
@st.cache_data
def load_game_data():
    df = pd.read_csv("game_feedback_data.csv")
    return df

game_df = load_game_data()

# --- User Data File ---
USER_DATA_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

def signup():
    st.subheader("Sign Up")
    role = st.radio("Are you an Organization or a Gamer/Normal User?", ["Organization", "Gamer/Normal User"])
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if password != confirm:
            st.error("Passwords do not match.")
            return
        users = load_users()
        if email in users:
            st.error("User already exists.")
        else:
            users[email] = {"password": password, "role": role}
            save_users(users)
            st.success("Account created! Please sign in.")
            st.session_state.mode = "login"

def login():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        users = load_users()
        if email in users and users[email]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("Logged in successfully!")
        else:
            st.error("Invalid email or password.")

def forgot_password():
    st.subheader("Forgot Password")
    email = st.text_input("Enter your email to recover password", key="forgot_email")
    if st.button("Recover Password"):
        users = load_users()
        if email in users:
            st.success(f"Your password is: {users[email]['password']}")
        else:
            st.error("Email not found.")

def explorer_section():
    st.title("Explorer")
    st.subheader("Search for .....")
    query = st.text_input("🔍 Search", placeholder="Enter game name")

    if query:
        matched = game_df[game_df["Game Name"].str.lower() == query.lower()]
        if not matched.empty:
            row = matched.iloc[0]
            st.markdown(f"### {row['Game Name']}")
            st.write(row["Game Description"])
            st.markdown(f"**Price:** ${row['Game Price ($)']}")
            st.markdown("### The Summarized Feedback Are:-")

            g = "Positive" if row["Graphics (1=Positive)"] == 1 else "Negative"
            p = "Positive" if row["Price (1=Good)"] == 1 else "Negative"
            s = "Positive" if row["Stability (1=Stable)"] == 1 else "Negative"

            st.markdown(f"- **Graphics:** {g}")
            st.markdown(f"- **Price Sentiment:** {p}")
            st.markdown(f"- **Stability:** {s}")
            st.markdown("### Sample Feedback:")
            st.write(row["Feedback Text"])
        else:
            st.warning("Game not found.")

def show_organization_ui():
    st.sidebar.title("Main")
    section = st.sidebar.radio("", ["Explorer", "Analyzer"])
    st.markdown("<div style='text-align:right; font-weight:bold; color:orange;'>Premium Plan ✅</div>", unsafe_allow_html=True)

    if section == "Explorer":
        explorer_section()

    elif section == "Analyzer":
        st.title("Analyzar")
        st.subheader("Attach your file")
        uploaded_file = st.file_uploader("Only text-based review files", type=["txt", "csv"])
        st.markdown("<p style='color:red;'>Kindly Note:- the file must only contain the textual data</p>", unsafe_allow_html=True)
        if uploaded_file:
            st.success(f"Uploaded file: {uploaded_file.name}")

    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False, "user_email": None}))

def show_user_ui():
    st.markdown("<div style='text-align:right; font-weight:bold; color:gray;'>Standard Plan</div>", unsafe_allow_html=True)
    explorer_section()
    st.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False, "user_email": None}))

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "mode" not in st.session_state:
        st.session_state.mode = "login"
    if "user_email" not in st.session_state:
        st.session_state.user_email = None

    if st.session_state.logged_in:
        users = load_users()
        user_data = users.get(st.session_state.user_email)
        role = user_data.get("role")

        if role == "Organization":
            show_organization_ui()
        else:
            show_user_ui()

    else:
        st.markdown("<h1 style='text-align:center;color:gold;'>LOGIN SYSTEM</h1>", unsafe_allow_html=True)

        if st.session_state.mode == "login":
            login()
            if st.button("Sign Up"):
                st.session_state.mode = "signup"
            if st.button("Forgot Password?"):
                st.session_state.mode = "forgot"

        elif st.session_state.mode == "signup":
            signup()
            if st.button("Back to Login"):
                st.session_state.mode = "login"

        elif st.session_state.mode == "forgot":
            forgot_password()
            if st.button("Back to Login"):
                st.session_state.mode = "login"

if __name__ == "__main__":
    main()
