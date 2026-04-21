"""
Name: Alyssa DiBenedetto
CS230: 2
Data: Starbucks in the USA
URL: xxx
Description: Interactive Streamlit application exploring Starbucks locations across the United States.
References:
    - Dataset: https://www.kaggle.com/datasets/starbucks/store-locations
    - Color Gradient Logic: https://matplotlib.org/stable/users/explain/colors/colors.html
    - Map Legend Logic: https://docs.streamlit.io/develop/api-reference/text/st.markdown
"""

import streamlit as st              #web application
import pandas as pd                 #data manipulation
import pydeck as pdk                #mapping
import matplotlib.pyplot as plt     #charting

@st.cache_data
def load_data():
    return pd.read_csv("usa_starbucks.csv")

#[FUNC2P] Function with two parameters (data & state), one of which (state) has a default value ("All States")
def filter_data(data, state="All States"):
    if state != "All States":
        return data[data["State/Province"] == state]
    return data

#[FUNCCALL2] Function make_green_gradient() is called for the bar chart and pie chart
def make_green_gradient(n):
    if n <= 1:
        return [(0, 80 / 255, 0)]
    #[LISTCOMP] List comprehension to generate a green color gradient for the bar chart based on the number of states being displayed
    return [(0, (80 + 175 * (i / (n - 1))) / 255, 0) for i in range(n)]

def main():
    df = load_data()

    #[ST3] Streamlit sidebar with title and image
    st.sidebar.title("Starbucks Location Explorer")
    st.sidebar.image("starbuckslogo.png", width=150)

    #[ST2] Streamlit slider to select number of results to display (5-50, default 10)
    top_n = st.sidebar.slider("Number of Results to Display", 5, 51, 10)

    st.title("Starbucks Locations in the US")


    #[CHART1] Horizontal bar chart showing number of Starbucks locations by state, colored with a green gradient based on count

    st.header("Starbucks Locations by State")
    
    #[ST1] Streamlit checkbox to toggle between showing top states and bottom states
    show_top_states = st.checkbox("Show TOP states (uncheck for bottom states)", value=True)
    
    #[PIVOTTABLE] Pivot table to count number of Starbucks locations by state
    state_counts = df.pivot_table(
        index="State/Province",
        values="Store Number",
        aggfunc="count"
    ).reset_index()
    state_counts.rename(columns={"Store Number": "Store Count"}, inplace=True)
    
    #[SORT] Sort the pivot table based on the checkbox selection to show either top states or bottom states
    state_counts = state_counts.sort_values("Store Count", ascending=not show_top_states)
    display_states = state_counts.head(top_n)
    
    #[MAXMIN] Identify the state with the highest or lowest number of Starbucks locations based on the checkbox selection
    extreme_state = display_states.iloc[0]["State/Province"]
    extreme_value = display_states.iloc[0]["Store Count"]
    st.write(f"Highlighted state: **{extreme_state} ({extreme_value})**")
    
    #[FUNCCALL2] Calling make_green_gradient() for bar chart coloring
    bar_colors = make_green_gradient(len(display_states))
    
    fig, ax = plt.subplots()
    bars = ax.barh(
        display_states["State/Province"],
        display_states["Store Count"],
        color=bar_colors)
    ax.invert_yaxis()
    ax.set_xlabel("Number of Locations")
    
    #[ITERLOOP] Loop iterating through the bars to add count labels at the end of each bar
    offset = max(display_states["Store Count"]) * 0.001
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)}",
            va="center",
            fontsize=6)
   
    st.pyplot(fig)


    #[CHART2] Pie chart showing distribution of Starbucks locations by city within the selected state
   
    st.header("City-Level Starbucks Distribution")

    #[ST1] Streamlit selectbox to choose a state for the city breakdown, with an option for "All States"
    states = sorted(df["State/Province"].dropna().unique())
    selected_state = st.selectbox("Select a State for City Breakdown",["All States"] + states)
    
    #[ST1] Streamlit checkbox to toggle between showing top cities and bottom cities within the selected state
    show_top_cities = st.checkbox("Show TOP cities (uncheck for bottom cities)", value=True)
    
    #[FILTER1]
    state_df = filter_data(df, selected_state)
    
    #[PIVOTTABLE] Pivot table to count number of Starbucks locations by city within the selected state
    state_df["City"] = state_df["City"].str.strip().str.title()
    city_counts = state_df.pivot_table(
        index="City",
        values="Store Number",
        aggfunc="count"
    ).reset_index()
    city_counts.rename(columns={"Store Number": "Store Count"}, inplace=True)
    
    #[SORT] Sort the pivot table based on the checkbox selection to show either top cities or bottom cities within the selected state
    city_counts = city_counts.sort_values("Store Count", ascending=not show_top_cities)
    city_counts = city_counts.head(top_n)
    
    #[FUNCCALL2] Calling make_green_gradient() for pie chart coloring
    pie_colors = make_green_gradient(len(city_counts))
    
    fig2, ax2 = plt.subplots()
    ax2.pie(
        city_counts["Store Count"],
        labels=city_counts["City"],
        autopct="%1.1f%%",
        startangle=140,
        colors=pie_colors)
    
    st.pyplot(fig2)


    #[MAP] Interactive map showing Starbucks locations in the selected state, colored by ownership type (company-owned vs licensed)
    
    st.header("Starbucks Locations Map")
    
    #[COLUMNS] Select only the necessary columns for mapping and drop rows with missing coordinates or ownership type
    map_df = state_df[["Latitude", "Longitude", "City", "Ownership Type"]].dropna()
    
    #[LAMBDA] Lambda function to assign colors based on ownership type for the map visualization
    map_df["color"] = map_df["Ownership Type"].apply(
        lambda x: [0, 112, 74] if x == "Company Owned" else [0, 180, 120])
    
    st.pydeck_chart(
        pdk.Deck(
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    get_position="[Longitude, Latitude]",
                    get_fill_color="color",
                    get_radius=10,
                    radiusUnits="pixels",
                    pickable=True)],
            initial_view_state=pdk.ViewState(
                latitude=map_df["Latitude"].mean(),
                longitude=map_df["Longitude"].mean(),
                zoom=5),
            tooltip={"text": "{City} ({Ownership Type})"}))
    
    st.markdown("**Map Legend:**")
    st.markdown('<span style="color:rgb(0,112,74)">●</span> Company-Owned Starbucks', unsafe_allow_html=True)
    st.markdown('<span style="color:rgb(0,180,120)">●</span> Licensed Starbucks', unsafe_allow_html=True)

main()