


import streamlit as st
import pandas as pd
import pymysql
import time 

# setting title and changing color 

st.set_page_config(page_title="Tennis Dashboard", layout="centered")

st.markdown(
    """
    <style>
        /* Main page background */
        .stApp {
            background-color: #90EE90; /* Light green */
        }

        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #4682B4; /* Steel Blue */
        }
    </style>
    """,
    unsafe_allow_html=True
)

#connecting with mysql

mydb = pymysql.connect( 
    host = "localhost",
    user= "root",
    password= "",
    port=3306 )

mycursor = mydb.cursor()

mycursor.execute("use guvi")

# Sidebar for selecting data to display
with st.sidebar:
    st.header("Select the data to view full details")
    selected_option = st.radio(
        "Choose an Option",
        ["Home", "Competition Data", "Complex Data", "Competitor Ranking Data","tasks given in project "]
    )

# Content rendering based on the selected option
if selected_option == "Home":
    st.image("c:/Users/Admin/Pictures/Screenshots/tennis.webp", use_container_width=True)
    st.markdown("# 🎾 Tennis Dashboard")

    query = '''
    SELECT *
        FROM Competitors
        INNER JOIN Competitor_Rankings
        USING (competitor_id)
    '''
    competitors_data = pd.read_sql_query(query, mydb)

    # Initialize session states to resetting purpose 

    if "name_filter" not in st.session_state:
        st.session_state.name_filter = ""
    if "rank_range" not in st.session_state:
        st.session_state.rank_range = (
            competitors_data["rank"].min(), competitors_data["rank"].max()
        )
    if "country_filter" not in st.session_state:
        st.session_state.country_filter = "All"
    if "points_range" not in st.session_state:
        st.session_state.points_range = (
            competitors_data["points"].min(), competitors_data["points"].max()
        )
    if "filters_cleared" not in st.session_state:
        st.session_state.filters_cleared = False

    # Remove Filters Button  initializing
    if st.button("🧹 Remove Filters"):
        with st.spinner("Resetting filters..."):
            time.sleep(1)  # simulate loading
            st.session_state.name_filter = ""
            st.session_state.rank_range = (
            competitors_data["rank"].min(), competitors_data["rank"].max()
        )
            st.session_state.country_filter = "All"
            st.session_state.points_range = (
            competitors_data["points"].min(), competitors_data["points"].max()
        )
            st.session_state.filters_cleared = True
    else:
        st.session_state.filters_cleared = False
    
    #creating sec to do countywise analyse 
    country = st.text_input("Enter country name :")
    if st.button("Country wise analysis"):
        query = '''
            SELECT 
            AVG(competitor_rankings.points) AS Average_points,
            COUNT(competitors.name) AS Total_no_players,
            SUM(competitor_rankings.competitions_played) AS Total_no_competitions_played
        FROM Competitors
        JOIN Competitor_Rankings 
        ON Competitors.competitor_id = Competitor_Rankings.competitor_id 
        WHERE Competitors.country = %s
        '''
        df = pd.read_sql_query(query, mydb, params=(country,))
        st.dataframe(df)

    
        
        
    st.subheader("🏆 Leaderboard")

   # radio buttons

    leaderboard_option = st.radio(
    "Select leaderboard type:",
    options=["Rank", "Points", "Back"],
    horizontal=True
    )

    if leaderboard_option == "Rank":
        query = '''
        SELECT name, country, rank, points
        FROM Competitors
        JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
        ORDER BY rank ASC
        LIMIT 10
    '''
        df = pd.read_sql_query(query, mydb)
        st.dataframe(df)

    elif leaderboard_option == "Points":
        query = '''
        SELECT name, country, rank, points
        FROM Competitors
        JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
        ORDER BY points DESC
        LIMIT 10
        '''
        df = pd.read_sql_query(query, mydb)
        st.dataframe(df)

    elif leaderboard_option == "Back":
        st.info("No leaderboard selected. Please choose an option to view.")



    # Filter Bar
    st.header("Filter Competitors")

    col1, col2, col3, col4 = st.columns([3, 3, 2, 2])

    competitor_name = col1.text_input(
        "Search by competitor name",
        value=st.session_state.name_filter,
        key="name_filter"
    )

    min_rank, max_rank = col2.slider(
        "Select Rank Range",
        min_value=competitors_data["rank"].min(),
        max_value=competitors_data["rank"].max(),
        value=st.session_state.rank_range,
        key="rank_range"
    )

    countries = competitors_data["country"].unique()
    selected_country = col3.selectbox(
        "Select Country",
        options=["All"] + list(countries),
        index=(["All"] + list(countries)).index(st.session_state.country_filter),
        key="country_filter"
    )

    points_threshold = col4.slider(
        "Select Points Threshold",
        min_value=competitors_data["points"].min(),
        max_value=competitors_data["points"].max(),
        value=st.session_state.points_range,
        key="points_range"
    )

    # codes to perform Filtering 
    filtered_competitors = competitors_data

    if competitor_name:
        filtered_competitors = filtered_competitors[
            filtered_competitors["name"].str.contains(competitor_name, case=False)
        ]

    if selected_country != "All":
        filtered_competitors = filtered_competitors[
            filtered_competitors["country"] == selected_country
        ]

    filtered_competitors = filtered_competitors[
        (filtered_competitors["rank"] >= min_rank) &
        (filtered_competitors["rank"] <= max_rank) &
        (filtered_competitors["points"] >= points_threshold[0]) &
        (filtered_competitors["points"] <= points_threshold[1])
    ]

    #  Display Result only if filters not cleared 
    st.subheader("Filtered Competitors")
    
    if not st.session_state.filters_cleared:
        st.dataframe(filtered_competitors)
    else:
        st.info("Filters cleared. No competitors to show.") 

   
