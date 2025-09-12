🌍 WellBot – A Wellness Chatbot

WellBot is an AI-powered Wellness Chatbot built as part of the Infosys Springboard Virtual Internship.
It evolves across two milestones:

Milestone 1: Authentication + Profile Management

Milestone 2: Conversational AI Core (Intent Recognition, Dialogue Management, Knowledge Base, Chat History)

🚀 Milestone 1 – User Authentication & Profile Management
📌 Features

✅ User Registration & Login using FastAPI backend

✅ Password Encryption with bcrypt

✅ Profile Management (Name, Age Group, Language) stored in SQLite

✅ Streamlit Frontend for easy interaction

✅ Feedback messages for user actions (success/error)

🛠️ Tech Stack

Frontend: Streamlit

Backend: FastAPI

Database: SQLite

Security: bcrypt for password hashing

📂 Files

app.py → Streamlit frontend (Home, Login, Register)

backend.py → FastAPI backend (Register, Login, Profile management)

users.db → SQLite database

🤖 Milestone 2 – Conversational AI Core
📌 Features

✅ Intent Recognition → Detects user queries (greetings, stress, diet, exercise, meditation, etc.)

✅ Dialogue Management → Maintains context and generates appropriate responses

✅ Knowledge Base Integration → Provides global wellness information

✅ Chat History Storage → Saves conversations (username, query, response, timestamp) in SQLite

✅ Personalized Guidance based on past conversations

🛠️ Tech Stack

Frontend: Streamlit

Backend: FastAPI

Database: SQLite (extended with chat_history table)

AI/NLP: Simple intent classification (keyword/rule-based or ML model)

Knowledge Source: JSON/Dictionary wellness dataset
