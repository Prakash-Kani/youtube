import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from isodate import parse_duration
from pymongo import MongoClient as mc
import numpy as np
from datetime import datetime as dt
import time
import matplotlib.pyplot as plt
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title = "YouTube Data Harvesting Hub",
                   page_icon = "https://cdn.emojidex.com/emoji/seal/youtube.png",
                   layout = "wide",
                   initial_sidebar_state = "expanded",
                   menu_items = None)

st.title(":red[YouTube Data] :blue[Harvesting] and :orange[Warehousing]")#📡
st.subheader('Using :green[Python, MongoDB,SQL and Streamlit]', divider='rainbow')

# Youtube developer console api Connection
api_service_name = os.getenv("API_SERVICE_NAME")
api_version = os.getenv("V3")
api_key = os.getenv("API_KEY")

youtube = build(api_service_name, api_version, developerKey=api_key)

# MongoDB Connection
cloud_client = mc("mongodb+srv://prakashkoffi:1234567890@cluster0.2owrgpr.mongodb.net/?retryWrites=true&w=majority")
# loc = mc('mongodb://localhost:27017')
database = cloud_client['YouTube']
collection = database['YouTube']

# MYSQL Connection
db = mysql.connector.connect(host = 'localhost',
                           user = 'root',
                           password = 'Prakashk14',
                           database = 'youtube')
mycursor = db.cursor(buffered = True)

# The get_channelId function retrieves the channelId associated with a given channel name.
def get_channelId(name):
    request = youtube.search().list(part = "id,snippet",
                                    channelType = 'any',
                                    maxResults = 1,
                                    q = name,)
    response = request.execute()
    
    channelId = response['items'][0]['snippet']['channelId']
    return channelId

