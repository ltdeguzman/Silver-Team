import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
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

@st.cache_data
def load_foot_traffic_data(file_path="sanjosefoottrafficdata.csv"):
    return pd.read_csv(file_path)

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
                markdown_table += f"<tr><td><img src='{row['Image URL']}' /></td><td>{row['Location Name']}</td><td>{row['Address']}</td><td>{row['Price Range']}</td><td>{row['Monthly Lease Cost']}</td><td>{row['Yearly Lease Cost']}</td><td>{row['Vacancy Status']}</td></tr>"

            markdown_table += "</table>"
            st.markdown(markdown_table, unsafe_allow_html=True)

            # Select a specific location to display detailed market information
            selected_place = st.selectbox("Learn more about a specific location:", st.session_state['filtered_data']['Location Name'].unique())
            
            if selected_place:
                # Retrieve and display detailed market analysis
                detailed_insights = get_market_details(selected_place)
                st.write(detailed_insights)
                st.divider()  # Add a horizontal line for separation

                # Display foot traffic data if available
                foot_traffic_plaza = foot_traffic_data[foot_traffic_data['Business Corridor'] == selected_place]
                if not foot_traffic_plaza.empty:
                    foot_traffic_plaza['Date'] = pd.to_datetime(foot_traffic_plaza['Date'])
                    foot_traffic_plaza['Month'] = foot_traffic_plaza['Date'].dt.month
                    foot_traffic_grouped_month = foot_traffic_plaza.groupby('Month').agg({'Foot Traffic Volume': 'sum'}).reset_index()
                    foot_traffic_grouped_month['Month'] = foot_traffic_grouped_month['Month'].apply(lambda x: pd.to_datetime(str(x), format='%m').strftime('%B'))

                    # Adjust figure size for a smaller display
                    fig, ax = plt.subplots(figsize=(5, 3))
                    sns.barplot(data=foot_traffic_grouped_month, x='Month', y='Foot Traffic Volume', ax=ax, color="#FF4B4B")
                    ax.set_title(f"Overall Foot Traffic by Month for {selected_place}")
                    ax.set_xlabel('Month')
                    ax.set_ylabel('Total Foot Traffic Volume')
                    ax.get_yaxis().set_major_formatter(mtick.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
                    plt.xticks(rotation=45)

                    # Center the plot by placing it inside a Streamlit column layout
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        st.pyplot(fig)

                    # Add a description below the graph
                    st.write("This graph shows the total foot traffic volume by month for the selected location. "
                             "Higher foot traffic can indicate a greater number of potential customers, which is "
                             "useful for businesses in planning peak hours, marketing efforts, and staffing needs.")

                    st.divider()  # Add a horizontal line for separation

                    # Additional Foot Traffic Insights with Styled Container
                    st.subheader("Overall Foot Traffic Insights")

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

                    # Calculate overall metrics
                    foot_traffic_grouped_day = foot_traffic_plaza.groupby('Date').agg({'Foot Traffic Volume': 'sum'}).reset_index()
                    avg_traffic_per_day = foot_traffic_grouped_day['Foot Traffic Volume'].mean().round().astype(int)
                    avg_traffic_per_week = (avg_traffic_per_day * 7).round().astype(int)
                    total_traffic_per_year = foot_traffic_grouped_month['Foot Traffic Volume'].sum().astype(int)

                    # Display insights with descriptions in a card-style format
                    st.markdown(f"""
                        <div class="insights-card">
                            <h4>Overall Average Foot Traffic Per Day</h4>
                            <p><strong>{avg_traffic_per_day:,} people</strong></p>
                            <p>This is the average number of people who visit the area each day. Understanding daily foot traffic can help businesses plan their daily operations, including staffing and inventory.</p>
                            <br>
                            <h4>Overall Average Foot Traffic Per Week</h4>
                            <p><strong>{avg_traffic_per_week:,} people</strong></p>
                            <p>This metric indicates the average number of visitors each week. It’s useful for identifying peak times throughout the week and adjusting business strategies accordingly.</p>
                            <br>
                            <h4>Total Foot Traffic Per Year</h4>
                            <p><strong>{total_traffic_per_year:,} people</strong></p>
                            <p>This is the total number of visitors over the entire year. Annual foot traffic provides insight into the long-term viability of a location and helps in forecasting potential revenue.</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.write(f"No foot traffic data available for {selected_place}.")

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
            # Update the model to use `gpt-3.5-turbo`
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant providing restaurant business advice for locations in San Jose."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150
            )
            st.markdown(f"<div class='chat-response'><strong>Chatbot:</strong> {response['choices'][0]['message']['content'].strip()}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error("An error occurred while processing your request.")
            st.write(f"Error details: {e}")

