import streamlit as st
import pandas as pd

# Load the data
@st.cache_data
def load_data():
    df = pd.read_excel("leaderboard.xlsx")
    df = df[['Profile Image', 'Author', 'Average Score', 'Number Played', 'Most Recent']]
    return df

st.set_page_config(page_title="Scrandle Leaderboard", layout="wide")
st.markdown("<h1 style='font-size: 40px; color: #f1f1f1;'>🏆 Scrandle Leaderboard</h1>", unsafe_allow_html=True)

# -- Filter controls
col1, col2, col3 = st.columns(3)
with col1:
    sort_option = st.selectbox("Sort by:", ["Average Score (High → Low)", "Games Played (High → Low)"])
with col2:
    min_games = st.number_input("Minimum Games Played", min_value=0, value=5)
with col3:
    max_days_inactive = st.number_input("Played Within (Days)", min_value=0, value=7)

# Load and filter data
df = load_data()

# Handle "Most Recent" if it's a timedelta (convert to days)
if pd.api.types.is_timedelta64_dtype(df['Most Recent']):
    df['Inactive Days'] = df['Most Recent'].dt.days.abs()
else:
    df['Inactive Days'] = df['Most Recent'].abs()

# Apply filters
df = df[(df['Number Played'] >= min_games) & (df['Inactive Days'] <= max_days_inactive)]

# Apply sorting
if sort_option == "Average Score (High → Low)":
    df = df.sort_values(by='Average Score', ascending=False).reset_index(drop=True)
else:
    df = df.sort_values(by='Number Played', ascending=False).reset_index(drop=True)

# -- CSS Styling --
st.markdown("""
<style>
.leaderboard {
    width: 100%;
    border-collapse: collapse;
    font-family: Arial, sans-serif;
    font-size: 16px;
    margin-top: 20px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    background-color: #ffffff;
    color: #222222;
}
.leaderboard thead {
    background-color: #f2f2f2;
    color: #222222;
}
.leaderboard th, .leaderboard td {
    text-align: left;
    padding: 12px;
    border-bottom: 1px solid #e0e0e0;
    vertical-align: middle;
}
.leaderboard tr:nth-child(even) {
    background-color: #fafafa;
}
.leaderboard tr:nth-child(odd) {
    background-color: #ffffff;
}
.leaderboard .top {
    background-color: #fff7cc !important;
}
img.avatar {
    border-radius: 50%;
    width: 60px;
    height: 60px;
    object-fit: cover;
}
.score-green {
    color: #2e7d32;
    font-weight: bold;
}
.score-orange {
    color: #f9a825;
    font-weight: bold;
}
.score-red {
    color: #c62828;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Trophy & formatting helpers
def get_trophy(index):
    return ["🥇", "🥈", "🥉"][index] if index < 3 else ""

def get_score_class(score):
    if score >= 9:
        return "score-green"
    elif score >= 7:
        return "score-orange"
    else:
        return "score-red"

# Build leaderboard HTML
row_list = []
for i, row in df.iterrows():
    avatar = f'<img class="avatar" src="{row["Profile Image"]}">' if pd.notna(row["Profile Image"]) else ""
    trophy = get_trophy(i)
    score_class = get_score_class(row['Average Score'])
    row_class = "top" if i == 0 else ""
    row_html = f"""
    <tr class="{row_class}">
        <td>{avatar}</td>
        <td><strong style='font-size:17px'>{trophy}{row['Author']}</strong></td>
        <td class="{score_class}">{row['Average Score']:.2f}</td>
        <td>{row['Number Played']}</td>
    </tr>
    """
    row_list.append(row_html.strip())

joined_rows = "\n".join(row_list)

html_table = f"""
<table class="leaderboard">
    <thead>
        <tr>
            <th>Profile</th>
            <th>Author</th>
            <th>Average Score</th>
            <th>Games Played</th>
        </tr>
    </thead>
    <tbody>
        {joined_rows}
    </tbody>
</table>
"""

st.markdown(html_table, unsafe_allow_html=True)
