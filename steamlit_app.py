# Import python packages.
import streamlit as st
from snowflake.snowpark.functions import col
import requests  

# Write directly to the app.
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw: ")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake and get session
cnx = st.connection("snowflake")
session = cnx.session()

# Select both FRUIT_NAME and SEARCH_ON columns
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multiselect widget for ingredients, using FRUIT_NAME for options
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ''
  
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get API-friendly search_on value from DataFrame
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')

        # Use search_on.lower() for the API call
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on.lower())
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
    st.write(my_insert_stmt)
   
    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
