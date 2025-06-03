
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Fitness Tracker", layout="centered")
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# File paths
NUTRITION_LOG = os.path.join(DATA_DIR, "nutrition_log.csv")
WORKOUT_LOG = os.path.join(DATA_DIR, "workout_log.csv")
WATER_LOG = os.path.join(DATA_DIR, "water_log.csv")
SLEEP_LOG = os.path.join(DATA_DIR, "sleep_log.csv")

def load_csv(path, columns):
    if os.path.exists(path):
        df = pd.read_csv(path, parse_dates=["Date"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    return pd.DataFrame(columns=columns)

# Load all logs
nutrition_df = load_csv(NUTRITION_LOG, ["Date", "Meal", "Protein", "Carbs", "Fats", "Calories"])
workout_df = load_csv(WORKOUT_LOG, ["Date", "Exercise", "Weight", "Reps", "Sets", "Volume"])
water_df = load_csv(WATER_LOG, ["Date", "Ounces"])
sleep_df = load_csv(SLEEP_LOG, ["Date", "Hours"])

# Today's date
today = pd.to_datetime(datetime.now().date())

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Nutrition", "Workout Tracker", "Water", "Sleep", "Progress", "Workout Planner"])

# --- NUTRITION TAB ---
with tab1:
    st.title("🍔 Nutrition Log")
    nutrition_today_df = nutrition_df[nutrition_df["Date"].dt.normalize() == today]

    with st.form("nutrition_form"):
        meal = st.text_input("Meal Description")
        protein = st.number_input("Protein (g)", min_value=0)
        carbs = st.number_input("Carbs (g)", min_value=0)
        fats = st.number_input("Fats (g)", min_value=0)
        calories = st.number_input("Calories", min_value=0)
        submitted = st.form_submit_button("Log Meal")

        if submitted and meal:
            new_row = {
                "Date": datetime.now(),
                "Meal": meal,
                "Protein": protein,
                "Carbs": carbs,
                "Fats": fats,
                "Calories": calories
            }
            nutrition_df = pd.concat([nutrition_df, pd.DataFrame([new_row])], ignore_index=True)
            nutrition_df.to_csv(NUTRITION_LOG, index=False)
            st.success("Meal logged!")

    # Progress Bars
    st.subheader("📉 Daily Nutrition Goals")
    goals = {"Calories": 1424, "Protein": 142, "Fats": 47, "Carbs": 107}
    totals = nutrition_today_df[["Calories", "Protein", "Fats", "Carbs"]].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Calories", f"{totals['Calories']:.0f} / {goals['Calories']} kcal")
        st.progress(min(totals['Calories'] / goals["Calories"], 1.0))
        st.metric("Protein", f"{totals['Protein']:.0f} / {goals['Protein']} g")
        st.progress(min(totals['Protein'] / goals["Protein"], 1.0))
    with col2:
        st.metric("Carbs", f"{totals['Carbs']:.0f} / {goals['Carbs']} g")
        st.progress(min(totals['Carbs'] / goals["Carbs"], 1.0))
        st.metric("Fats", f"{totals['Fats']:.0f} / {goals['Fats']} g")
        st.progress(min(totals['Fats'] / goals["Fats"], 1.0))

    # Edit nutrition log
    st.subheader("📋 Edit Nutrition Log")
    nutrition_edit = st.data_editor(nutrition_df, num_rows="dynamic", use_container_width=True)
    if st.button("Save Nutrition Log"):
        nutrition_edit.to_csv(NUTRITION_LOG, index=False)
        st.success("Nutrition log saved.")

# --- WORKOUT TAB ---
with tab2:
    st.header("🏋️ Log Workout")
    preset_exercises = [
        "Chest Press", "Goblet Squat", "Declined Chest Fly", "Incline Chest Fly", "Chest Fly",
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

    st.subheader("Workout History")
    st.dataframe(workout_df.tail(10))

    st.subheader("🛠 Edit Workout Log")
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

# --- WATER TAB ---
with tab3:
    st.header("💧 Water Intake")
    ounces = st.number_input("Ounces", min_value=0)
    if st.button("Log Water"):
        new_entry = {"Date": datetime.now(), "Ounces": ounces}
        water_df = pd.concat([water_df, pd.DataFrame([new_entry])], ignore_index=True)
        water_df.to_csv(WATER_LOG, index=False)
        st.success("Water logged!")
    st.subheader("Water History")
    st.dataframe(water_df.tail(10))

# --- SLEEP TAB ---
with tab4:
    st.header("😴 Sleep Log")
    hours = st.number_input("Hours Slept", min_value=0.0, value=0.0)
    if st.button("Log Sleep"):
        new_entry = {"Date": datetime.now(), "Hours": hours}
        sleep_df = pd.concat([sleep_df, pd.DataFrame([new_entry])], ignore_index=True)
        sleep_df.to_csv(SLEEP_LOG, index=False)
        st.success("Sleep logged!")
    st.subheader("Sleep History")
    st.dataframe(sleep_df.tail(10))

# --- PROGRESS TAB ---
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

# --- WORKOUT PLANNER ---
with tab6:
   # --- Workout Planner ---
WORKOUT_PLANNER = os.path.join(DATA_DIR, "workout_planner.csv")

def load_or_create_planner():
    if os.path.exists(WORKOUT_PLANNER):
        return pd.read_csv(WORKOUT_PLANNER, parse_dates=["Date"])
    return pd.DataFrame(columns=["Date", "Muscle Group", "Workout Plan"])

def save_plan_to_csv(df):
    df.to_csv(WORKOUT_PLANNER, index=False)

planner_df = load_or_create_planner()

st.header("📅 Workout Planner")
selected_date = st.date_input("Choose a day", datetime.now().date())
muscle_group = st.selectbox("Muscle Group / Routine", ["Push", "Pull", "Legs", "Chest", "Back", "Arms", "Full Body", "Rest"])
plan = st.text_area("Workout Plan (e.g., exercises, reps, sets)")

if st.button("Save Workout Plan"):
    new_row = {"Date": selected_date, "Muscle Group": muscle_group, "Workout Plan": plan}
    planner_df = pd.concat([planner_df, pd.DataFrame([new_row])], ignore_index=True)
    save_plan_to_csv(planner_df)
    st.success("Workout plan saved!")

st.subheader("📖 Planned Workouts")
if not planner_df.empty:
    st.dataframe(planner_df.sort_values("Date"), use_container_width=True)
else:
    st.info("No planned workouts yet.")
