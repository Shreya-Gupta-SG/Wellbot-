import streamlit as st
import requests
import time
import random

API_URL = "http://127.0.0.1:8000"

# --- Session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Handle query params for navigation ---
params = st.query_params
if "choice" in params:
    default_choice = params["choice"]
else:
    default_choice = "Home"

# --- Sidebar Menu ---
st.title("🌍 WellBot Menu")
menu = ["Home", "Login", "Register", "Profile", "Dashboard"]
choice = st.sidebar.selectbox("Navigate", menu, index=menu.index(default_choice))

# --- Home Page ---
if choice == "Home":
    st.title("Global Wellness Chatbot")
    st.markdown(
        """
        Welcome to **WellBot** 🤖💬 — your AI-powered wellness companion.  
        - ✅ Register an account to get started  
        - 🔑 Login to continue your wellness journey  
        """
    )
    st.image(
        "https://img.freepik.com/free-vector/chatbot-concept-illustration_114360-5522.jpg",
        use_container_width=True
    )

# --- Login Page ---
elif choice == "Login":
    st.subheader("🔑 Login to Your Account")
    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if st.button("Login"):
        response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success("Login successful! Redirecting to Dashboard...")
            st.session_state.logged_in = True
            st.session_state.username = username
            time.sleep(1)
            st.query_params = {"choice": "Dashboard"}  # ✅ update query params
            st.rerun()
        else:
            st.error(response.json()["detail"])

# --- Register Page ---
elif choice == "Register":
    st.subheader("🆕 Create a New Account")
    new_user = st.text_input("👤 Username")
    new_password = st.text_input("🔒 Password", type="password")

    if st.button("Register"):
        response = requests.post(f"{API_URL}/register", json={"username": new_user, "password": new_password})
        if response.status_code == 200:
            st.success("Registration successful! Please complete your profile...")
            st.session_state.username = new_user
            time.sleep(1)
            st.query_params = {"choice": "Profile"}  # ✅ redirect to Profile
            st.rerun()
        else:
            st.error(response.json()["detail"])

# --- Profile Page ---
elif choice == "Profile":
    st.subheader("📝 Complete Your Profile")
    if st.session_state.username:
        name = st.text_input("👤 Full Name")
        age_group = st.selectbox("🎂 Age Group", ["Teen", "Adult", "Senior"])
        language = st.selectbox("🌐 Preferred Language", ["English", "Hindi", "Spanish", "French"])

        if st.button("Save Profile"):
            response = requests.post(f"{API_URL}/profile", json={
                "username": st.session_state.username,
                "name": name,
                "age_group": age_group,
                "language": language
            })
            if response.status_code == 200:
                st.success("Profile saved! ")
                time.sleep(1)
                st.query_params = {"choice": "Dashboard"}  # ✅ redirect to Dashboard
                st.rerun()
            else:
                st.error(response.json()["detail"])
    else:
        st.warning("⚠️ Please register or login first.")

# --- Dashboard Page ---
elif choice == "Dashboard":
    if st.session_state.logged_in:
        st.subheader(f"👋 Welcome, {st.session_state.username}!")

        # Fetch profile
        response = requests.get(f"{API_URL}/profile/{st.session_state.username}")
        if response.status_code == 200:
            profile = response.json()
            st.markdown(f"""
            ### Your Profile
            - **Name:** {profile['name']}
            - **Age Group:** {profile['age_group']}
            - **Language:** {profile['language']}
            """)
        else:
            st.info("No profile found. Go to Profile page to complete your details.")

        # Fun Section ✨
        st.markdown("### 🌱 Daily Wellness Tip")
        tips = [
            "Take a 5-minute break every hour 🧘",
            "Drink 8 glasses of water today 💧",
            "Go for a short walk 🚶",
            "Practice gratitude 🙏",
            "Limit screen time before bed 🌙"
        ]
        st.success(random.choice(tips))

        # --- Chatbox Section ---
        st.markdown("### 💬 Chat with WellBot")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.write(chat["content"])

        user_input = st.chat_input("Type your message...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            try:
                # ✅ FIXED: Send user_id + message
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"user_id": st.session_state.username, "message": user_input}
                )
                if response.status_code == 200:
                    bot_reply = response.json().get("response", "⚠️ No reply from server.")
                else:
                    bot_reply = f"⚠️ Error: {response.status_code} - {response.text}"
            except Exception as e:
                bot_reply = f"❌ Could not connect to backend: {e}"

            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
            st.rerun()

        # Logout Button
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.query_params = {"choice": "Home"}
            st.rerun()

    else:
        st.warning("⚠️ Please login first.")

