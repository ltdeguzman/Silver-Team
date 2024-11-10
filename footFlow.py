import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

# Set your OpenAI API key (replace with your actual API key)
openai.api_key = "OPENAI_API_KEY"

# Set page config
st.set_page_config(page_title="Foot Flow", layout="wide")

# Load Data
@st.cache_data
def load_data(file_path="sanjosedataset.csv"):
    data = pd.read_csv(file_path)
    return data

@st.cache_data
def load_foot_traffic_data(file_path="sanjosefoottrafficvolume.csv"):
    foot_traffic_data = pd.read_csv(file_path)
    return foot_traffic_data

# Function to get detailed market information using OpenAI
def get_market_details(center_name):
    try:
        # Enhanced prompt for gathering more comprehensive details
        prompt = f"""
        Provide a detailed analysis of the market for the plaza called '{center_name}'. 
        Include the following information:
        1. Pros and cons of the plaza.
        2. Accessibility issues (e.g., parking, public transport access).
        3. Demographics of the types of people or groups who frequent the plaza (e.g., families, young professionals, tourists).
        4. Additional factors or details that a new restaurant owner should consider before deciding to open their business in this plaza, such as foot traffic trends, local competition, and general atmosphere.
        """

        # Use the chat-based model with the correct endpoint
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated model for chat-based completions
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,  # Increase token limit to get detailed responses
            temperature=0.7  # Set temperature for more diverse responses
        )
        
        return response['choices'][0]['message']['content'].strip()  # Return the detailed text

    except openai.error.OpenAIError as e:
        return f"An OpenAI error occurred: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Display title and description
st.title("Foot Flow: Analyzing San Jose Foot Traffic for New Restaurants")
st.write("Explore high-foot-traffic areas in San Jose that best match your restaurant's needs. "
         "Use the options below to narrow down locations based on restaurant type and food preferences.")

# Load data directly from sanjosedataset.csv
data = load_data()

# Load foot traffic data
foot_traffic_data = load_foot_traffic_data()

# Filter required columns
required_columns = ['Location Name', 'Address', 'Cuisine Compatibility', 'Image URL', 'Average Store Size (sq ft)', 'Average Lease Rate ($/sq ft)', 'Price Range', 'Vacancy Status']
if not all(column in data.columns for column in required_columns):
    st.error(f"Dataset is missing one or more required columns: {', '.join(required_columns)}")
