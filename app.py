import streamlit as st
import requests
import random
import time
import pandas as pd

API_URL = "http://127.0.0.1:8000"

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- Sidebar Navigation ---
params = st.query_params
default_choice = params.get("choice", "Home")
st.title("🌍 WellBot Menu")
menu = ["Home", "Login", "Register", "Profile", "Dashboard"]
choice = st.sidebar.selectbox("Navigate", menu, index=menu.index(default_choice))

# --- Home Page ---
if choice == "Home":
    st.markdown("""
    ## Welcome to **WellBot** 🤖💬 — your AI-powered wellness companion.  
    - ✅ Register an account to get started  
    - 🔑 Login to continue your wellness journey  
    """)
    st.image("https://img.freepik.com/free-vector/chatbot-concept-illustration_114360-5522.jpg", use_container_width=True)

# --- Login Page ---
elif choice == "Login":
    st.subheader("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success("Login successful! Redirecting to Dashboard...")
            st.session_state.logged_in = True
            st.session_state.username = username
            time.sleep(1)
            st.query_params = {"choice": "Dashboard"}
            st.rerun()
        else:
            st.error(response.json()["detail"])

# --- Register Page ---
elif choice == "Register":
    st.subheader("🆕 Register")
    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    if st.button("Register"):
        try:
            r = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
            if r.status_code == 200:
                st.success("Registered successfully! Please complete your profile.")
                st.session_state.username = username
                st.session_state.logged_in = True
                st.session_state.page = "Profile"
            else:
                st.error(r.json().get("detail", "Registration failed"))
        except Exception as e:
            st.error(f"⚠️ Could not connect to server: {e}")

# --- Profile Page ---
elif choice == "Profile":
    if st.session_state.username:
        st.subheader("📝 Profile Setup")
        name = st.text_input("Full Name")
        age = st.selectbox("Age Group", ["Teen", "Adult", "Senior"])
        language = st.selectbox("Preferred Language", ["English", "Hindi"])
        if st.button("Save Profile"):
            try:
                r = requests.post(f"{API_URL}/profile", json={
                    "username": st.session_state.username,
                    "name": name,
                    "age_group": age,
                    "language": language
                })
                if r.status_code == 200:
                    st.success("Profile saved! Redirecting to Dashboard...")
                    st.session_state.page = "Dashboard"
                    st.query_params = {"choice": "Dashboard"}
                    st.rerun()
                else:
                    st.error("Failed to save profile")
            except Exception as e:
                st.error(f"⚠️ Could not connect to server: {e}")
    else:
        st.warning("⚠️ Please login first.")

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
            st.info("No profile found. Please complete your profile.")

        # --- Daily Wellness Tip ---
        st.markdown("### 🌱 Daily Wellness Tip")
        tips = [
            "Take a 5-minute break every hour 🧘",
            "Drink 8 glasses of water today 💧",
            "Go for a short walk 🚶",
            "Practice gratitude 🙏",
            "Limit screen time before bed 🌙"
        ]
        st.success(random.choice(tips))

        tab_choice = st.tabs(["💬 Chat with WellBot", "📊 Admin Dashboard"])

        # --- Chat Tab ---
        with tab_choice[0]:
            st.markdown("### 💬 Chat with WellBot")

            for idx, chat in enumerate(st.session_state.chat_history):
                if chat["role"] == "user":
                    with st.chat_message("user"):
                        st.write(chat["content"])
                else:  # assistant
                    container = st.container()
                    with container:
                        with st.chat_message("assistant"):
                            st.write(chat["content"])

                        # Feedback buttons
                        col1, col2 = st.columns([1, 1])
                        feedback_submitted = False

                        with col1:
                            if st.button("👍", key=f"up_{idx}"):
                                feedback_data = {
                                    "user_id": st.session_state.username,
                                    "question": st.session_state.chat_history[idx-1]["content"] if idx > 0 else "",
                                    "answer": chat["content"],
                                    "rating": 1,
                                    "comment": ""
                                }
                                requests.post(f"{API_URL}/feedback", json=feedback_data)
                                st.success("Thanks for your feedback 👍")
                                feedback_submitted = True

                        with col2:
                            if st.button("👎", key=f"down_{idx}"):
                                feedback_data = {
                                    "user_id": st.session_state.username,
                                    "question": st.session_state.chat_history[idx-1]["content"] if idx > 0 else "",
                                    "answer": chat["content"],
                                    "rating": 0,
                                    "comment": ""
                                }
                                requests.post(f"{API_URL}/feedback", json=feedback_data)
                                st.warning("Thanks for your feedback 👎")
                                feedback_submitted = True

                        # Optional comment
                        comment_key = f"comment_{idx}"
                        comment = st.text_input("Add a comment (optional)", key=comment_key)
                        if st.button("Submit Comment", key=f"submit_comment_{idx}") and comment.strip():
                            requests.post(f"{API_URL}/feedback", json={
                                "user_id": st.session_state.username,
                                "question": st.session_state.chat_history[idx-1]["content"] if idx > 0 else "",
                                "answer": chat["content"],
                                "rating": None,
                                "comment": comment.strip()
                            })
                            st.info("Comment submitted!")
                            st.session_state[f"{comment_key}_submitted"] = True

                        if feedback_submitted or st.session_state.get(f"{comment_key}_submitted", False):
                            col1.empty()
                            col2.empty()

            user_input = st.chat_input("Type your message...")
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                try:
                    response = requests.post(f"{API_URL}/chat", json={
                        "user_id": st.session_state.username,
                        "message": user_input
                    })
                    if response.status_code == 200:
                        data = response.json()
                        bot_reply = data.get("bot", "⚠️ No reply from server.")
                        predicted_illness = data.get("predicted_illness")
                        if predicted_illness:
                            bot_reply += f"\n\n**Possible illnesses:** {predicted_illness}"
                    else:
                        bot_reply = f"⚠️ Error: {response.status_code} - {response.text}"
                except Exception as e:
                    bot_reply = f"❌ Could not connect to backend: {e}"

                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                st.rerun()

        # --- Admin Dashboard Tab ---
        with tab_choice[1]:
            st.markdown("### 🛠 Admin Dashboard")
            admin_tabs = st.tabs(["📊 Analytics", "📝 Knowledge Base"])

            # --- Analytics ---
            with admin_tabs[0]:
                st.subheader("📊 Analytics")
                try:
                    analytics_resp = requests.get(f"{API_URL}/analytics")
                    if analytics_resp.status_code == 200:
                        analytics = analytics_resp.json()
                        st.metric("Total Queries", analytics.get("total_queries", 0))
                        st.metric("Failed Queries", analytics.get("failed_queries", 0))
                        st.metric("Feedback % 👍", analytics.get("feedback_percentage", 0))

                        # --- Graph 1: Total vs Failed Queries ---
                        df_total_failed = pd.DataFrame({
                            "Queries": ["Total", "Failed"],
                            "Count": [analytics.get("total_queries", 0), analytics.get("failed_queries", 0)]
                        })
                        st.bar_chart(df_total_failed.set_index("Queries"))

                        # --- Graph 2: Daily Queries Trend ---
                        daily_queries = analytics.get("daily_queries", {})  
                        if daily_queries:
                            df_daily = pd.DataFrame(list(daily_queries.items()), columns=["Date", "Queries"])
                            df_daily["Date"] = pd.to_datetime(df_daily["Date"])
                            df_daily = df_daily.sort_values("Date")
                            st.line_chart(df_daily.set_index("Date"))

                        # --- Graph 3: Feedback Breakdown ---
                        positive = analytics.get("positive_feedback", 0)
                        negative = analytics.get("negative_feedback", 0)
                        if positive + negative > 0:
                            df_feedback = pd.DataFrame({
                                "Feedback": ["👍 Positive", "👎 Negative"],
                                "Count": [positive, negative]
                            })
                            st.bar_chart(df_feedback.set_index("Feedback"))

                        # --- Graph 4: Common Failed Queries ---
                        failed_queries_list = analytics.get("failed_queries_list", [])
                        if failed_queries_list:
                            df_failed = pd.DataFrame(failed_queries_list, columns=["Query"])
                            top_failed = df_failed["Query"].value_counts().head(10)
                            st.bar_chart(top_failed)

                    else:
                        st.info("No analytics data available.")
                except Exception as e:
                    st.warning(f"Error fetching analytics: {e}")

            # --- Knowledge Base ---
            with admin_tabs[1]:
                st.subheader("📝 Knowledge Base")
                kb_resp = requests.get(f"{API_URL}/kb")
                kb_entries = kb_resp.json() if kb_resp.status_code == 200 else []

                st.markdown("#### Existing Entries")
                for entry in kb_entries:
                    st.write(f"**Q:** {entry['question']}")
                    st.write(f"**A:** {entry['answer']}")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"Edit", key=f"edit_{entry['id']}"):
                            new_q = st.text_input(f"Edit Q {entry['id']}", value=entry['question'], key=f"new_q_{entry['id']}")
                            new_a = st.text_input(f"Edit A {entry['id']}", value=entry['answer'], key=f"new_a_{entry['id']}")
                            if st.button(f"Save {entry['id']}", key=f"save_{entry['id']}"):
                                requests.put(f"{API_URL}/kb/{entry['id']}", json={"question": new_q, "answer": new_a})
                                st.success("Updated!")
                    with col2:
                        if st.button(f"Delete", key=f"delete_{entry['id']}"):
                            requests.delete(f"{API_URL}/kb/{entry['id']}")
                            st.warning("Deleted!")

                st.markdown("#### Add New Entry")
                new_question = st.text_input("Question")
                new_answer = st.text_input("Answer")
                if st.button("Add Entry"):
                    requests.post(f"{API_URL}/kb", json={"question": new_question, "answer": new_answer})
                    st.success("Entry added!")

        # --- Logout ---
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.chat_history = []
            st.query_params = {"choice": "Home"}
            st.rerun()

    else:
        st.warning("⚠️ Please login first.")
