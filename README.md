# YouTube Data Harvesting Hub
___

## Problem Statement
___
  YouTube is a vast platform where countless creators and viewers worldwide engage with a wide range of videos. This project focuses on extracting specific YouTube channel data using unique channel IDs, processing and structuring this data and efficiently storing it in a MongoDB database. The application streamlines the data transfer from MongoDB to MySQL, enabling further analysis. Users can effortlessly inquire about the data and receive detailed insights based on their queries, simplifying data analysis and decision-making.

## Required Libraries to Install
___
- **Streamlit:** A powerful Python library for creating web apps with minimal code.
   -      pip install streamlit
- **Google API Client:** Used for connecting to the YouTube API and retrieving data.
   -      pip install google-api-python-client
- **MySQL Connector:** Enables communication with MySQL databases for data storage and retrieval.
   -      pip install mysql-connector-python
- **Pymongo:** Provides a Python driver for MongoDB, allowing you to work with NoSQL data.
   -      pip install pymongo
- **Pandas:** Used for data cleaning and manipulation.
   -      pip install pandas
- **Isodate:** Helps parse video durations from YouTube data.
   -      pip install isodate
- **NumPy:** Essential for numerical operations and data handling.
   -      pip install numpy
- **Matplotlib:** A popular library for creating data visualizations.
  -       pip install matplotlib

## Example Import Statements

Here are the import statements you'll need in your Python program to use these libraries:

```
# For Streamlit app
import streamlit as st

# For Google API
from googleapiclient.discovery import build

# For MySQL database
import mysql.connector
from sqlalchemy import create_engine

# For MongoDB
from pymongo import MongoClient as mc

# For data manipulation and analysis
import pandas as pd

# For parsing YouTube video durations
from isodate import parse_duration

# For creating plots or visualizations
import matplotlib.pyplot as plt
```

## ETL Process
### 1. Channel Identification
- Our process begins with users inputting the name of a YouTube channel. Next, we utilize the YouTube API developer console to discover the unique channel ID, a crucial identifier.
### 2. Data Extraction Mastery
- Once we obtain the channel ID, we seamlessly transition to the "Extraction" phase. During this step, we selectively retrieve specific channel data using the channel ID. This data is then expertly converted into a user-friendly JSON format.
### 3. Data Repository Options
- After the transformation, we securely store this valuable data in a MongoDB database. But that's not all! We also provide the option to transfer this data to a MySQL database


## Exploration and Data Analysis Process and Framework
### 1. Access MySQL Database
Establish a connection to the MySQL server and access the designated MySQL database using the MySQL Connector. Navigate through the database tables.

### 2. Data Filtering
Refine and manipulate the collected data from the tables based on specified requirements through SQL queries. Transform this processed data into a DataFrame format.

### 3. Visual Representation
Conclude by constructing a user-friendly dashboard with Streamlit. Provide dropdown menu options for users to choose from. Select a question from this menu to analyze the data and display the results in both a DataFrame Table and Bar Chart.

## Streamlit User Guide

## Features
### Fetch Channel Data
- Easily retrieve information about YouTube channels by entering the channel name. Click the "Get Channel Details" button to initiate data retrieval.

### View Channel Details
- Explore comprehensive YouTube channel information, including video details and comments.

### Migrate Data To MYSQL Warehouse
- Seamlessly transfer and synchronize data between databases, such as MongoDB and MySQL.

### MYSQL Query Results
- Perform MYSQL queries and view results in user-friendly tables for data analysis.

### Direct MySQL Query
- Craft and execute custom MySQL queries for more advanced data exploration.


## Getting Started
- Let's kick things off by cloning this repository to your local machine.
- Next, you'll need to input your API key and set up connections with MongoDB and MySQL.
- Ensure that you've installed all the required Python libraries listed under the "Required Libraries to Install" section.
- Now, execute the following command to launch the Streamlit app: streamlit run app.py.
- Once it's up and running, follow the on-screen instructions to dive into the world of YouTube data.