# get_alldetails main class retrieve the channel details, videoid details, video details and the comment details associated with a given channel name.
class get_alldetails:
    def __init__(self, youtube, name):
        self.channelId = get_channelId(name)
        self.youtube = youtube
    
    # getchanneldetails fuction retrieves the channel details associated with a given channel id.
    def getchanneldetails(self):
        request = self.youtube.channels().list(
                    part = 'snippet, contentDetails, statistics',
                    maxResults = 1,
                    id = self.channelId
 
                    )
        response = request.execute()
        self.channel_data = dict(ChannelName=response['items'][0]['snippet'].get('title'),
                                 ChannelId = response['items'][0]['id'],
                                 PlayListId = response['items'][0]['contentDetails']['relatedPlaylists'].get("uploads"),
                                 Description = response['items'][0]['snippet'].get('description'),
                                 Country = response['items'][0]['snippet'].get("country", ''),
                                 Views = response['items'][0]['statistics'].get('viewCount', 0),
                                 Subscriber = response['items'][0]['statistics'].get('subscriberCount', 0),
                                 PublishedAt = response['items'][0]['snippet'].get("publishedAt"),
                                 VideoCount = response['items'][0]['statistics'].get('videoCount', 0))

        return self.channel_data
    
    # The "getvideoid" function returns all video ID linked to the specified playlist id.
    def getvideoid(self):
        
        self.playlistid = self.channel_data.get('PlayListId')
        self.video_id = []
        self.Token = None
        while True:
            request = self.youtube.playlistItems().list(
                    part = 'snippet,contentDetails',
                    playlistId = self.playlistid,
                    maxResults = 50,
                    pageToken = self.Token)
            response = request.execute()

            for i in range(len(response['items'])):
                data=dict(VideoId = response['items'][i]['contentDetails']['videoId'],
                          PlayListId = response['items'][i]['snippet']["playlistId"])
                self.video_id.append(data)
            self.Token = response.get('nextPageToken')

            if response.get('nextPageToken') is None:
                break

        return self.video_id
    
     # The getvideodetails function returns the video information related to a particular video id.
    def getvideodetails(self):
        
        self.video_data = []
        for j in self.video_id:

            request = youtube.videos().list(
                                            part = 'snippet,contentDetails,statistics',
                                            id = j['VideoId'],
                                            maxResults = 1
                                            )  
            response = request.execute()


            for i in response['items']:
                duration = response['items'][0]["contentDetails"].get('duration')
                duration1 = (round(parse_duration(duration).total_seconds() / 60,2))

                videodata = dict(VideoTitle = response['items'][0]['snippet'].get('title'),
                                 VideoId = response['items'][0]['id'],
                                 PublishedAt = response['items'][0]['snippet'].get("publishedAt"),
                                 VideoDescription = response['items'][0]['snippet'].get('description', ''),
                                 Thumbnails = response['items'][0]['snippet']['thumbnails']['default'].get('url'),
                                 CategoryId = response['items'][0]['snippet'].get("categoryId"),
                                 Caption = response['items'][0]["contentDetails"].get('caption'),
                                 Dimension = response['items'][0]["contentDetails"].get('dimension', ''),
                                 Definition = response['items'][0]["contentDetails"].get('definition',''),
                                 Tags = ' '.join(response['items'][0]['snippet'].get('tags', ' ')),
                                 Views = response['items'][0]['statistics'].get('viewCount', 0),
                                 LikeCount = response['items'][0]['statistics'].get('likeCount', 0),
                                 DislikeCount = response['items'][0]['statistics'].get('dislikeCount', 0),
                                 Duration = duration1,
                                 FavoriteCount = response['items'][0]['statistics'].get("favoriteCount", 0),
                                 CommentCount = response['items'][0]['statistics'].get('commentCount', 0))
                self.video_data.append(videodata)

        return self.video_data
    
     # The function getcommentdetails collects the comment information related to a particular video id. Handling of exceptions for videos with disabled comments.
    def getcommentdetails(self):

        self.comment_details = []
        for j in self.video_id:
            try:
                Token = None
                while True:
                    request = youtube.commentThreads().list(
                            part = "snippet",
                            videoId = j['VideoId'],
                            maxResults = 100,
                            pageToken = Token

                        )
                    response = request.execute()


                    for i in range(len(response['items'])):
                        data = dict(VideoId = response['items'][i]['snippet'].get('videoId'),
                                  AuthorDisplayName = response['items'][i]['snippet']['topLevelComment']['snippet'].get('authorDisplayName'),
                                  CommentId = response['items'][i]['snippet']['topLevelComment'].get('id'),
                                  PublishedAt = response['items'][i]['snippet']['topLevelComment']['snippet'].get('publishedAt'),
                                  LikeCount = response['items'][i]['snippet']['topLevelComment']['snippet'].get('likeCount', 0),
                                  DislikeCount = response['items'][i]['snippet']['topLevelComment']['snippet'].get('dislikeCount',0),
                                  Text = response['items'][i]['snippet']['topLevelComment']['snippet'].get('textOriginal'),
                                  TotalReplyCount = response['items'][i]['snippet'].get('totalReplyCount', 0))

                        self.comment_details.append(data)

                        Token = response.get('nextPageToken')

                    if response.get('nextPageToken') is None:
                        break

            except:
                pass
        return self.comment_details

# The get_all function allows you to get all channel data through the main class associated with the channel name.
def get_all(name):
    channel = get_alldetails(youtube, name)
    alldetails = {'channeldata': channel.getchanneldetails(),
                  'videoiddata': channel.getvideoid(),
                  'videodata': channel.getvideodetails(),
                  'commentdata': channel.getcommentdetails()}
    return alldetails  

# The push_mongodb function inserts channel data from the channel name input into mongoDB.
def push_mongoDB(name):
    data = get_all(name)
    collection.insert_one(data)
    return 'datas are inserted collection is YouTube!'

