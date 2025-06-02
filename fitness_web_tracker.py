import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

NUTRITION_LOG = os.path.join(DATA_DIR, "nutrition_data.csv")

# Load nutrition data
def load_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["Date"])
    return pd.DataFrame(columns=columns)

nutrition_df = load_csv(NUTRITION_LOG, ["Date", "Meal", "Protein", "Carbs", "Fats", "Calories"])

# Calculate totals
totals = nutrition_df[["Protein", "Carbs", "Fats", "Calories"]].sum()

# Display goals and totals
st.subheader("🥗 Daily Nutrition Goals")
col1, col2 = st.columns(2)

with col1:
    st.metric("Calories", f"{totals['Calories']:.0f} / 1424 kcal")
    st.metric("Protein", f"{totals['Protein']:.0f} / 142 g")
with col2:
    st.metric("Carbs", f"{totals['Carbs']:.0f} / 107 g")
    st.metric("Fats", f"{totals['Fats']:.0f} / 47 g")

# File paths
NUTRITION_LOG = os.path.join(DATA_DIR, "nutrition_log.csv")
WORKOUT_LOG = os.path.join(DATA_DIR, "workout_log.csv")
WATER_LOG = os.path.join(DATA_DIR, "water_log.csv")
SLEEP_LOG = os.path.join(DATA_DIR, "sleep_log.csv")

# Load logs
def load_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["Date"])
    return pd.DataFrame(columns=columns)

# Nutrition
nutrition_df = load_csv(NUTRITION_LOG, ["Date", "Meal", "Protein", "Carbs", "Fats", "Calories"])
# Workout
workout_df = load_csv(WORKOUT_LOG, ["Date", "Exercise", "Weight", "Reps", "Sets", "Volume"])
# Water
water_df = load_csv(WATER_LOG, ["Date", "Ounces"])
# Sleep
sleep_df = load_csv(SLEEP_LOG, ["Date", "Hours"])

# Streamlit App
st.set_page_config(page_title="Fitness Tracker", layout="centered")
st.title("🏋️‍♂️ Fitness Tracker")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Nutrition", "Workout Tracker", "Water", "Sleep", "Progress"])

with tab1:
    st.header("🥗 Nutrition Log")
    meal = st.text_input("Meal Description")
    protein = st.number_input("Protein (g)", min_value=0)
    carbs = st.number_input("Carbs (g)", min_value=0)
    fats = st.number_input("Fats (g)", min_value=0)
    calories = st.number_input("Calories", min_value=0)

    if st.button("Log Meal"):
        new_entry = {
            "Date": datetime.now(),
            "Meal": meal,
            "Protein": protein,
            "Carbs": carbs,
            "Fats": fats,
            "Calories": calories
        }
        nutrition_df = pd.concat([nutrition_df, pd.DataFrame([new_entry])], ignore_index=True)
        nutrition_df.to_csv(NUTRITION_LOG, index=False)
        st.success("Meal logged!")

    st.subheader("Meal History")
    st.dataframe(nutrition_df.tail(10))

with tab2:
    st.header("🏋️ Log Workout")
    exercise = st.text_input("Exercise")
    sets = st.number_input("Sets", min_value=1, value=1)
    reps = st.number_input("Reps", min_value=1, value=1)
    weight = st.number_input("Weight (lbs)", min_value=0.0, value=0.0)
    volume = sets * reps * weight

    if st.button("Log Workout"):
        new_entry = {
            "Date": datetime.now(),
            "Exercise": exercise,
            "Weight": weight,
            "Reps": reps,
            "Sets": sets,
            "Volume": volume
        }
        workout_df = pd.concat([workout_df, pd.DataFrame([new_entry])], ignore_index=True)
        workout_df.to_csv(WORKOUT_LOG, index=False)
        st.success("Workout logged!")

    st.subheader("Workout History")
    st.dataframe(workout_df.tail(10))

with tab3:
    st.header("💧 Water Intake")
    ounces = st.number_input("Ounces", min_value=0)

    if st.button("Log Water"):
        new_entry = {
            "Date": datetime.now(),
            "Ounces": ounces
        }
        water_df = pd.concat([water_df, pd.DataFrame([new_entry])], ignore_index=True)
        water_df.to_csv(WATER_LOG, index=False)
        st.success("Water logged!")

    st.subheader("Water History")
    st.dataframe(water_df.tail(10))

with tab4:
    st.header("😴 Sleep Log")
    hours = st.number_input("Hours Slept", min_value=0.0, value=0.0)

    if st.button("Log Sleep"):
        new_entry = {
            "Date": datetime.now(),
            "Hours": hours
        }
        sleep_df = pd.concat([sleep_df, pd.DataFrame([new_entry])], ignore_index=True)
        sleep_df.to_csv(SLEEP_LOG, index=False)
        st.success("Sleep logged!")

    st.subheader("Sleep History")
    st.dataframe(sleep_df.tail(10))

with tab5:
    st.header("📈 Progress Charts")

    if not workout_df.empty:
        st.subheader("Workout Volume Over Time")
        chart = workout_df.groupby(workout_df["Date"].dt.date)["Volume"].sum()
        st.line_chart(chart)

    if not nutrition_df.empty:
        st.subheader("Calories Over Time")
        cal_chart = nutrition_df.groupby(nutrition_df["Date"].dt.date)["Calories"].sum()
        st.line_chart(cal_chart)

    if not sleep_df.empty:
        st.subheader("Sleep Duration Over Time")
        sleep_chart = sleep_df.groupby(sleep_df["Date"].dt.date)["Hours"].sum()
        st.line_chart(sleep_chart)

