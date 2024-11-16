import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import plotly.express as px
import matplotlib.ticker as mtick
import numpy as np
import scipy.interpolate
import seaborn as sns

# Set OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set page configuration
st.set_page_config(page_title="Foot Flow", layout="wide")

# Function to get detailed market information using OpenAI
def get_market_details(center_name):
    try:
        messages = [
            {"role": "system", "content": "You are a market analyst specializing in providing detailed insights for restaurant owners in San Jose, California."},
            {"role": "user", "content": f"""
            Provide a comprehensive analysis of the market for the plaza called '{center_name}' in San Jose, specifically for someone looking to open a restaurant. Include the following details:
            
            - **Pros and Cons**: List the main advantages and disadvantages of this location as it pertains to opening a restaurant, considering both high-level and detailed points.
            
            - **Accessibility Issues**: Describe the accessibility of the location, including parking availability, public transit options, walkability, and any accessibility challenges or benefits that might affect customer flow.
            
            - **Demographics**: Provide an overview of the local population, including average income, family size, age distribution, and relevant lifestyle preferences. Explain why these demographics would or would not be favorable for different types of restaurants (e.g., casual, fine dining, fast food, or niche cuisines).
            
            - **Foot Traffic Trends**: Describe the foot traffic patterns around this plaza, highlighting peak hours, busy days, and seasonal variations. Include specific tips for capturing foot traffic based on these trends, such as recommended hours of operation or menu specials.
            
            - **Local Competition**: Identify the existing restaurant types and notable competitors in the area. Highlight any gaps in the market or opportunities for new restaurant types. Provide insights into how a new restaurant could differentiate itself in this competitive environment.
            
            - **Atmosphere and Customer Expectations**: Describe the general atmosphere of the plaza and the type of dining experiences people expect when visiting this location. Indicate whether this plaza attracts families, professionals, students, tourists, etc., and how a restaurant could tailor its vibe and decor to align with these expectations.
            
            - **Special Advice for Beginners**: Include additional insights for first-time restaurant owners, such as startup tips, common pitfalls in this area, and advice on building a customer base. Recommend initial marketing strategies to attract attention and build loyalty.
            
            - **Advanced Insights for Experienced Owners**: For seasoned restaurateurs, suggest ways to maximize revenue, streamline operations, and use advanced marketing techniques. Include advice on leveraging digital tools (e.g., delivery platforms, social media) and optimizing operational efficiency based on the plaza's characteristics.
            
            Aim to provide practical, actionable insights that would be valuable to both a beginner and an experienced restaurant owner.
            """}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=4096
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Sidebar with Logo and Centered Title
st.sidebar.image("footflowlogo.png", use_column_width=True)
st.sidebar.markdown(
    """
    <style>
    .sidebar-title {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .stButton button {
        background: none;
        color: #FFFFFF;
        font-size: 20px;
        border: none;
        padding: 10px 0;
        text-align: left;
        cursor: pointer;
    }
    .stButton button:hover {
        color: #ff4b4b;
    }
    </style>
    <div class="sidebar-title">Foot Flow</div>
    """,
    unsafe_allow_html=True
)

# Sidebar navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"
if st.sidebar.button("Home 🏠"):
    st.session_state.page = "Home"
if st.sidebar.button("Restaurant Insights 🍽"):
    st.session_state.page = "Restaurant Insights"
if st.sidebar.button("Chatbot 🤖"):
    st.session_state.page = "Chatbot"

# Load data functions
@st.cache_data
def load_data(file_path="sanjosedataset.csv"):
    return pd.read_csv(file_path)

# Load data functions
@st.cache_data
def load_foot_traffic_data(file_path="sj_daily_foottraffic.csv"):
    return pd.read_csv(file_path)

# Load the new dataset
@st.cache_data
def load_hourly_foot_traffic(file_path="sj_hourly_foottraffic.csv"):
    return pd.read_csv(file_path)

# After loading the data, define `foot_traffic_plaza`
foot_traffic_data = load_foot_traffic_data()
foot_traffic_plaza = foot_traffic_data[['Date', 'Business Corridor', 'Foot Traffic Volume']].copy()

# Load hourly foot traffic data
hourly_traffic_data = load_hourly_foot_traffic()

# Apply main title and feature card styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 36px;
        color: #FF4B4B;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .feature-card {
        background-color: #2c2f38;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
    }
    .feature-title {
        font-size: 20px;
        font-weight: bold;
        color: #ff4b4b;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display content based on page selection
if st.session_state.page == "Home":
    # Main Title
    st.markdown("<div class='main-title'>Welcome to Foot Flow! 👣</div>", unsafe_allow_html=True)
    st.write(
    "Foot Flow is a powerful tool for aspiring and seasoned restaurant owners looking to find prime locations in San Jose. "
    "By providing insights on foot traffic, demographics, local competition, and leasing options, Foot Flow helps you make informed decisions "
    "on where to establish your new restaurant. Customize your search based on restaurant type, cuisine, budget, and space needs to find a location "
    "that aligns with your vision and maximizes your potential for success."
)
    
    # Features Section
    st.write("### Features:")

    # Feature Cards
    st.markdown("<div class='feature-card'><div class='feature-title'>🍽 Restaurant Insights</div><p>Explore location-specific data for choosing the right restaurant spot.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='feature-card'><div class='feature-title'>🤖 Chatbot</div><p>Ask questions about setting up your business in San Jose.</p></div>", unsafe_allow_html=True)

elif st.session_state.page == "Restaurant Insights":
    st.header("Restaurant Insights 🍽")
    st.write("Explore and compare prime locations in San Jose for opening your restaurant. Tailor your search by restaurant style, cuisine, budget, and space requirements to find a location that aligns with your business goals and maximizes customer reach.")

    
    data = load_data()
    foot_traffic_data = load_foot_traffic_data()
    
    # Check for required columns
    required_columns = ['Location Name', 'Address', 'Cuisine Compatibility', 'Image URL', 'Average Store Size (sq ft)', 'Average Lease Rate ($/sq ft)', 'Price Range', 'Vacancy Status']
    if not all(column in data.columns for column in required_columns):
        st.error(f"Dataset is missing one or more required columns: {', '.join(required_columns)}")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            restaurant_type = st.selectbox("Restaurant Type:", ["Fast Food", "Casual Dining", "Fine Dining", "Cafe", "Coffee Shop", "Dessert Shops", "Buffet", "Food Truck", "Other"], key="restaurant_type")
        with col2:
            food_types = st.multiselect("Cuisine Type:", ["Italian", "Mexican", "Chinese", "Indian", "Japanese", "Korean", "American", "Mediterranean", "Vegan", "Fusion", "Other"], key="food_types")
        with col3:
            startup_costs = st.selectbox("Startup Costs:", ["<$10,000", "$10,000-$50,000", "$50,000-$100,000", "$100,000+"], key="startup_costs")

        square_footage = st.slider("Desired Square Footage (sq²):", min_value=100, max_value=10000, step=100, key="square_footage")
        
        submit_button = st.button("Submit", key="restaurant_insights_submit")

        if submit_button:
            filtered_data = data.dropna(subset=['Cuisine Compatibility'])
            filtered_data = filtered_data[filtered_data['Cuisine Compatibility'].apply(
                lambda x: restaurant_type.lower() in x.lower() or any(food.lower() in x.lower() for food in food_types))
            ]

            if filtered_data.empty:
                st.write("No matching plazas found. Please adjust your selection criteria.")
            else:
                filtered_data['Monthly Lease Cost'] = filtered_data['Average Lease Rate ($/sq ft)'] * square_footage
                filtered_data['Yearly Lease Cost'] = filtered_data['Monthly Lease Cost'] * 12
                st.session_state['filtered_data'] = filtered_data.drop_duplicates(subset=['Location Name']).reset_index(drop=True)

        # Display filtered results in a centered table format
        if 'filtered_data' in st.session_state and not st.session_state['filtered_data'].empty:
            st.write("### Potential Locations:")
            st.markdown(
                """
                <style>
                .wide-table {
                    width: 100%;
                    table-layout: auto;
                    text-align: center;
                    margin: 0 auto;
                    border-collapse: collapse;
                    background-color: #2c2f38;
                    color: white;
                    font-size: 16px;
                }
                .wide-table th, .wide-table td {
                    border: 1px solid #444;
                    padding: 10px;
                    vertical-align: middle;
                }
                .wide-table th {
                    background-color: #444;
                    font-weight: bold;
                }
                .wide-table img {
                    width: 150px;
                    height: auto;
                    display: block;
                    margin: 0 auto;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # Create the HTML table
            markdown_table = "<table class='wide-table'><tr><th>Image</th><th>Center Name</th><th>Address</th><th>Price Range</th><th>Monthly Lease Cost</th><th>Yearly Lease Cost</th><th>Vacancy Status</th></tr>"

            for _, row in st.session_state['filtered_data'].iterrows():
                markdown_table += f"<tr><td><img src='{row['Image URL']}' /></td><td>{row['Location Name']}</td><td>{row['Address']}</td><td>{row['Price Range']}</td><td>${row['Monthly Lease Cost']:,.2f}</td><td>${row['Yearly Lease Cost']:,.2f}</td><td>{row['Vacancy Status']}</td></tr>"

            markdown_table += "</table>"
            st.markdown(markdown_table, unsafe_allow_html=True)

            # Replace title dynamically
            selected_place = st.selectbox("Learn more about a specific location:", st.session_state['filtered_data']['Location Name'].unique())
            if selected_place:
                # Retrieve and display detailed market analysis
                detailed_insights = get_market_details(selected_place)
                st.write(detailed_insights)
                st.divider()  # Add a horizontal line for separation
                st.subheader(f"Overall Foot Traffic Insights for {selected_place}")
                

                # Replace general description above the dropdown
                st.markdown("""
                    <p>Understanding foot traffic is crucial for making informed decisions about your restaurant's location. 
                    Select a metric below to explore detailed foot traffic insights for the selected plaza. These metrics provide 
                    valuable information on daily, weekly, monthly, and yearly visitor trends, helping you tailor your operations, 
                    marketing strategies, and staffing to maximize customer engagement.</p>
                """, unsafe_allow_html=True)

                # Dropdown for selecting foot traffic metric
                traffic_option = st.selectbox(
                    "Choose Foot Traffic Metric:",
                    ["Average Foot Traffic Per Day", "Average Foot Traffic Per Week", "Average Foot Traffic Per Month", "Total Foot Traffic Per Year"]
                )
                
                # Include the styling for the insights card
                st.markdown("""
                    <style>
                    .insights-card {
                        background-color: #2c2f38;
                        padding: 15px;
                        border-radius: 10px;
                        margin-top: 15px;
                    }
                    .insights-card h4 {
                        color: #ff4b4b;
                        margin-bottom: 5px;
                    }
                    .insights-card p {
                        margin: 0;
                    }
                    </style>
                """, unsafe_allow_html=True)

                # Ensure the foot_traffic_plaza dataframe is properly prepared
                foot_traffic_plaza['Date'] = pd.to_datetime(foot_traffic_plaza['Date'])

                # Calculate total traffic per year from monthly or daily data
                foot_traffic_grouped_month = foot_traffic_plaza.groupby(foot_traffic_plaza['Date'].dt.to_period('M')).agg({'Foot Traffic Volume': 'sum'}).reset_index()
                foot_traffic_grouped_month['Date'] = foot_traffic_grouped_month['Date'].dt.to_timestamp()

                # Calculate total traffic per year
                total_traffic_per_year = foot_traffic_grouped_month['Foot Traffic Volume'].sum()

                # Metrics calculation
                avg_traffic_per_day = int(round(total_traffic_per_year / 365))
                avg_traffic_per_week = int(round(total_traffic_per_year / 52))
                avg_traffic_per_month = int(round(total_traffic_per_year / 12))


# Bold the "x amount of people"
                if traffic_option == "Average Foot Traffic Per Day":
                    st.markdown(f"""
                        <div class="insights-card" style="background-color: #2c2f38; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                            <h4 style="color: #ff4b4b;">Overall Average Foot Traffic Per Day</h4>
                            <p style="font-size: 20px; font-weight: bold; color: #ffffff;">{avg_traffic_per_day:,} people</p>
                            <p style="color: #94a3b8;">This represents the average number of people who pass through or visit the area on a typical day. 
                            Use this metric to estimate daily customer potential, plan staffing levels, and determine the best hours 
                            for peak operations to maximize customer engagement.</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # Plot daily foot traffic trends with Plotly
                    # Simulated dataset structure (replace this with your actual data)
                    # Ensure the data has 'Hour' and 'Foot Traffic' columns
                    hourly_traffic_data = pd.DataFrame({
                        'Hour': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00',
                                '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
                                '20:00', '21:00', '22:00', '23:00'],
                        'Foot Traffic': [0, 0, 0, 0, 0, 5, 20, 50, 100, 150, 200, 250, 300, 320, 310, 290, 270, 250, 200, 150, 100, 50, 10, 0]
                    })

                    # Check the structure of the dataset
                    if 'Hour' not in hourly_traffic_data.columns or 'Foot Traffic' not in hourly_traffic_data.columns:
                        st.error("The dataset must contain 'Hour' and 'Foot Traffic' columns.")
                    else:
                        # Extract hour as an integer from the 'Hour' column
                        hourly_traffic_data['Hour'] = pd.to_datetime(hourly_traffic_data['Hour'], format='%H:%M').dt.hour

                        # Add formatted time labels for the x-axis
                        hourly_traffic_data['Formatted Time'] = pd.to_datetime(hourly_traffic_data['Hour'], format='%H').dt.strftime('%I:%M %p')

                        # Ensure all 24 hours are included in the data
                        all_hours = pd.DataFrame({'Hour': range(24)})
                        hourly_traffic_data = all_hours.merge(hourly_traffic_data, on='Hour', how='left').fillna(0)

                        # Reduce the number of displayed x-axis labels (e.g., every 3 hours)
                        tick_step = 3
                        tickvals = hourly_traffic_data['Hour'][::tick_step]
                        ticktext = hourly_traffic_data['Formatted Time'][::tick_step]

                        # Plot hourly trends using Plotly
                        fig = px.line(
                            hourly_traffic_data,
                            x="Hour",  # Hour is numeric for sorting
                            y="Foot Traffic",
                            title="",  # The title will be set in update_layout
                            labels={"Hour": "Time of Day", "Foot Traffic": "Average Foot Traffic Volume"},
                            template="plotly_dark",
                        )

                        # Adjust the layout to properly center the title
                        fig.update_layout(
                            title={
                                "text": f"Average Hourly Foot Traffic on a Typical Day at {selected_place}",
                                "x": 0.5,  # Center the title
                                "xanchor": "center",  # Ensure proper alignment
                                "yanchor": "top",
                            },
                            title_font_size=20,
                            xaxis=dict(
                                tickmode='array',
                                tickvals=tickvals,
                                ticktext=ticktext,
                                range=[-0.5, 23.5],  # Ensure the graph starts at 0 and ends at 23
                                showgrid=True,
                                zeroline=True,
                                showline=True,
                                linecolor='white',  # Axis line color
                                mirror=True,
                            ),
                            xaxis_title="Time of Day",
                            yaxis_title="Average Foot Traffic Volume",
                            font=dict(size=14),
                        )
                        fig.update_traces(
                            mode="lines+markers", 
                            line=dict(color="#ff4b4b", width=3)  # Match the red color
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Analyze hourly traffic insights
                        max_traffic_hour = hourly_traffic_data.loc[hourly_traffic_data['Foot Traffic'].idxmax()]
                        min_traffic_hour = hourly_traffic_data.loc[hourly_traffic_data['Foot Traffic'].idxmin()]
                        avg_hourly_traffic = int(hourly_traffic_data['Foot Traffic'].mean())  # Convert to integer

                        busiest_time = max_traffic_hour['Formatted Time']
                        quietest_time = min_traffic_hour['Formatted Time']

                        # Graph insights and recommendations
                        st.markdown(f"""
                            <div style="background-color: #2c2f38; padding: 20px; border-radius: 10px; margin-top: 20px;">
                                <h4 style="color: #ff4b4b; text-align: left;">Graph Insights</h4>
                                <p style="color: white;">
                                    <b>Peak Hour:</b> The busiest time of the day is around <b>{busiest_time}</b>, where traffic reaches its peak.<br>
                                    <b>Quietest Hour:</b> The quietest time of the day is <b>{quietest_time}</b>, with minimal activity.<br>
                                    <b>Average Hourly Traffic:</b> On average, there are <b>{avg_hourly_traffic} people</b> during each hour of the day.
                                </p>
                                <h4 style="color: #ff4b4b; text-align: left;">Recommendations</h4>
                                <ul style="color: white;">
                                    <li>Plan staffing levels to align with peak hours for better customer service.</li>
                                    <li>Schedule promotions or special offers during busy periods to maximize reach.</li>
                                    <li>Use off-peak hours for maintenance or other operational improvements.</li>
                                </ul>
                            </div>
                        """, unsafe_allow_html=True)

                elif traffic_option == "Average Foot Traffic Per Week":
                    # Aggregate foot traffic data by day of the week
                    foot_traffic_data['Day of Week'] = pd.to_datetime(foot_traffic_data['Date']).dt.day_name()
                    weekly_traffic = foot_traffic_data.groupby('Day of Week')['Foot Traffic Volume'].mean().reindex(
                        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    )

                    # Header
                    st.markdown(f"""
                        <div class="insights-card" style="background-color: #2c2f38; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                            <h4 style="color: #ff4b4b;">Overall Average Foot Traffic Per Week</h4>
                            <p style="font-size: 20px; font-weight: bold; color: #ffffff;">{avg_traffic_per_week:,} people</p>
                            <p style="color: #94a3b8;">
                                This represents the average number of people who pass through or visit the area during a typical week. 
                                Use this metric to identify busy days, plan operations, and optimize weekly performance.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    # Create a Plotly bar chart for weekly foot traffic
                    fig = px.bar(
                        x=weekly_traffic.index,
                        y=weekly_traffic.values,
                        labels={"x": "Day of the Week", "y": "Average Foot Traffic Volume"},
                        title="",  # Title will be added in `update_layout`
                        template="plotly_dark",
                    )

                    # Update the layout for title and axis styling
                    fig.update_layout(
                        title={
                            "text": f"Average Foot Traffic by Day of a Typical Week for {selected_place}",  # Use f-string here
                            "x": 0.5,  # Center the title
                            "xanchor": "center",  # Center alignment
                            "yanchor": "top",  # Align the title to the top
                        },
                        title_font_size=20,  # Adjust font size
                        xaxis_title="Day of the Week",
                        yaxis_title="Average Foot Traffic Volume",
                        font=dict(size=14),  # General font size for labels
                    )

                    # Update the color of the bars
                    fig.update_traces(marker_color="#ff4b4b")  # Match UI theme color

                    # Render the bar chart
                    st.plotly_chart(fig, use_container_width=True)


                    # Analyze weekly traffic insights
                    busiest_day = weekly_traffic.idxmax()
                    busiest_traffic = int(weekly_traffic.max())
                    least_busy_day = weekly_traffic.idxmin()
                    least_busy_traffic = int(weekly_traffic.min())
                    avg_weekly_traffic = int(weekly_traffic.mean())

                    # Generate insights section
                    st.markdown(f"""
                        <div style="background-color: #2c2f38; padding: 20px; border-radius: 10px; margin-top: 20px;">
                            <h4 style="color: #ff4b4b; text-align: left;">Graph Insights</h4>
                            <p style="color: white;">
                                <b>Busiest Day:</b> The highest foot traffic occurs on <b>{busiest_day}</b> with an average of <b>{busiest_traffic} people</b>. This is the ideal day for special promotions or events.<br>
                                <b>Least Busy Day:</b> The lowest foot traffic occurs on <b>{least_busy_day}</b> with an average of <b>{least_busy_traffic} people</b>. Use this day to perform maintenance or test new strategies.<br>
                                <b>Average Daily Traffic:</b> On average, the location sees about <b>{avg_weekly_traffic} people</b> per day.
                            </p>
                            <h4 style="color: #ff4b4b; text-align: left;">Recommendations</h4>
                            <ul style="color: white;">
                                <li>Plan promotions or events on <b>{busiest_day}</b> to maximize engagement.</li>
                                <li>Optimize staffing levels for peak days like <b>{busiest_day}</b>.</li>
                                <li>Experiment with new offerings or operational changes on <b>{least_busy_day}</b>.</li>
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)

                elif traffic_option == "Average Foot Traffic Per Month":
                    # Filter data dynamically based on the selected location
                    filtered_data = foot_traffic_data[foot_traffic_data['Business Corridor'] == selected_place]

                    # Ensure there is data for the selected location
                    if filtered_data.empty:
                        st.error(f"No data available for {selected_place}. Please select another location.")
                    else:
                        # Ensure 'Date' column is in datetime format
                        filtered_data['Date'] = pd.to_datetime(filtered_data['Date'], errors='coerce')

                        # Drop rows with invalid dates if any
                        filtered_data = filtered_data.dropna(subset=['Date'])

                        # Calculate the week of the month (1 to 4)
                        filtered_data['Week of Month'] = (filtered_data['Date'].dt.day - 1) // 7 + 1

                        # Group by week of the month and calculate the average across all months
                        monthly_traffic = (
                            filtered_data.groupby('Week of Month')['Foot Traffic Volume']
                            .mean()
                            .reindex(range(1, 5), fill_value=0)  # Ensure weeks 1 to 4 are included
                        )

                        # Header with highlighted metric
                        avg_traffic_per_month = int(monthly_traffic.mean())  # Calculate average traffic for the month

                        st.markdown(f"""
                            <div class="insights-card" style="background-color: #2c2f38; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                                <h4 style="color: #ff4b4b;">Average Foot Traffic Per Month</h4>
                                <p style="font-size: 20px; font-weight: bold; color: #ffffff;">{avg_traffic_per_month:,} people</p>
                                <p style="color: #94a3b8;">
                                    This represents the average number of people who pass through or visit {selected_place} during a typical month. 
                                    Use this metric to identify busy weeks, plan operations, and optimize performance for a typical month.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)

                        # Convert grouped data into a DataFrame for visualization
                        typical_month_data = monthly_traffic.reset_index()
                        typical_month_data.columns = ['Week of Month', 'Average Foot Traffic']

                        # Plot the typical month data
                        fig = px.line(
                            typical_month_data,
                            x='Week of Month',
                            y='Average Foot Traffic',
                            labels={"Week of Month": "Week of the Month", "Average Foot Traffic": "Average Foot Traffic Volume"},
                            title="",
                            template="plotly_dark",
                        )

                        # Customize the layout
                        fig.update_layout(
                            title={
                                "text": f"Average Foot Traffic by Week for a Typical Month at {selected_place}",
                                "x": 0.5,
                                "xanchor": "center",
                                "yanchor": "top",
                            },
                            title_font_size=20,
                            xaxis_title="Week of the Month",
                            yaxis_title="Average Foot Traffic Volume",
                            font=dict(size=14),
                        )
                        fig.update_traces(
                            line=dict(color="#ff4b4b", width=3),  # Match the red color
                            mode="lines+markers"  # Add markers for better visualization
                        )

                        # Plot the graph in Streamlit
                        st.plotly_chart(fig, use_container_width=True)

                        # Insights and Recommendations
                        busiest_week = monthly_traffic.idxmax()
                        busiest_traffic = int(monthly_traffic.max())
                        quietest_week = monthly_traffic.idxmin()
                        quietest_traffic = int(monthly_traffic.min())

                        st.markdown(f"""
                            <div style="background-color: #2c2f38; padding: 20px; border-radius: 10px; margin-top: 20px;">
                                <h4 style="color: #ff4b4b; text-align: left;">Graph Insights</h4>
                                <p style="color: white;">
                                    <b>Busiest Week:</b> The highest foot traffic occurs during <b>Week {busiest_week}</b>, with an average of <b>{busiest_traffic:,} people</b>.<br>
                                    <b>Quietest Week:</b> The lowest foot traffic occurs during <b>Week {quietest_week}</b>, with an average of <b>{quietest_traffic:,} people</b>.<br>
                                    <b>Average Weekly Traffic:</b> On average, each week sees <b>{avg_traffic_per_month:,} people</b>.
                                </p>
                                <h4 style="color: #ff4b4b; text-align: left;">Recommendations</h4>
                                <ul style="color: white;">
                                    <li>Plan promotions or events during <b>Week {busiest_week}</b> to maximize customer engagement.</li>
                                    <li>Use <b>Week {quietest_week}</b> for staff training, maintenance, or testing new offerings.</li>
                                    <li>Monitor trends during quieter weeks to identify patterns and adjust your marketing strategies.</li>
                                </ul>
                            </div>
                        """, unsafe_allow_html=True)

                elif traffic_option == "Total Foot Traffic Per Year":
                    # Filter data dynamically based on the selected location
                    filtered_data = foot_traffic_data[foot_traffic_data['Business Corridor'] == selected_place]

                    # Ensure there is data for the selected location
                    if filtered_data.empty:
                        st.error(f"No data available for {selected_place}. Please select another location.")
                    else:
                        # Ensure the Date column is in datetime format
                        filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])

                        # Extract the month from the Date column
                        filtered_data['Month'] = filtered_data['Date'].dt.month

                        # Group by month and calculate total foot traffic
                        monthly_traffic = (
                            filtered_data.groupby('Month')['Foot Traffic Volume']
                            .sum()
                            .reset_index()
                        )

                        # Rename columns for clarity
                        monthly_traffic.columns = ['Month', 'Total Foot Traffic']

                        # Map month numbers to month names
                        month_names = {
                            1: 'January', 2: 'February', 3: 'March', 4: 'April',
                            5: 'May', 6: 'June', 7: 'July', 8: 'August',
                            9: 'September', 10: 'October', 11: 'November', 12: 'December'
                        }
                        monthly_traffic['Month'] = monthly_traffic['Month'].map(month_names)

                        # Calculate insights
                        busiest_month = monthly_traffic.loc[monthly_traffic['Total Foot Traffic'].idxmax(), 'Month']
                        busiest_traffic = monthly_traffic['Total Foot Traffic'].max()
                        quietest_month = monthly_traffic.loc[monthly_traffic['Total Foot Traffic'].idxmin(), 'Month']
                        quietest_traffic = monthly_traffic['Total Foot Traffic'].min()
                        avg_monthly_traffic = int(round(monthly_traffic['Total Foot Traffic'].mean()))
                        total_yearly_traffic = monthly_traffic['Total Foot Traffic'].sum()

                        # Header for Yearly Foot Traffic
                        st.markdown(f"""
                            <div class="insights-card" style="background-color: #2c2f38; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                                <h4 style="color: #ff4b4b;">Total Foot Traffic Per Year</h4>
                                <p style="font-size: 20px; font-weight: bold; color: #ffffff;">{total_yearly_traffic:,} people</p>
                                <p style="color: #94a3b8;">
                                    This represents the estimated total number of people who pass through or visit {selected_place} during a typical year. 
                                    Use this metric to understand yearly trends, plan long-term operations, and optimize performance based on annual data.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)

                        # Create a bar chart for monthly foot traffic
                        fig = px.bar(
                            monthly_traffic,
                            x='Month',
                            y='Total Foot Traffic',
                            labels={"Month": "Month", "Total Foot Traffic": "Total Foot Traffic Volume"},
                            title="",
                            template="plotly_dark",
                        )

                        # Update layout for the bar chart
                        fig.update_layout(
                            title={
                                "text": f"Monthly Foot Traffic Trends for {selected_place}",
                                "x": 0.5,
                                "xanchor": "center",
                                "yanchor": "top",
                            },
                            title_font_size=20,
                            xaxis_title="Month",
                            yaxis_title="Total Foot Traffic Volume",
                            font=dict(size=14),
                        )

                        fig.update_traces(marker_color="#ff4b4b")  # Use consistent red color for the bars

                        # Display the chart in Streamlit
                        st.plotly_chart(fig, use_container_width=True)

                        # Add insights below the graph
                        st.markdown(f"""
                            <div style="background-color: #2c2f38; padding: 20px; border-radius: 10px; margin-top: 20px;">
                                <h4 style="color: #ff4b4b; text-align: left;">Graph Insights</h4>
                                <p style="color: white;">
                                    <b>Busiest Month:</b> The highest foot traffic occurs in <b>{busiest_month}</b>, with a total of <b>{busiest_traffic:,} people</b>.<br>
                                    <b>Quietest Month:</b> The lowest foot traffic occurs in <b>{quietest_month}</b>, with a total of <b>{quietest_traffic:,} people</b>.<br>
                                    <b>Average Monthly Traffic:</b> On average, each month sees <b>{avg_monthly_traffic:,} people</b>.
                                </p>
                                <h4 style="color: #ff4b4b; text-align: left;">Recommendations</h4>
                                <ul style="color: white;">
                                    <li>Plan marketing campaigns or special promotions during <b>{busiest_month}</b> to capitalize on increased foot traffic.</li>
                                    <li>Use <b>{quietest_month}</b> for internal process improvements, staff training, or maintenance.</li>
                                    <li>Analyze trends during quieter months to identify potential opportunities for growth.</li>
                                </ul>
                            </div>
                        """, unsafe_allow_html=True)











elif st.session_state.page == "Chatbot":
    st.markdown("<h1 style='color: white;'>Chatbot 🤖</h1>", unsafe_allow_html=True)
    
    # Chatbot description
    st.write("Ask any questions about opening or managing a restaurant in San Jose, and get tailored insights to help you succeed. "
             "Whether you're a beginner or an experienced restaurant owner, our chatbot is here to provide guidance.")

    # Input field and customized button
    user_input = st.text_input("Type your question here:")
    ask_button = st.button("Get Advice")

    if ask_button and user_input:
        try:
            # Enhanced system prompt for detailed and structured responses
            system_prompt = """
                You are a highly intelligent and helpful assistant specializing in restaurant business advice for San Jose.
                Your goal is to provide comprehensive, actionable, and user-friendly insights.

                For every user question:
                1. Interpret the question and infer the user's intention if it is unclear.
                2. Provide a structured response:
                   - **Answer**: Address the user's query directly.
                   - **Examples**: Provide real-world examples or case studies.
                   - **Steps/Actions**: List actionable steps where applicable.
                   - **Pro Tips**: Offer additional insights or expert recommendations.
                   - **Resources**: Share links, statistics, or resources for further exploration.
                3. Guess what related questions the user might have and answer them briefly to preempt follow-ups.
                4. Use your knowledge of San Jose to tailor advice, such as information about popular areas, foot traffic patterns, licensing regulations, and marketing strategies.
                5. Proactively offer tips and address potential challenges the user might not have considered.
                6. Ensure your responses are concise but thorough for maximum clarity.
            """

            # Generate a response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=1024  # Adjust token limit based on desired response length
            )

            # Extract and display the chatbot response
            chatbot_response = response['choices'][0]['message']['content'].strip()
            st.markdown(f"""
                <div style='background-color: #2c2f38; padding: 15px; border-radius: 10px; margin-top: 20px;'>
                    <strong>Chatbot:</strong> {chatbot_response}
                </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error("An error occurred while processing your request.")
            st.write(f"Error details: {e}")
