import pandas as pd
import os
import streamlit as st
from textblob import TextBlob

# --- Helper Functions ---

# Function to load or create a user database (CSV file)
def load_user_data():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    else:
        return pd.DataFrame(columns=["User", "Age", "Dietary_Goals", "Favorite_Foods", "Avoid_Foods", "Average_Satisfaction"])

# Function to save user data (preferences, goals, etc.)
def save_user_data(user_name, dietary_goals, favorite_foods, avoid_foods, satisfaction):
    # Load existing user data
    user_data = load_user_data()

    # Check if the user already exists in the database
    if user_name in user_data["User"].values:
        user_data.loc[user_data["User"] == user_name, "Dietary_Goals"] = dietary_goals
        user_data.loc[user_data["User"] == user_name, "Favorite_Foods"] = favorite_foods
        user_data.loc[user_data["User"] == user_name, "Avoid_Foods"] = avoid_foods
        user_data.loc[user_data["User"] == user_name, "Average_Satisfaction"] = satisfaction
    else:
        # Add new user to the database
        new_user = pd.DataFrame([{
            "User": user_name,
            "Dietary_Goals": dietary_goals,
            "Favorite_Foods": favorite_foods,
            "Avoid_Foods": avoid_foods,
            "Average_Satisfaction": satisfaction
        }])
        user_data = pd.concat([user_data, new_user], ignore_index=True)

    # Save back to CSV
    user_data.to_csv("users.csv", index=False)

# Function to get user preferences
def get_user_preferences(user_name):
    user_data = load_user_data()
    user_info = user_data[user_data["User"] == user_name]
    if not user_info.empty:
        return user_info.iloc[0]
    else:
        return None

# Function to analyze and adjust recommendations based on user preferences
def personalize_recommendations(nutrition, user_name):
    user_preferences = get_user_preferences(user_name)

    if user_preferences is None:
        return "User not found, please set your preferences first."

    dietary_goals = user_preferences["Dietary_Goals"]
    favorite_foods = user_preferences["Favorite_Foods"].split(",")
    avoid_foods = user_preferences["Avoid_Foods"].split(",")

    # Example of adjusting recommendations
    advice = []

    if nutrition["Food"] in favorite_foods:
        advice.append("👍 Great choice! This food aligns with your favorites.")
    
    if any(food in nutrition["Food"] for food in avoid_foods):
        advice.append("⚠️ You might want to avoid this food based on your preferences.")
    
    if "weight_loss" in dietary_goals and nutrition["Calories"] > 500:
        advice.append("⚠️ High in calories. Consider a lighter option if you're focused on weight loss.")
    
    if "high_protein" in dietary_goals and nutrition["Proteins (g)"] < 20:
        advice.append("💪 Consider adding more protein to your diet for muscle maintenance.")
    
    return advice

# --- Streamlit App Setup ---
st.set_page_config(page_title="Smart Food Analyzer", layout="wide")

# --- Sidebar Navigation ---
st.sidebar.title("🍽️ Navigation")
page = st.sidebar.radio("Go to", ["Analyze Food", "Give Feedback", "Set Preferences"])
st.session_state.page = "analyze" if page == "Analyze Food" else "feedback" if page == "Give Feedback" else "preferences"

# --- Set Preferences Page ---
if st.session_state.page == "preferences":
    st.title("📝 Set Your Preferences")

    user_name = st.text_input("👤 Your Name")
    dietary_goals = st.multiselect("🎯 Your Dietary Goals", ["Weight Loss", "High Protein", "Diabetes Management", "Heart Health"])
    favorite_foods = st.text_input("🍽️ Your Favorite Foods (comma-separated)")
    avoid_foods = st.text_input("❌ Foods You Want to Avoid (comma-separated)")

    if st.button("Save Preferences"):
        save_user_data(user_name, dietary_goals, favorite_foods, avoid_foods, satisfaction=5)
        st.success("✅ Your preferences have been saved!")

# --- Analyze Food Page ---
if st.session_state.page == "analyze":
    st.title("🍴 Smart Food Analyzer")

    uploaded_file = st.file_uploader("Upload a food image (or skip to use prompt):", type=["jpg", "jpeg", "png"])
    image = None
    input_text = st.text_input("Input prompt (e.g., 'I have diabetes, suggest meals')")

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    user_name = st.text_input("Enter Your Name")

    if st.button("✨ Analyze Food"):
        if image:
            with st.spinner('Detecting food from image...'):
                food_name = detect_food_name(image)
            st.success(f"🍽️ Detected Food: **{food_name}**")

            # Allow user to edit food name
            food_name = st.text_input("📝 Confirm or edit the food name:", value=food_name)

            with st.spinner('Fetching nutrition information...'):
                nutrition = get_nutrition_info(food_name)

            if nutrition:
                st.subheader("🥗 Nutrition Facts:")
                for key, value in nutrition.items():
                    st.write(f"**{key}**: {value}")

                recommendations = personalize_recommendations(nutrition, user_name)
                for rec in recommendations:
                    st.info(rec)

# --- Feedback Page ---
elif st.session_state.page == "feedback":
    st.title("📝 Share Your Feedback")

    user_name = st.text_input("Enter Your Name")
    satisfaction = st.slider("⭐ Rate Your Satisfaction (1 - 10)", 1, 10, 5)
    comment = st.text_area("🖋️ Your Comment")

    if st.button("✅ Submit Feedback"):
        if user_name and comment:
            save_feedback(user_name, user_name, satisfaction, comment)
            st.success("🎉 Thanks for your feedback!")
        else:
            st.error("⚠️ Please fill in both Name and Comment.")