# For a certain query, the dataclean function retrieves the relevant mongoDB data and separates the channel information, video id details, video details, and comment details. After that, data cleaning took place.
def dataclean(query):
    channeldetails, playlistid, videodetails, commentdetails = [], [], [], []

    for i in collection.find(query,{'_id':0}):
        channeldetails.append(i['channeldata'])
        playlistid.extend(i['videoiddata'])
        videodetails.extend(i['videodata'])
        commentdetails.extend(i['commentdata'])
        
    channel = pd.DataFrame(channeldetails)
    play = pd.DataFrame(playlistid)
    video = pd.DataFrame(videodetails)
    comment = pd.DataFrame(commentdetails)
    
    channel['Views'] = pd.to_numeric(channel['Views'])
    channel['Subscriber'] = pd.to_numeric(channel['Subscriber'])
    channel['VideoCount'] = pd.to_numeric(channel['VideoCount'])
    channel['PublishedAt'] = pd.to_datetime(channel['PublishedAt']).dt.date

    video['Views'] = pd.to_numeric(video['Views'])
    video['CommentCount'] = pd.to_numeric(video['CommentCount'])
    video['LikeCount'] = pd.to_numeric(video['LikeCount'])
    video['DislikeCount'] = pd.to_numeric(video['DislikeCount'])
    video['FavoriteCount'] = pd.to_numeric(video['FavoriteCount'])
    video['Duration'] = pd.to_numeric(video['Duration'])
    video['PublishedAt'] = pd.to_datetime(video['PublishedAt'])
    
    comment['LikeCount'] = pd.to_numeric(comment['LikeCount'])
    comment['DislikeCount'] = pd.to_numeric(comment['DislikeCount'])
    comment['TotalReplyCount'] = pd.to_numeric(comment['TotalReplyCount'])
    comment['PublishedAt'] = pd.to_datetime(comment['PublishedAt'])
  
    return(channel, play,video, comment)


#code for Direct insert 

# from sqlalchemy import create_engine
# engine = create_engine("mysql+mysqlconnector://root:Prakashk14@localhost/youtube")
# curs = engine.connect()
# channel.to_sql('channeldetails', if_exists = 'append', index = False, con = engine)
# play.to_sql('playlistiddetails', if_exists = 'append', index = False, con = engine)
# comment.to_sql('commentdetails', if_exists = 'append', index = False, con = engine)
# video.to_sql('videodetails', if_exists = 'append', index = False, con = engine)


# migrate mongoDB data into MYSQL database. It is possible to migrate MongoDB channel details without creating duplicate values in MySQL.
def migrate_to_mysql(query):
    channel, play, video, comment = dataclean(query)

    #channeldetails
    mycursor.execute("select ChannelId from channeldetails")
    data5 = mycursor.fetchall()
    storedchannel = [i[0] for i in data5]

    data1 = channel['ChannelId'].tolist()

    YetToChannel = [i for i in data1 if i not in storedchannel]
    filter1 = channel['ChannelId'].isin(YetToChannel)
    newchannel = channel[filter1]

    newchannelrow = list(zip(newchannel['ChannelName'], newchannel['ChannelId'], newchannel['PlayListId'],
                           newchannel['Description'], newchannel['Country'], newchannel['Views'], newchannel['Subscriber'],
                           newchannel['PublishedAt'], newchannel['VideoCount']))
    sql1 = "INSERT INTO channeldetails VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    mycursor.executemany(sql1, newchannelrow)
    db.commit()

    #play list id 
    mycursor.execute("select PlayListId from playlistiddetails")
    data6 = mycursor.fetchall()
    storedplay = [i[0] for i in data6]

    data2 = play['PlayListId'].tolist()

    YetToPlay = [i for i in data2 if i not in storedplay]
    filter2 = play['PlayListId'].isin(YetToPlay)
    newplay = play[filter2]
    newplayrows = list(zip(newplay['VideoId'], newplay['PlayListId']))
    sql2 = "INSERT INTO playlistiddetails VALUES (%s, %s)"
    mycursor.executemany(sql2, newplayrows)
    db.commit()

    #video Details 
    mycursor.execute("select VideoId from videodetails")
    data7 = mycursor.fetchall()
    storedvideo = [i[0] for i in data7]

    data3 = video['VideoId'].tolist()

    YetToVideo = [i for i in data3 if i not in storedvideo]
    filter3 = video['VideoId'].isin(YetToVideo)
    newvideo = video[filter3]

    newvideorows = list(zip(newvideo['VideoTitle'], newvideo['VideoId'], newvideo['PublishedAt'], newvideo['VideoDescription'],
                          newvideo['Thumbnails'], newvideo['CategoryId'], newvideo['Caption'], newvideo['Dimension'],
                          newvideo['Definition'], newvideo['Tags'], newvideo['Views'], newvideo['LikeCount'],
                          newvideo['DislikeCount'], newvideo['Duration'], newvideo['FavoriteCount'], newvideo['CommentCount']))

    sql3 = "INSERT INTO videodetails VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    mycursor.executemany(sql3,newvideorows)
    db.commit()

    #comment Details
    mycursor.execute("select VideoId from commentdetails")
    data8 = mycursor.fetchall()
    storedcomment = [i[0] for i in data8]
  
    data4 = comment['VideoId'].tolist()

    YetToComment = [i for i in data4 if i not in storedcomment]
    filter4 = comment['VideoId'].isin(YetToComment)
    newcomment = comment[filter4]

    newcommentrows = list(zip(newcomment['VideoId'], newcomment['AuthorDisplayName'], newcomment['CommentId'],
                            newcomment['PublishedAt'], newcomment['LikeCount'], newcomment['DislikeCount'], newcomment['Text'],
                            newcomment['TotalReplyCount'],))

    sql4 = "INSERT INTO commentdetails VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    mycursor.executemany(sql4,newcommentrows)
    db.commit()
    return 'data inserted done!'

