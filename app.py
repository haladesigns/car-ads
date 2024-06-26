import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


st.header('Car Sales Advertisements')

# Load the dataset  
file_path = './vehicles_us.csv'
df = pd.read_csv(file_path)

#--------------------EDA-----------------# Fill missing values
# ---restore missing data based on related factors (accounting for the relationships within the data)---
df['model_year'] = df['model_year'].fillna(df.groupby(['model'])['model_year'].transform('median'))

# Fill missing 'odometer' values with median of 'model', 'model_year', 'condition', and 'days_listed' group
df['odometer'] = df['odometer'].fillna(
    df.groupby(['model', 'model_year', 'condition', 'days_listed'])['odometer'].transform('median'))

# odometer fallback - fill remaining missing values with the overall median
df['odometer'] = df['odometer'].fillna(df['odometer'].median())

# Fill missing 'cylinders' values with mode of 'model', 'model_year', and 'fuel' group
df['cylinders'] = df['cylinders'].fillna(df.groupby(['model', 'model_year', 'fuel'])['cylinders']
                                         .transform(lambda x: x.mode()[0] if not x.mode().empty else np.nan))

# cylindeers fallback - fill missing values with the overall mode
df['cylinders'] = df['cylinders'].fillna( df['cylinders'].mode()[0])

df['paint_color'] = df['paint_color'].fillna('unknown')

# Fill missing values in 'is_4wd' with 0
df['is_4wd'] = df['is_4wd'].fillna(0)

#-------------------SIDEBAR------------------
# Choose a template
templates = ["plotly", "ggplot2", "seaborn", "simple_white", "none"]

st.sidebar.header("Settings")
my_template = st.sidebar.radio("Choose a template", templates, key="template")

# Set expand_all state based on button clicks
col1, col2 = st.sidebar.columns(2)
with col1: expand_all = st.button("Expand All", key="expandall")
with col2: minimize = st.button("Minimize All", key="minimizeall")

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

text_auto= st.sidebar.checkbox("Enable Histogram text")
 
#-----------------NAVIGATION MENU-------------
selected = option_menu(None, ["Plots", "Correlations", "Contact", ], 
                       icons=['bar-chart', 'arrows-collapse', 'mailbox', ], 
                       menu_icon="cast", default_index=0, orientation="horizontal")

#---------------------PLOTS-------------------

# Separator
st.sidebar.markdown("<hr>", unsafe_allow_html=True)

# Dropdown for selecting the color category
color_category = st.sidebar.selectbox("Select category for scatter plots", [
    'price','model_year','model','condition','cylinders','fuel','odometer',
    'transmission','type','paint_color', 'is_4wd','date_posted','days_listed'], 
                                      key="color_category")

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

expanders = [
    'expand_price', 'expand_odometer', 'expand_days_listed',
    'expand_condition', 'expand_scatter_price_odom',
    'expand_scatter_price_cylinders'
]

# Initialize session state for each expander
for expander in expanders:
    if expander not in st.session_state: st.session_state[expander] = False

# Set expand_all state based on button clicks
if expand_all:
    for expander in expanders: st.session_state[expander] = True
if minimize:
    for expander in expanders: st.session_state[expander] = False

# func to handle the state of the expanders
def create_expander(label, state_key, content_func):
    expander = st.expander(label, expanded=st.session_state[state_key],)
    with expander:
        content_func()
    return expander

# Histogram factory
def create_histogram(df, x, title):
    fig = px.histogram(df, x=x, nbins=30, color='condition', text_auto=text_auto, template=my_template)
    fig.update_traces(textposition='outside')
    fig.update_layout(title_text=title, title_x=0.35)
    st.write(fig)
    
# Scatter plot factory
def create_scatter_plot(df, x, y, title, color):
    fig = px.scatter(df, x=x, y=y, title=title, opacity=0.5, color=color, template=my_template)
    fig.update_layout(title_text=title, title_x=0.35)
    st.write(fig)

# Create histogram functions
def content_hist_price(): 
    """Histogram - Distribution of Vehicle Prices"""
    create_histogram(df, 'price', 'Distribution of Vehicle Prices')

def content_hist_odometer(): 
    """Histogram of Odometer Readings: Visualize the distribution of odometer readings across the dataset."""
    create_histogram(df, 'odometer', 'Distribution of Odometer Readings')

def content_hist_days_listed(): 
    """Histogram of Days Listed: Understand how long vehicles are typically listed for sale."""
    create_histogram(df, 'days_listed', 'Distribution of Days Listed')

def content_hist_condition(): 
    """ Histogram of Vehicle Conditions: Understand the distribution of different vehicle conditions (categorical histogram)."""
    create_histogram(df, 'condition', 'Distribution of Vehicle Conditions')

# Create scatter plot functions
def content_scatter_price_odom(): 
    """Scatter plot of price vs. Odometer Reading"""
    create_scatter_plot(df, 'odometer', 'price', 'Price vs. Odometer Reading', color_category)

def content_scatter_price_cylinders(): 
    """Scatter plot of price vs. cylinder count"""
    create_scatter_plot(df, 'cylinders', 'price', 'Price vs. Cylinder Count', color_category)

# Create expanders
create_expander("Distribution of Vehicle Prices (Histogram)", 'expand_price', content_hist_price)
create_expander("Distribution of Odometer Readings (Histogram)", 'expand_odometer', content_hist_odometer)
create_expander("Days Listed (Histogram)", 'expand_days_listed', content_hist_days_listed)
create_expander("Distribution of Vehicle Conditions (Histogram)", 'expand_condition', content_hist_condition)
create_expander("Price vs. Odometer Reading (Scatter)", 'expand_scatter_price_odom', content_scatter_price_odom)
create_expander("Price vs. Cylinder Count (Scatter)", 'expand_scatter_price_cylinders', content_scatter_price_cylinders)