# other slide bar options 

elif selected_option == "Competition Data":
    query = '''
        SELECT competitions.*, category.category_name 
        FROM competitions 
        JOIN category ON competitions.category_id = category.category_id
    '''
    comp_data = pd.read_sql_query(query, mydb)
    st.subheader("🏆 Competition Data")
    st.dataframe(comp_data)

elif selected_option == "Complex Data":
    query = '''
        SELECT venues.*, complexes.complex_name 
        FROM venues 
        JOIN complexes ON venues.complex_id = complexes.complex_id
    '''
    complex_data = pd.read_sql_query(query, mydb)
    st.subheader("🏟️ Complex Data")
    st.dataframe(complex_data)

elif selected_option == "Competitor Ranking Data":
    query = '''
        SELECT competitors.*,
        competitor_rankings.rank_id,
        competitor_rankings.rank,
        competitor_rankings.movement,
        competitor_rankings.points,
        competitor_rankings.competitions_played

        FROM competitors
        JOIN competitor_rankings ON competitors.competitor_id = competitor_rankings.competitor_id
    '''
    ranking_data = pd.read_sql_query(query, mydb)
    st.subheader("📊 Competitor Ranking Data")
    st.dataframe(ranking_data)

elif selected_option == "tasks given in project ":
   
    
    
    st.header("🎾 Competition Data Explorer")

    question = st.selectbox("Choose a question:", [
        "1. List all competitions with their category name",
        "2. Count the number of competitions in each category",
        "3. Find all competitions of type 'doubles'",
        "4. Get competitions in a specific category",
        "5. Identify parent competitions and their sub-competitions",
        "6. Analyze distribution of competition types by category",
        "7. List all competitions with no parent",
        "8. Back"
    ])

    if question.startswith("1"):
        query= '''select competitions.*,category.category_name
        from competitions join category on competitions.category_id= category.category_id '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("2"):
        query= '''SELECT count(competition_name),category.category_name 
        FROM Competitions 
        JOIN category on competitions.category_id= category.category_id GROUP BY category.category_name '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("3"):
        query= '''SELECT competition_name FROM competitions WHERE type ='doubles' '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("4"):
        category = st.text_input("Enter category name (e.g., ITF Men):")
        query= '''select competitions.competition_name,category.category_name 
        from competitions 
        join category on competitions.category_id= category.category_id 
        where category_name = %s '''
        df = pd.read_sql_query(query,mydb,params=(category,))
        st.dataframe(df)

    elif question.startswith("5"):
        query= '''select parent_id,competition_id as Sub_ID ,competition_name as sub_competitions 
        from competitions where parent_id = parent_id order by parent_id  '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("6"):
        query= '''select category.category_name,competitions.competition_name ,competitions.type 
        from competitions 
        join category on competitions.category_id= category.category_id 
        order by category_name '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("7"):
        query= '''SELECT competitions.* FROM competitions WHERE parent_id IS NULL'''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("8"):
        st.write("")

    st.header("🏟️ Complexes Data Explorer ")
       
    question = st.selectbox("Choose a question:", [

        "1. List all venues along with their associated complex name",
        "2. Count the number of venues in each complex",
        "3. Get details of venues in a specific country (e.g., Chile)",
        "4. Identify all venues and their timezones",
        "5. Find complexes that have more than one venue",
        "6. List venues grouped by country",
        "7. Find all venues for a specific complex (e.g., Nacional)",
        "8. Back"
    ])

    if question.startswith("1"):
        query= '''select Venues.*,complexes.complex_name
        from Venues join complexes on Venues.complex_id = complexes.complex_id '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("2"):
        query= '''select complexes.complex_name,count(venue_name) as no_of_venues 
        from Venues 
        join complexes on Venues.complex_id = complexes.complex_id group by complex_name '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("3"):
        
        country = st.text_input("Enter country name (e.g., Chile):")
        query= '''select * from venues where country_name = %s '''
        df = pd.read_sql_query(query,mydb,params=(country,))
        st.dataframe(df)

    elif question.startswith("4"):
        query= '''select venue_name,timezone from venues'''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("5"):
        query= '''select complexes.*,count(venue_id) as no_of_venues 
        from Venues 
        join complexes on Venues.complex_id = complexes.complex_id 
        group by complex_name,complex_id having count(venue_id) >1 '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("6"):
        query= '''select * from venues order by country_name '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("7"):
        compl = st.text_input("Enter specific complex (e.g., Nacional):")
        query= '''select venues.*,complexes.complex_name
        from Venues 
        join complexes on Venues.complex_id = complexes.complex_id  
        where complex_name = %s '''
        df = pd.read_sql_query(query,mydb,params=(compl,))
        st.dataframe(df)

    elif question.startswith("8"):
        st.write("")

    st.header("🥇🥈🏅 Competitor Rankings Data Explorer")
    
    question = st.selectbox("Choose a question:", [

        "1. Get all competitors with their rank and points.",
        "2. Find competitors ranked in the top 5",
        "3. List competitors with no rank movement (stable rank)",
        "4. Get the total points of competitors from a specific country (e.g., Croatia)",
        "5. Count the number of competitors per country",
        "6. Find competitors with the highest points in the current week",
        "7. Back"
    ])

    if question.startswith("1"):
        query= '''select Competitors.*,Competitor_Rankings.rank,Competitor_Rankings.points
        from Competitors
        join Competitor_Rankings on Competitors.competitor_id = Competitor_Rankings.competitor_id  '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("2"):
        query= '''select Competitors.*,Competitor_Rankings.rank
        from Competitors
        join Competitor_Rankings on Competitors.competitor_id = Competitor_Rankings.competitor_id  
        where rank <=5 '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("3"):
        query= '''select Competitor_Rankings.movement,Competitors.*
        from Competitors
        join Competitor_Rankings on Competitors.competitor_id = Competitor_Rankings.competitor_id  
        where movement =0 '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("4"):
       country = st.text_input("Enter country name  (e.g., Croatia):")
       query= '''select sum(Competitor_Rankings.points) as total_points 
       from Competitors
       join Competitor_Rankings on Competitors.competitor_id = Competitor_Rankings.competitor_id  
       where country =  %s '''
       df = pd.read_sql_query(query,mydb,params=(country,))
       st.dataframe(df)

    elif question.startswith("5"):
        query= '''select count(name) as No_of_competitors ,country from Competitors group by country '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)

    elif question.startswith("6"):
        query= '''select max(Competitor_Rankings.points) as highest_points,Competitors.*
        from Competitors
        join Competitor_Rankings on Competitors.competitor_id = Competitor_Rankings.competitor_id  '''
        df = pd.read_sql_query(query,mydb)
        st.dataframe(df)
        
    elif question.startswith("7"):
        st.write("")

   






