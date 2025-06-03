import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_calendar import calendar

# Setup
st.set_page_config(page_title="Fitness Tracker", layout="centered")
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# File paths
NUTRITION_LOG = os.path.join(DATA_DIR, "nutrition_log.csv")
WORKOUT_LOG = os.path.join(DATA_DIR, "workout_log.csv")
WATER_LOG = os.path.join(DATA_DIR, "water_log.csv")
SLEEP_LOG = os.path.join(DATA_DIR, "sleep_log.csv")
PLANNER_LOG = os.path.join(DATA_DIR, "planner_log.csv")

def load_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["Date"])
    return pd.DataFrame(columns=columns)

# Load logs
nutrition_df = load_csv(NUTRITION_LOG, ["Date", "Meal", "Protein", "Carbs", "Fats", "Calories"])
workout_df = load_csv(WORKOUT_LOG, ["Date", "Exercise", "Weight", "Reps", "Sets", "Volume"])
water_df = load_csv(WATER_LOG, ["Date", "Ounces"])
sleep_df = load_csv(SLEEP_LOG, ["Date", "Hours"])
planner_df = load_csv(PLANNER_LOG, ["Date", "Muscle Group", "Workout Plan"])

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Nutrition", "Workout Tracker", "Water", "Sleep", "Progress", "Workout Planner"])

with tab1:
    st.title("🍔 Nutrition Log")
    today = pd.to_datetime(datetime.now().date())
    if not nutrition_df.empty:
        nutrition_df["Date"] = pd.to_datetime(nutrition_df["Date"], errors="coerce")
        nutrition_today_df = nutrition_df[nutrition_df["Date"].dt.normalize() == today]
    else:
        nutrition_today_df = pd.DataFrame(columns=nutrition_df.columns)

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

    st.subheader("📈 Daily Nutrition Goals")
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

    st.subheader("📋 Edit Nutrition Log")
    nutrition_edit = st.data_editor(nutrition_df, num_rows="dynamic", use_container_width=True)
    if st.button("Save Nutrition Log"):
        nutrition_edit.to_csv(NUTRITION_LOG, index=False)
        st.success("Nutrition log saved.")

with tab2:
    st.header("🏋️ Log Workout")
    preset_exercises = [
        "Chest Press", "Goblet Squat", "Decline Chest Fly", "Incline Chest Fly", "Chest Fly",
        "Tricep Pulldown", "Lat Pulldown", "Pallof Press", "Woodchopper", "Plank Hold",
        "Overhead Press", "Deadlift", "Glute Bridge", "Barbell Row", 'Calf Raise", "bench press", " overhead Tricep press", "farmer March"
    ]
    exercise = st.selectbox("Exercise", preset_exercises)
    sets = st.number_input("Sets", min_value=1, value=1)
    reps = st.number_input("Reps", min_value=1, value=1)
    weight = st.number_input("Weight (lbs)", min_value=0, value=0)
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
    st.title("💧 Water Intake")
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
    st.title("😴 Sleep Log")
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
    st.header("📈 Progress")

    # Ensure only the date part is used
    workout_df["Date"] = pd.to_datetime(workout_df["Date"]).dt.date
    nutrition_df["Date"] = pd.to_datetime(nutrition_df["Date"]).dt.date

    if not workout_df.empty:
        st.subheader("Workout Volume by Day")
        volume_by_day = workout_df.groupby("Date")["Volume"].sum()
        volume_by_day.index = volume_by_day.index.astype(str)  # Convert index to string
        st.bar_chart(volume_by_day)

    if not nutrition_df.empty:
        st.subheader("Calories by Day")
        calories_by_day = nutrition_df.groupby("Date")["Calories"].sum()
        calories_by_day.index = calories_by_day.index.astype(str)  # Convert index to string
        st.bar_chart(calories_by_day)



        
with tab6:
    st.title("📅 Workout Planner")
    with st.form("planner_form"):
        planner_date = st.date_input("Select Date")
        muscle_group = st.selectbox("Muscle Group", ["Push", "Pull", "Legs", "Chest", "Back", "Shoulders", "Arms", "Full Body"])
        workout_plan = st.text_area("Planned Workout Details")
        submit_plan = st.form_submit_button("Add to Planner")
        if submit_plan:
            new_plan = {
                "Date": pd.to_datetime(planner_date),
                "Muscle Group": muscle_group,
                "Workout Plan": workout_plan
            }
            planner_df = pd.concat([planner_df, pd.DataFrame([new_plan])], ignore_index=True)
            planner_df.to_csv(PLANNER_LOG, index=False)
            st.success("Workout plan saved!")

    st.subheader("🗓️ Visual Workout Calendar")
    calendar_events = [
        {
            "title": f"{row['Muscle Group']}: {str(row['Workout Plan'])[:30]}..." if pd.notna(row['Workout Plan']) else row['Muscle Group'],
            "start": row["Date"].strftime("%Y-%m-%d"),
            "allDay": True
        }
        for _, row in planner_df.iterrows()
    ]
    calendar_options = {
        "initialView": "dayGridMonth",
        "editable": False,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        }
    }
    calendar(events=calendar_events, options=calendar_options)