else:
    data = data[required_columns]

    # Create columns for dropdown menus
    col1, col2, col3 = st.columns(3)

    # What Kind of Restaurant Selectbox
    with col1:
        restaurant_type = st.selectbox("What kind of restaurant do you want to open?", 
                                        ["Fast Food", "Casual Dining", "Fine Dining", "Cafe", "Buffet", "Food Truck", "Other"])

    # What Kind of Food Multi-Select
    with col2:
        food_types = st.multiselect("What kind of food will you serve?", 
                                    ["Italian", "Mexican", "Chinese", "Indian", "Japanese", "American", "Mediterranean", "Vegan", "Fusion", "Other"])

    # Estimated Startup Cost Dropdown
    with col3:
        startup_costs = st.selectbox("Select your estimated startup costs:", 
                                     ["<$10,000", "$10,000-$50,000", "$50,000-$100,000", "$100,000+"])

    # Square footage input
    # Replace square footage input with a slider
    square_footage = st.slider("Select desired square footage (sq²):", min_value=100, max_value=10000, step=100)


    # Session state for filtered data
    if 'filtered_data' not in st.session_state:
        st.session_state['filtered_data'] = pd.DataFrame()

    # Submit button
    if st.button("Submit"):
        # Clean and filter data based on restaurant type and food types
        filtered_data = data.dropna(subset=['Cuisine Compatibility'])  # Remove rows where 'Cuisine Compatibility' is NaN

        # Apply the filtering logic to check if any selected restaurant type or food type is present in 'Cuisine Compatibility'
        filtered_data = filtered_data[filtered_data['Cuisine Compatibility'].apply(
            lambda x: restaurant_type.lower() in x.lower() or any(food.lower() in x.lower() for food in food_types))
        ]

        # If no matches are found after filtering
        if filtered_data.empty:
            st.write("No matching plazas found. Please adjust your selection criteria.")
        else:
            # Process the filtered data
            filtered_data = filtered_data.dropna().applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # Calculate monthly and yearly lease cost per location
            filtered_data['Monthly Lease Cost'] = filtered_data['Average Lease Rate ($/sq ft)'] * square_footage
            filtered_data['Yearly Lease Cost'] = filtered_data['Monthly Lease Cost'] * 12

            # Format the lease cost columns
            filtered_data['Monthly Lease Cost'] = filtered_data['Monthly Lease Cost'].apply(lambda x: f"${x:,.0f}")
            filtered_data['Yearly Lease Cost'] = filtered_data['Yearly Lease Cost'].apply(lambda x: f"${x:,.0f}")

            # Ensure all plazas are shown by removing duplicate entries
            unique_filtered_data = filtered_data.drop_duplicates(subset=['Location Name'])

            # Reset index to avoid empty index rows in the display
            unique_filtered_data.reset_index(drop=True, inplace=True)

            # Store in session state
            st.session_state['filtered_data'] = unique_filtered_data

    # Render the table only if data exists
    if not st.session_state['filtered_data'].empty:
        markdown_table = "| Image | Center Name | Address | Price Range | Monthly Lease Cost | Yearly Lease Cost | Vacancy Status |\n"
        markdown_table += "|:-----:|:-----------:|:-------:|:-----------:|:------------------:|:-----------------:|:--------------:|\n"

        for index, row in st.session_state['filtered_data'].iterrows():
            markdown_table += f"| <img src='{row['Image URL']}' alt='{row['Location Name']}' width='150' height='150' /> | {row['Location Name']} | {row['Address']} | {row['Price Range']} | {row['Monthly Lease Cost']} | {row['Yearly Lease Cost']} | {row['Vacancy Status']} |\n"

        st.markdown(markdown_table, unsafe_allow_html=True)

    # Ensure the 'Location Name' column is present in filtered data before continuing
    if 'Location Name' not in st.session_state['filtered_data'].columns:
        st.error("The column 'Location Name' is missing from the filtered data.")
    else:
        # Initialize selected_place in session state if not already set
        if 'selected_place' not in st.session_state:
            st.session_state['selected_place'] = None

        # User selects a single center to learn more about
        if not st.session_state['filtered_data'].empty:
            selected_place = st.selectbox(
                "Select a place you want to learn more about:", 
                st.session_state['filtered_data']['Location Name'].unique(), 
                index=0, 
                key='selected_place'
            )

        if st.session_state['selected_place']:
            details = get_market_details(st.session_state['selected_place'])
            st.write(f"### Detailed Information about {st.session_state['selected_place']}")
            st.write(details)

        ### PUT
        ### DATA
        ### HERE

         # Foot Traffic Data for the selected plaza
        foot_traffic_plaza = foot_traffic_data[foot_traffic_data['Business Corridor'] == selected_place]

        if foot_traffic_plaza.empty:
            st.write(f"No foot traffic data available for {selected_place}.")
        else:
            # 1. Foot Traffic by Day per Week
            foot_traffic_grouped_day = foot_traffic_plaza.groupby('Day').agg({'Foot Traffic Volume': 'mean'}).reset_index()

            # Define the correct order for days of the week (Monday to Sunday)
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            foot_traffic_grouped_day['Day'] = pd.Categorical(foot_traffic_grouped_day['Day'], categories=day_order, ordered=True)

            # Sort days by the correct order
            foot_traffic_grouped_day = foot_traffic_grouped_day.sort_values('Day')

            # Plot Foot Traffic by Day
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=foot_traffic_grouped_day, x='Day', y='Foot Traffic Volume', ax=ax)
            ax.set_title(f"Foot Traffic by Day for {selected_place}")
            ax.set_xlabel('Day of the Week')
            ax.set_ylabel('Average Foot Traffic Volume')

            # Format y-axis with commas for readability
            ax.get_yaxis().set_major_formatter(mtick.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

            st.pyplot(fig)

            # 2. Foot Traffic by Weeks of the Month
            # Foot Traffic by Weeks of the Month
            # Convert 'Date' to datetime and extract the week number for the month
            foot_traffic_plaza['Date'] = pd.to_datetime(foot_traffic_plaza['Date'])
            foot_traffic_plaza['Week of Month'] = (foot_traffic_plaza['Date'].dt.day - 1) // 7 + 1  # Week number in the month

            # Restrict week numbers to 4 (i.e., make sure Week 5 does not appear)
            foot_traffic_plaza['Week of Month'] = foot_traffic_plaza['Week of Month'].apply(lambda x: min(x, 4))

            # Group by the week of the month and sum foot traffic volumes
            foot_traffic_grouped_week = foot_traffic_plaza.groupby('Week of Month').agg({'Foot Traffic Volume': 'sum'}).reset_index()

            # Map the week numbers to 'Week 1', 'Week 2', 'Week 3', 'Week 4'
            foot_traffic_grouped_week['Week of Month'] = foot_traffic_grouped_week['Week of Month'].apply(lambda x: f"Week {x}")

            # Plot Foot Traffic by Week of the Month
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=foot_traffic_grouped_week, x='Week of Month', y='Foot Traffic Volume', ax=ax)
            ax.set_title(f"Overall Foot Traffic by Week of the Month for {selected_place}")
            ax.set_xlabel('Week of the Month')
            ax.set_ylabel('Total Foot Traffic Volume')

            # Format y-axis with commas for readability
            ax.get_yaxis().set_major_formatter(mtick.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

            st.pyplot(fig)

            # 3. Calculate Total Foot Traffic Per Year (Text Summary)
            foot_traffic_plaza['Year'] = foot_traffic_plaza['Date'].dt.year
            foot_traffic_grouped_year = foot_traffic_plaza.groupby('Year').agg({'Foot Traffic Volume': 'sum'}).reset_index()

            # Calculate the total foot traffic per year and display as a text summary
            total_traffic_per_year = foot_traffic_grouped_year['Foot Traffic Volume'].sum()

            # Calculate the total foot traffic per week and overall average per week
            foot_traffic_plaza['Week of Year'] = foot_traffic_plaza['Date'].dt.isocalendar().week
            foot_traffic_grouped_week_year = foot_traffic_plaza.groupby('Week of Year').agg({'Foot Traffic Volume': 'sum'}).reset_index()

            # Calculate Overall Average Foot Traffic Per Week
            avg_traffic_per_week = foot_traffic_grouped_week_year['Foot Traffic Volume'].mean().round().astype(int)

            # Section Title for the Overall Graphs
            st.subheader("Overall Foot Traffic Insights")

            # **Overall Average Foot Traffic Per Day**: Calculate and display the average daily foot traffic
            avg_traffic_per_day = foot_traffic_grouped_day['Foot Traffic Volume'].mean().round().astype(int)
            st.write(f"**Overall Average Foot Traffic Per Day:** {avg_traffic_per_day:,} people")  # Formatting with commas

            # **Overall Average Foot Traffic Per Week**: Calculate and display the average weekly foot traffic
            st.write(f"**Overall Average Foot Traffic Per Week:** {avg_traffic_per_week:,} people")  # Formatting with commas

            # **Total Foot Traffic Per Year**: Sum of all foot traffic volumes for the year
            st.write(f"**Total Foot Traffic Per Year:** {total_traffic_per_year:,} people")  # Formatting with commas