# Streamlit webapp
st.sidebar.title(":red[YouTube Data Hub]")
inp = st.sidebar.selectbox("**Data Operations**", ["Select Operation", 'Fetch Channel Data', 'View Channel Details', 'Migrate Data to MYSQL Warehouse',
                                   'MYSQL Query Results', 'Direct MySQL Query', 'Feedback'])
st.sidebar.markdown(""":blue[Welcome to the ***YouTube Data Hub*** an all-in-one solution for harvesting, storing, and analyzing YouTube data. 
                    Use the options above to explore channel details, migrate data, query your database, and more.]""")
# Front page of my webapp
if inp == 'Select Operation':
    st.title(":blue[***Welcome to Your YouTube Data Hub***]")
    st.markdown("""Welcome to our **YouTube Data Harvesting** application. Here, you can seamlessly fetch YouTube channel data, 
                explore comprehensive channel details, and migrate data to a MYSQL warehouse. Whether you need to retrieve specific channel 
                information or perform custom MYSQL queries, our app offers versatile tools to help you extract insights and make data-driven decisions.""")
    st.subheader(":green[Use the options below to interact with your data]")
    st.markdown("""- **Fetch Channel Data:** Retrieve information about YouTube channels.
                \n- **View Channel Details:** Explore detailed channel information.
                \n- **Migrate Data to MYSQL Warehouse:** Transfer data to your MySQL data warehouse.
                \n- **MYSQL Query Results:** Perform SQL queries and view results.
                \n- **Direct MySQL Query:** Write and execute custom MySQL queries.
                                
                \n***Please select an operation and get started with your data analysis journey!***""")
    
# Fetch Channel Data: Retrieve information about YouTube channels.
elif inp == 'Fetch Channel Data':
    name = st.text_input('**Enter the Channel Name**')
    execute = st.button("Get Channel Details")
    if execute == False:
        st.header(':blue[***Fetch Channel Data***]')
        st.markdown("""With this option, users can input the YouTube channel name and initiate the data retrieval process by clicking 
                    the **"Get Channel Details"** button. The app will fetch and store comprehensive data, including channel information,
                    video IDs, video details, and comments associated with the channel's videos, all neatly organized in the MongoDB database.""")
    elif name and execute:
        with st.spinner('Please wait '):
                data1=push_mongoDB(name)
                if data1:
                    st.success('Done!, Data Fetched Successfully')

