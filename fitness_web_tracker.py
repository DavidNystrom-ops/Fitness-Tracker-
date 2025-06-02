import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Fitness Tracker", layout="centered")
st.title("🏋️‍♂️ Fitness Tracker")

DATA_DIR = "data"
WORKOUT_LOG = os.path.join(DATA_DIR, "workout_data.csv")
NUTRITION_LOG = os.path.join(DATA_DIR, "nutrition_log.csv")
if os.path.exists(DATA_DIR) and not os.path.isdir(DATA_DIR):
    os.remove(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)

def load_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["Date"])
    return pd.DataFrame(columns=columns)

def save_csv(df, path):
    df.to_csv(path, index=False)
Save goal data
def save_goals(protein, carbs, fats, calories):
    df = pd.DataFrame([{
        "Protein (g)": protein,
        "Carbs (g)": carbs,
        "Fats (g)": fats,
        "Calories": calories
    }])
    df.to_csv(GOALS_FILE, index=False)

Load goals
def load_goals():
    if os.path.exists(GOALS_FILE):
        return pd.read_csv(GOALS_FILE).iloc[0]
    return pd.Series({"Protein (g)": 0, "Carbs (g)": 0, "Fats (g)": 0, "Calories": 0})

Main app
tabs = st.tabs(["🍎 Nutrition", "🏋️‍♂️ Workout Tracker", "💧 Water", "🛌 Sleep", "📈 Progress"])


st.header("Nutrition Log")
meal = st.text_input("Meal Description")
protein = st.number_input("Protein (g)", 0)
carbs = st.number_input("Carbs (g)", 0)
fats = st.number_input("Fats (g)", 0)
calories = st.number_input("Calories", 0)

if st.button("Log Meal"):
    date = pd.Timestamp.now()
    new_row = pd.DataFrame([[date, meal, protein, carbs, fats, calories]],
                           columns=["Date", "Meal", "Protein", "Carbs", "Fats", "Calories"])
    nutrition_df = load_csv(NUTRITION_LOG, new_row.columns.tolist())
    nutrition_df = pd.concat([nutrition_df, new_row], ignore_index=True)
    save_csv(nutrition_df, NUTRITION_LOG)
    st.success("Meal logged.")

st.subheader("Meal History")
try:
    nutrition_df = load_csv(NUTRITION_LOG, ["Date", "Meal", "Protein", "Carbs", "Fats", "Calories"])
    st.dataframe(nutrition_df.tail(10))
except Exception as e:
    st.warning("No meal data found yet.")
