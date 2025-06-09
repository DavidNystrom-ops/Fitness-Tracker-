import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_calendar import calendar
import shutil

# ✅ MUST be the first Streamlit command
st.set_page_config(page_title="Fitness Tracker", layout="centered")

# Setup
DATA_DIR = "data"
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Backup function
def backup_csv_logs():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for filename in ["nutrition_log.csv", "sleep_log.csv", "water_log.csv", "workout_data.csv"]:
        src = os.path.join(DATA_DIR, filename)
        if os.path.exists(src):
            dst = os.path.join(BACKUP_DIR, f"{timestamp}_{filename}")
            shutil.copy2(src, dst)

# Sidebar backup button
if st.sidebar.button("💾 Backup Logs"):
    backup_csv_logs()
    st.sidebar.success("Logs backed up!")


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

import requests  # ensure this is imported at the top

# USDA API key
USDA_API_KEY = "cTk1ljZeYiYjWyohdwcJrB1I5tnE5IDz665YizO3"

def fetch_usda_nutrition(query):
    """Search USDA for food item and return top match's macros"""
    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": query,
        "pageSize": 1,
        "api_key": USDA_API_KEY
    }
    res = requests.get(search_url, params=params)
    if res.status_code != 200:
        return None
    
    foods = res.json().get("foods", [])
    if not foods:
        return None

    nutrients = {n["nutrientName"]: n["value"] for n in foods[0]["foodNutrients"]}

    return {
        "Protein": round(nutrients.get("Protein", 0)),
        "Carbs": round(nutrients.get("Carbohydrate, by difference", 0)),
        "Fats": round(nutrients.get("Total lipid (fat)", 0)),
        "Calories": round(nutrients.get("Energy", 0))
    }

# Initialize session state for macros
for key in ["protein", "carbs", "fats", "calories"]:
    if key not in st.session_state:
        st.session_state[key] = 0

with tab1:
    st.header("🥗 Nutrition Log")

    # Initialize session state safely
    for key in ["meal", "protein", "carbs", "fats", "calories"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key == "meal" else 0

    today = pd.to_datetime(datetime.now().date())
    nutrition_df["Date"] = pd.to_datetime(nutrition_df["Date"], errors="coerce")
    nutrition_today_df = nutrition_df[nutrition_df["Date"].dt.normalize() == today]
    totals = nutrition_today_df[["Calories", "Protein", "Fats", "Carbs"]].sum()

    # Recent meal history (limit to last 20 unique)
    previous_meals = nutrition_df.dropna(subset=["Meal"])
    recent_entries = (
        previous_meals.sort_values("Date")
        .drop_duplicates(subset=["Meal"], keep="last")
        [["Meal", "Protein", "Carbs", "Fats", "Calories"]]
        .set_index("Meal")
        .to_dict(orient="index")
    )

    # Meal input
    meal = st.text_input("Meal Description", value=st.session_state["meal"], placeholder="e.g. Chicken Breast")
    st.session_state["meal"] = meal

    # USDA lookup
    if st.button("🔍 Search Nutrition Info"):
        result = fetch_usda_nutrition(meal)
        if result:
            st.session_state["protein"] = result["Protein"]
            st.session_state["carbs"] = result["Carbs"]
            st.session_state["fats"] = result["Fats"]
            st.session_state["calories"] = result["Calories"]
            st.toast("✅ Nutrition info loaded!", icon="🍎")
        else:
            st.warning("No nutrition info found. Try a simpler item name.")

    # Macro fields using session state
    st.session_state["protein"] = st.number_input("Protein (g)", min_value=0, value=st.session_state["protein"])
    st.session_state["carbs"] = st.number_input("Carbs (g)", min_value=0, value=st.session_state["carbs"])
    st.session_state["fats"] = st.number_input("Fats (g)", min_value=0, value=st.session_state["fats"])
    st.session_state["calories"] = st.number_input("Calories", min_value=0, value=st.session_state["calories"])

    if st.button("Log Meal"):
        new_entry = {
            "Date": datetime.now(),
            "Meal": st.session_state["meal"],
            "Protein": st.session_state["protein"],
            "Carbs": st.session_state["carbs"],
            "Fats": st.session_state["fats"],
            "Calories": st.session_state["calories"]


with tab2:
    st.header("🏋️ Log Workout")
    preset_exercises = [
        "Standing Chest Press", "Incline Chest Fly", "Chest Fly", "Decline Chest Fly", "Bench press", "Barbell curl", "Tricep Pulldown", "Bicep curl", "Hammer Curl", "Overhead Tricep press",
        "Lat Pulldown", "Seated Overhead Press", "Barbell Row", "Lateral Raise", "Face Pulls", "Upright Row", "Barbell Seated Lat Pulldown", "Pallof Press", "Woodchopper", "Plank Hold", "Farmer March", "Rope crunch", "Resisted Hip Raise", "Goblet Squat", "Deadlift", "Glute Bridge", "Calf Raise",
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
        new_entry = {"Date": datetime.now(), "Ounces": ounces}
        water_df = pd.concat([water_df, pd.DataFrame([new_entry])], ignore_index=True)
        water_df.to_csv(WATER_LOG, index=False)
        st.success("Water logged!")

    st.subheader("📋 Edit Water Log")
    water_edit = st.data_editor(water_df, num_rows="dynamic", use_container_width=True)
    if st.button("Save Water Log"):
        water_edit.to_csv(WATER_LOG, index=False)
        st.success("Water log saved!")

with tab4:
    st.title("😴 Sleep Log")

    hours = st.number_input("Hours Slept", min_value=0.0, value=0.0)

    if st.button("Log Sleep"):
        new_entry = {"Date": datetime.now(), "Hours": hours}
        sleep_df = pd.concat([sleep_df, pd.DataFrame([new_entry])], ignore_index=True)
        sleep_df.to_csv(SLEEP_LOG, index=False)
        st.success("Sleep logged!")

    st.subheader("📋 Edit Sleep Log")
    sleep_edit = st.data_editor(sleep_df, num_rows="dynamic", use_container_width=True)
    if st.button("Save Sleep Log"):
        sleep_edit.to_csv(SLEEP_LOG, index=False)
        st.success("Sleep log saved!")

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
    st.header("🗓️ Workout Planner")

    st.markdown("Plan your future workouts by assigning routines to specific days.")

    # Input layout (better stacked on small screens)
    selected_date = st.date_input("Select a Date to Plan Workout", datetime.now().date())
    muscle_group = st.text_input("Muscle Group (e.g., Push, Pull, Chest)")
    workout_plan = st.text_area("Workout Plan (e.g., Incline DB Press, Rows, etc.)")

    if st.button("Save Workout Plan"):
        new_entry = {
            "Date": selected_date,
            "Muscle Group": muscle_group,
            "Workout Plan": workout_plan
        }
        planner_df = pd.concat([planner_df, pd.DataFrame([new_entry])], ignore_index=True)
        planner_df.to_csv(WORKOUT_PLANNER_LOG, index=False)
        st.success("Workout plan saved!")

    st.subheader("📅 Your Workout Plans")

    # Group and show in expanders per date
    if not planner_df.empty:
        planner_df_sorted = planner_df.sort_values("Date")
        for date in planner_df_sorted["Date"].drop_duplicates():
            daily_plans = planner_df_sorted[planner_df_sorted["Date"] == date]
            with st.expander(f"{date.strftime('%A, %B %d')}"):
                for _, row in daily_plans.iterrows():
                    st.markdown(f"**{row['Muscle Group']}**: {row['Workout Plan']}")
    else:
        st.info("No workouts planned yet.")