# View Channel Details to see the details of the stored channels in MongoDB.
elif inp == 'View Channel Details':
    channelname = st.selectbox('select ChannelName', [i['channeldata']['ChannelName'] for i in collection.find()])
    if channelname:
        query = {'channeldata.ChannelName':channelname}
        tab1, tab2, tab3, tab4, tab5 = st.tabs(['View Channel Details', 'ChannelDetails', 'VideoIdDetails', 'VideoDetails', 'CommentDetails'])
        with tab1:
            st.header(':blue[***View Channel Details***]')
            st.markdown("""This option enables users to explore comprehensive YouTube channel information stored in the MongoDB database.
                            Users can input the YouTube channel name, and the app will retrieve and display details including **channel information,
                            video IDs, video details, and comments associated with that channel's videos**. Dive deep into the channel's content with ease.""")
        with tab2:
            st.header(':blue[Channel Details]')
            for i in collection.find(query):
                st.dataframe(i['channeldata'])
        with tab3:
            st.header(':blue[Video Id Details]')
            for i in collection.find(query):
                df6 = pd.DataFrame(i['videoiddata'])
            st.dataframe(df6.head(100))
        with tab4:
            st.header(':blue[Video Details]')
            for i in collection.find(query):
                df7 = pd.DataFrame(i['videodata'])
            st.dataframe(df7.head(500))
        with tab5:
            st.header(':blue[Comment Details]')
            for i in collection.find(query):
                df8 = pd.DataFrame(i['commentdata'])
            st.dataframe(df8.head(1000))

 # Transfer information from the MongoDB database to MySQL data warehouse.
elif inp == 'Migrate Data to MYSQL Warehouse':
    mode = st.selectbox('Select the Method of Migration',["Select the Mode of Migration", "Default Migration", "Selective Migration"])
    if mode == 'Select the Mode of Migration':
        sql = False
        st.markdown('**Default Migration**:  Fetches and migrates all channel data from MongoDB to MySQL for comprehensive synchronization.')
        st.markdown('**Selective Migration**: Enables the selection of specific channels from MongoDB for targeted migration to MySQL.')
    elif mode == "Default Migration":
        query = {}
        st.write('Click the below button to migrate records into MYSQL')
        sql = st.button("Migrate Data")
    elif mode == "Selective Migration":
        sql = False
        channelname = st.multiselect('select ChannelName', [i['channeldata']['ChannelName'] for i in collection.find()])
        if channelname:
            query = {'channeldata.ChannelName':{'$in':channelname}}
            st.write('Click the below button to migrate records into MYSQL')
            sql = st.button("Migrate Data")
 
    if sql == False:
        st.header(':blue[***Migrate Data to MYSQL Warehouse***]')
        st.markdown("""The "Migrate Data to MYSQL Warehouse" functionality streamlines the process of transferring data from MongoDB databases
                     into a MYSQL warehouse. Whether you prefer comprehensive data migration or selective transfers, this option offers versatility.
                     By seamlessly synchronizing databases, it ensures that your data is readily available for structured analysis and actionable insights.""")
    elif sql:
        with st.spinner('Please wait '):
            merge = migrate_to_mysql(query)
            st.success('Done!, Data Migration Successfully')

