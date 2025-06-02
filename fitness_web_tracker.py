import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Fitness Tracker", layout="centered")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

NUTRITION_LOG = os.path.join(DATA_DIR, "nutrition_log.csv")
WORKOUT_LOG = os.path.join(DATA_DIR, "workout_log.csv")
WATER_LOG = os.path.join(DATA_DIR, "water_log.csv")
SLEEP_LOG = os.path.join(DATA_DIR, "sleep_log.csv")

def load_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["Date"])
    return pd.DataFrame(columns=columns)

# Load data
nutrition_df = load_csv(NUTRITION_LOG, ["Date", "Meal", "Protein", "Carbs", "Fats", "Calories"])
workout_df = load_csv(WORKOUT_LOG, ["Date", "Exercise", "Weight", "Reps", "Sets", "Volume"])
water_df = load_csv(WATER_LOG, ["Date", "Ounces"])
sleep_df = load_csv(SLEEP_LOG, ["Date", "Hours"])

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Nutrition", "Workout", "Water", "Sleep", "Progress"])

with tab1:
    st.header("🥗 Nutrition Log")
    with st.form("nutrition_form"):
        meal = st.text_input("Meal Description")
        protein = st.number_input("Protein (g)", min_value=0)
        carbs = st.number_input("Carbs (g)", min_value=0)
        fats = st.number_input("Fats (g)", min_value=0)
        calories = st.number_input("Calories", min_value=0)
        submitted = st.form_submit_button("Log Meal")

        if submitted and meal:
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

    st.subheader("📈 Daily Nutrition Goals")
    goals = {"Calories": 1424, "Protein": 142, "Fats": 47, "Carbs": 107}
    totals = nutrition_df[["Calories", "Protein", "Fats", "Carbs"]].sum()

    for key in goals:
        st.metric(key, f"{int(totals[key])} / {goals[key]} {'kcal' if key == 'Calories' else 'g'}")
        st.progress(min(totals[key] / goals[key], 1.0))

    with st.expander("📋 Edit Nutrition Log"):
        nutrition_edit = st.data_editor(nutrition_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Nutrition Log"):
            nutrition_edit.to_csv(NUTRITION_LOG, index=False)
            st.success("Nutrition log saved.")

with tab2:
    st.header("🏋️ Log Workout")
    preset_exercises = [
        "Chest Press", "Goblet Squat", "Decline Chest Fly", "Incline Chest Fly", "Chest Fly",
        "Tricep Pulldown", "Lat Pulldown", "Pallof Press", "Woodchopper", "Plank Hold",
        "Overhead Press", "Deadlift", "Glute Bridge", "Barbell Row"
    ]
    exercise = st.selectbox("Exercise", preset_exercises)
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

    with st.expander("🏋️‍♀️ Edit Workout Log"):
        workout_edit = st.data_editor(workout_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Workout Log"):
            workout_edit.to_csv(WORKOUT_LOG, index=False)
            st.success("Workout log saved.")

    st.subheader("🏆 Max Weight PRs")
    if not workout_df.empty:
        pr_df = workout_df.groupby("Exercise")["Weight"].max().reset_index()
        pr_df = pr_df.sort_values("Weight", ascending=False)
        st.dataframe(pr_df, use_container_width=True)
    else:
        st.info("No workout data available to calculate PRs.")

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

    with st.expander("Water History"):
        st.dataframe(water_df.tail(10), use_container_width=True)

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

    with st.expander("Sleep History"):
        st.dataframe(sleep_df.tail(10), use_container_width=True)

with tab5:
    st.header("📊 Progress")
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