# MySQL query for 10 frequently asked questions.
elif inp == 'MYSQL Query Results':
    question = st.selectbox("**Select Questions**",
                            ['Click the question that you would like to query',
                            '1. What are the names of all the videos and their corresponding channels?',
                            '2. Which channels have the most number of videos, and how many videos do they have?',
                            '3. What are the top 10 most viewed videos and their respective channels?',
                            '4. How many comments were made on each video, and what are their corresponding video names?',
                            '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                            '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                            '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                            '8. What are the names of all the channels that have published videos in the year 2022?',
                            '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                            '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])
    
    if question == 'Click the question that you would like to query':
        st.header(':blue[***MYSQL Query Results***]') 
        st.markdown("""This option allows you to interactively query YouTube data using a variety of predefined queries. 
                    Simply select a query of interest, and the results will be displayed as a user-friendly table within 
                    the Streamlit application. Explore valuable insights and statistics about videos, channels, likes, views, comments, and more.""")
    
    elif question == '1. What are the names of all the videos and their corresponding channels?':
        st.write(question)
        mycursor.execute("""select channeldetails.ChannelName,  videodetails.VideoTitle from channeldetails INNER JOIN
                        playlistiddetails ON channeldetails.PlayListId=playlistiddetails.PlayListId INNER JOIN videodetails
                        ON videodetails.VideoId=playlistiddetails.VideoId;""")
        data = mycursor.fetchall()
        df = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
        st.dataframe(df)
    elif question == '2. Which channels have the most number of videos, and how many videos do they have?':
        st.write(question)
        mycursor.execute("""select ChannelName, VideoCount from ChannelDetails
                        where VideoCount=(select max(VideoCount)from ChannelDetails);""")
        data = mycursor.fetchall()
        df1 = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
        st.dataframe(df1)
    elif question == '3. What are the top 10 most viewed videos and their respective channels?':
        st.write(question)
        mycursor.execute("""select channeldetails.ChannelName, video.VideoTitle, video.Views from channeldetails INNER JOIN
                        playlistiddetails ON channeldetails.PlayListId=playlistiddetails.PlayListId INNER JOIN (
                        select VideoTitle, Views, CommentCount,VideoId from videodetails ORDER BY Views desc LIMIT 10) video 
                        ON video.VideoId=playlistiddetails.VideoId ORDER BY Views desc;""")

        data = mycursor.fetchall()
        df3 = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
        st.dataframe(df3)
    elif question == '4. How many comments were made on each video, and what are their corresponding video names?':
        st.write(question)
        mycursor.execute("""select VideoTitle, Views, CommentCount from videodetails ORDER BY Views desc;""")
        data = mycursor.fetchall()
        df4 = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
        st.dataframe(df4)

    elif question == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        st.write(question)
        mycursor.execute("""select channeldetails.ChannelName, video.VideoTitle, video.LikeCount from channeldetails INNER JOIN
                        playlistiddetails ON channeldetails.PlayListId=playlistiddetails.PlayListId INNER JOIN (
                        SELECT * FROM videodetails WHERE LikeCount=(SELECT max(LikeCount) FROM videodetails)) video ON 
                        video.VideoId=playlistiddetails.VideoId;""")
        data = mycursor.fetchall()
        df5 = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
        st.dataframe(df5)
    elif question == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        st.write(question)
        mycursor.execute("""SELECT VideoTitle, LikeCount, DislikeCount FROM videodetails;""")
        data = mycursor.fetchall()
        df6 = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
        st.dataframe(df6)
    elif question == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        st.write(question)
        mycursor.execute("""select channeldetails.ChannelName, sum(videodetails.Views) as TotalViews from channeldetails inner join 
                        playlistiddetails on playlistiddetails.PlayListId= channeldetails.PlayListId inner join 
                        videodetails on videodetails.VideoId=playlistiddetails.VideoId group by ChannelName;""")
        data = mycursor.fetchall()
        df7 = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
        df7['TotalViews'] = df7['TotalViews'].astype(int)
        st.dataframe(df7)

        # st.bar_chart(df7,x='ChannelName' , y='TotalViews') 
    elif question == '8. What are the names of all the channels that have published videos in the year 2022?':
        st.write(question)
        mycursor.execute(""" SELECT DISTINCT channeldetails.ChannelName FROM channeldetails INNER JOIN playlistiddetails ON channeldetails.PlayListId = playlistiddetails.PlayListId
                        INNER JOIN videodetails ON playlistiddetails.VideoId = videodetails.VideoId
                        WHERE YEAR(videodetails.PublishedAt) = 2022;""")
        data = mycursor.fetchall()
        df8 = pd.DataFrame(data, columns=[i[0] for i in mycursor.description])
        st.dataframe(df8)
    elif question == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        st.write(question) 
        mycursor.execute("""select channeldetails.ChannelName, AVG(videodetails.Duration) as AverageDuration from channeldetails inner join
                        playlistiddetails on playlistiddetails.PlayListId= channeldetails.PlayListId inner join videodetails 
                        on videodetails.VideoId=playlistiddetails.VideoId group by channeldetails.ChannelName;""")
        data = mycursor.fetchall()
        df9 = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
        st.dataframe(df9)   
        st.bar_chart(df9,x='ChannelName' , y='AverageDuration') 
    elif question == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        st.write(question)
        mycursor.execute("""select channeldetails.ChannelName, video.VideoTitle, video.CommentCount from channeldetails INNER JOIN
                        playlistiddetails ON channeldetails.PlayListId=playlistiddetails.PlayListId INNER JOIN (
                        SELECT VideoId,VideoTitle, CommentCount FROM videodetails where CommentCount =( select max(CommentCount) as max FROM 
                        videodetails)) video ON video.VideoId=playlistiddetails.VideoId;""")
        data = mycursor.fetchall()
        df10 = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
        st.dataframe(df10) 
# Direct MySQL Query
elif inp == 'Direct MySQL Query':
    query = st.text_area('**Enter your own query**')
    query = query.lower()
    result = st.button( "Retrieve Data")
    if result == False:
        mycursor.execute("DESCRIBE channeldetails")
        data1 = mycursor.fetchall()
        mycursor.execute("DESCRIBE playlistiddetails")
        data2 = mycursor.fetchall()
        mycursor.execute("DESCRIBE videodetails")
        data3 = mycursor.fetchall()
        mycursor.execute("show columns from commentdetails")
        data4 = mycursor.fetchall()
        if st.button('Table Reference'):
            tab1, tab2, tab3, tab4 = st.tabs(['ChannelDetails','PlayListIdDetails','VideoDetails','CommentDetails'])
            st.write("""Refer to the below tables for guidance, where title is represented as the table name,
                      and their corresponding column names are provided as row values.""")
            with tab1:
                st.header(':blue[ChannelDetails]')
                data1 = [i[0] for i in data1]
                st.dataframe(pd.DataFrame(data1, columns = ['Column Name']))  
            with tab2:
                st.header(':blue[PlayListIdDetails]')
                data2 = [i[0] for i in data2]
                st.dataframe(pd.DataFrame(data2, columns = ['Column Name']))
            with tab3:
                st.header(':blue[VideoDetails]')
                data3 = [i[0] for i in data3]
                st.dataframe(pd.DataFrame(data3, columns = ['Column Name']))
            with tab4:
                st.header(':blue[CommentDetails]')
                data4 = [i[0] for i in data4]
                st.dataframe(pd.DataFrame(data4, columns = ['Column Name']))

        st.header(':blue[***Direct MySQL Query***]')
        st.markdown("""Empower your data exploration with direct MySQL queries. Craft your own SQL queries for analysis and insights.
                     Input your custom query and click the "**Retrieve Data**" button. The results will be displayed for your exploration. Please
                     note that you have read-only access (DQL). Any attempt to perform other query types will result in an "Access Denied" message.""")
    elif query and result and 'select' in query:
        try:
            mycursor.execute(query)
            data = mycursor.fetchall() 
            df = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
            st.dataframe(df)
        except Exception as e:
            st.write(e)
            st.error('Error Occurred', icon="🚨")
            st.write('Please review your query and check for any syntax or logic errors.')
    elif query and result and 'select' not in query:
        st.warning('Access Denied', icon="⚠️")
# Feedback
elif inp == 'Feedback':
    st.header(':blue[***Feedback Form***]')
    FName = st.text_input('**Enter your First Name**')
    LName = st.text_input('**Enter your Last Name**')
    Mobile = st.text_input('**Enter your Mobile Number**')
    Feedback = st.text_area('**Enter your Feedback**')
    submit = st.button('Submit Feedback')
    if FName and LName and Mobile and Feedback:
        data = {'First_Name':FName, 'Last_Name':LName, 'Mobile Number':Mobile, 'Feedback': Feedback, 'PublishedAt':dt.now()}
        if submit and data:
            collection = database.Feedback
            collection.insert_one(data)
            st.success("Thank you for your feedback!")
        else:
            st.warning("Please enter your feedback before submitting.")