import pandas as pd
import emoji
import time as T
import re, os
import numpy as np
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import calendar
import time
import plotly.graph_objects as go
# from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from collections import Counter
import streamlit as st
import plotly.io as pio
import csv
import nltk_stopword
from nltk.corpus import stopwords
import wordcloud
import nltk_stopword

# nltk.download('stopwords')
stop_words_sp = set(stopwords.words('spanish'))
pio.templates.default = 'plotly'
def extract_chat_info(chat):
    chat_info = []
    lines = chat
    for row in lines:
        row = row.split()
        cur_row = " ".join([str(item) for item in row])
        if re.search(r"(\d{1,}/\d{2}/\d{2},) (\d{1,2}\:\d{1,2}\:\d{1,2})",cur_row) is None:
            chat_info[-1]['Message'] = chat_info[-1]['Message'] + cur_row
            # print()
            continue
        # print(cur_row)
        # print(re.search(r"(\d{1,}/\d{2}/\d{2})  (\d{1,2}\:\d{1,2}\:\d{1,2})",cur_row))
        date_time = dt.datetime.strptime(re.search(r"(\d{1,}/\d{2}/\d{2},) (\d{1,2}\:\d{1,2}\:\d{1,2})",cur_row).group(),'%d/%m/%y, %H:%M:%S')
        date = re.search(r"(\d{1,}/\d{2}/\d{2})", cur_row).group()
        time = re.search(r"(\d{1,2}\:\d{1,2}\:\d{1,2}\s)(AM|PM)",cur_row).group()
        DayOfWeek = date_time.strftime('%a')
        Contact = str(re.search(r"\]( [^\:]+)",cur_row).group())[2:]
        Message= str(re.search(r'\:\s(.*)',cur_row).group())[2:]
            
        chat_info.append({
            'Date': date,
            'Time': time,
            'DayOfWeek': DayOfWeek,
            'Contact': Contact,
            'Message': Message
        })
            
    df = pd.DataFrame(chat_info)
    return df
def chat_processing(chat):
    
    chat["Words"] = chat.apply(lambda x: len(x["Message"].split()) ,axis=1)
    chat["Length"] = chat.apply(lambda x: len(x["Message"]) ,axis=1)
    chat[['Time', 'Timez']] = chat["Time"].apply(lambda x: pd.Series(str(x).split(" ")))
    chat['Date'] = chat['Date'].apply(lambda x: (str(x))[:10])
    chat['Datetime'] = pd.to_datetime(chat['Date'] + ' ' + chat['Time'])
    chat['Time'] = pd.to_datetime(chat['Time'],format= '%H:%M:%S' ).dt.time
    chat['Date'] = pd.to_datetime(chat['Date']).dt.date
    delta = dt.timedelta(hours = 12)
    chat['Datetime'] = np.where((chat['Timez'] == 'PM') & (chat['Datetime'].dt.hour != 12) ,chat['Datetime'] + delta,chat['Datetime']) 
    chat['Datetime'] = np.where((chat['Timez'] == 'AM') & (chat['Datetime'].dt.hour == 12),chat['Datetime'] - delta,chat['Datetime'])
    contacts = chat.Contact.unique()
    chat['prev_group'] = chat['Contact'].shift(1)
    # create a Boolean column that indicates when 'group' changes between two consecutive rows
    chat['group_change'] = np.where(chat['Contact'] != chat['prev_group'], True, False)
    # create a new data frame that includes only rows where 'group' changes
    group_changes = chat[chat['group_change']]
    group_changes['Time_to_respond_mins'] = group_changes.Datetime.diff().astype('timedelta64[m]')
    group_changes['Time_to_respond_secs'] = group_changes.Datetime.diff().astype('timedelta64[s]')
    chat = pd.merge(chat, group_changes[['Time_to_respond_secs','Time_to_respond_mins']],left_index=True,right_index=True,how='left')
    chat.drop(['prev_group','group_change'],axis=1,inplace=True)
    chat['Emojis'] = chat['Message'].apply(lambda x: emoji.distinct_emoji_list(x))
    chat.drop(chat[chat.Datetime.dt.year > dt.date.today().year].index, inplace = True)
    chat.drop(chat[chat.Datetime.dt.year < dt.datetime(2000, 5, 17).year].index, inplace = True)
    return chat,contacts
def create_graphs(df):
    # Data for pie chart with years
    pie_data=pd.DataFrame(df.groupby([df.Datetime.dt.year,'Contact']).agg({'Message':'count'}).reset_index())
    fig_pie = px.pie(pie_data,values='Message',names = 'Contact',title='Total Messages per Contact')
    # Data for messages over time and plot
    msg_over_time_df = df
    msg_over_time_df['Year_month'] = msg_over_time_df['Datetime'].apply(lambda x:x.strftime("%Y-%m"))
    msg_over_time_df= pd.DataFrame(msg_over_time_df.groupby(['Year_month','Contact']).agg({'Message':'count'}).reset_index())
    fig_msg_over_time = px.line(msg_over_time_df, x="Year_month", y="Message", color='Contact',markers=True,title='Messages over time')
    # Media files data and plot
    # Map media files
    df['Audio'] = df['Message'].apply(lambda x: 1 if x.strip() == '\u200eaudio omitted' else 0 )
    df['Sticker'] = df['Message'].apply(lambda x: 1 if x.strip() == '\u200esticker omitted' else 0 )
    df['Image'] = df['Message'].apply(lambda x: 1 if x.strip() == '\u200eimage omitted' else 0 )
    df['Video'] = df['Message'].apply(lambda x: 1 if x.strip() == '\u200evideo omitted' else 0 )
    df['Media'] = df.apply(lambda x: 1 if x.Audio + x.Sticker + x.Image + x.Video >0 else 0 ,axis= 1)
    # Usage of media
    media_usage = df.groupby('Contact')['Audio','Sticker','Image','Video','Media'].agg({'Audio':'sum','Sticker':'sum','Image':'sum','Video':'sum','Media':'sum'}).reset_index()
    media_usage = pd.melt(media_usage,id_vars='Contact')
    fig_media = px.bar(media_usage,x='variable', y= 'value', color = 'Contact',barmode="group",title= 'Media usage')
    # Most messages per month
    msg_per_month = df
    msg_per_month['Month'] = msg_per_month['Datetime'].apply(lambda x:x.strftime("%B"))
    line_data=pd.DataFrame(msg_per_month.groupby(['Month']).agg({'Message':'count'}).reset_index())
    fig_message_month = px.bar(line_data, x="Month", y="Message",title = 'Messages per month (total)')
    fig_message_month.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
    # Boxplot by day of the week
    boxplot_data = pd.DataFrame(df.groupby(['Date','Contact']).agg({'Message':'count'}).reset_index())
    boxplot_data['Day'] = boxplot_data['Date'].apply(lambda x: x.strftime('%A'))
    fig_boxplot = px.box(boxplot_data,x='Day',y='Message')
    # Boxplot for messages per day by contact
    fig_boxplot_contact = go.Figure()
    contacts.sort()
    for i in contacts:
        fig_boxplot_contact.add_trace(go.Box(
        y=boxplot_data[boxplot_data['Contact'] == i]['Message'],
        x=boxplot_data['Day'],
        name=i
        
        ))

    fig_boxplot_contact.update_layout(
    yaxis_title='Messages per day',
    boxmode='group' 
    )
    # Finding consecutive data and creating dataframe with streak and dates of top 3
    cons_days_data = pd.DataFrame(df['Date'].unique())
    cons_days_data.rename( columns={0:'Day'}, inplace=True )
    cons_days_data['Amount']=cons_days_data.Day.diff().dt.days.ne(1).cumsum()
    cons_days_data.groupby([cons_days_data.index,'Amount']).size().reset_index(level=1, drop=True)
    cons_days = pd.DataFrame(cons_days_data['Amount'].value_counts())
    top_3 = cons_days.index[:3]
    top_3 = top_3.to_list()
    day_top3_data = cons_days_data[cons_days_data['Amount'].isin(top_3)]
    top_3_streak = day_top3_data.groupby('Amount').agg(['min','max'])
    top_3_streak = top_3_streak.join(cons_days,'Amount','left')
    # Streak counter for graphing streak throughout time
    cons_days_data['start_of_streak'] = cons_days_data.Amount.ne(cons_days_data['Amount'].shift())
    cons_days_data['streak_id'] = cons_days_data['start_of_streak'].cumsum()
    cons_days_data['streak_counter'] = cons_days_data.groupby('streak_id').cumcount() + 1
    fig_streak = px.bar(cons_days_data,x='Day',y='streak_counter',title = 'Consecutive days of conversation')
    # Emoji count by contact
    contact_emoji_df = df[['Contact','Emojis']]
    contact_emoji_df = contact_emoji_df.explode('Emojis')
    contact_emoji_df = contact_emoji_df.dropna(subset=['Emojis'])
    emoji_df = pd.DataFrame(contact_emoji_df.groupby(['Contact','Emojis']).agg(count=('Emojis', 'count'))).reset_index()
    emoji_df.sort_values(by=['count'],ascending=False,inplace=True)
    emoji_top_5 = emoji_df.groupby('Contact').head(5)
    emoji_graph = px.bar(emoji_top_5,x='Emojis',y='count',color = 'Contact',barmode="group",title='Emoji used in message per contact')
    # Response time per person
    response_time_filtered = df[(df['Time_to_respond_mins'] < 300) & (df['Time_to_respond_mins'] >= 1)]
    avg_response_time = response_time_filtered.groupby('Contact').agg(avg_time_mins = ('Time_to_respond_mins','mean'),
                                                                        median = ('Time_to_respond_mins','median'),
                                                                        std = ('Time_to_respond_mins','std')).reset_index()
    avg_time_day = response_time_filtered.groupby(['Contact','Year_month']).agg(avg_resp_time = ('Time_to_respond_mins','mean')).reset_index()
    fig_avg_response_time = px.line(avg_time_day,x='Year_month',y = 'avg_resp_time',color='Contact',title= 'Mean response time per month (minutes)')
    # med_time_day = response_time_filtered.groupby(['Contact','Year_month']).agg(avg_resp_time = ('Time_to_respond_mins','median')).reset_index()
    # fig_med_response_time = px.line(med_time_day,x='Year_month',y = 'avg_resp_time',color='Contact',title= 'Median response time per month (minutes)')
    # Calculating peak hours adjusting timezone diff
    peak_hours = df
    timezone_diff = dt.timedelta(hours=6)
    peak_hours['Hour'] = peak_hours['Datetime'].apply(lambda x: x.hour)
    peak_hours['Hour'] = peak_hours['Datetime'].apply(lambda x: x + timezone_diff if ((dt.datetime.strptime('22/09/10', '%y/%m/%d')).date() <= x.date() <= (dt.datetime.strptime('23/01/17', '%y/%m/%d').date())) else x)
    peak_hours['Hour'] = peak_hours['Hour'].apply(lambda x: x.hour)
    peak_hours_df = peak_hours.groupby(['Hour']).agg(msg_amount = ('Hour','count')).reset_index()
    fig_peak_hour = px.bar(peak_hours_df,x='Hour',y='msg_amount',title='Messages per hour')
    # Words per message and message length
    msg_length_df = df
    msg_length_df['msg_type'] = msg_length_df['Words'].apply(lambda x: 'Long' if x>=20 else ('Short' if x<=5 else 'Mid') )
    msg_length_total = msg_length_df.groupby(['Contact','msg_type']).agg(msg_amount = ('msg_type','count')).reset_index()
    fig_msg_length_cat = px.bar(msg_length_total,x='Contact',y='msg_amount',color= 'msg_type',barmode='group',title= 'Message type')
    # Messages over 20 words over time
    msg_length_month = msg_length_df.groupby(['Year_month','Contact','msg_type']).agg(msg_amount = ('msg_type','count')).reset_index()
    msg_length_month.sort_values(by='Contact',ascending= True)
    # msg_length_overtime = px.line(msg_length_month[msg_length_month['msg_type'] == 'Long'],x='Year_month',y='msg_amount',color='Contact',title='Messages with >= 20 words')
    # Max words per contact
    max_words = df.groupby('Contact').agg(max_words = ('Words','max')).reset_index()
    return [fig_pie,fig_msg_over_time,fig_media,fig_message_month,fig_boxplot,fig_boxplot_contact,
            fig_streak,emoji_graph,fig_avg_response_time,fig_peak_hour,
            fig_msg_length_cat]

def word_clouds(processed_chat):
  words_contact = []
  clouds = []
  for i in contacts:
    text = " ".join(Message for Message in processed_chat[processed_chat['Contact'] == i].Message)
    words_contact.append(text)
  for i in range(len(words_contact)):
    wordcloud = WordCloud(max_font_size=40, max_words=150, background_color="white",stopwords = stop_words_sp).generate(words_contact[i])
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    st.pyplot()
  return clouds


uploaded_file = st.file_uploader("Upload Files",type=['.txt'])

if st.button('Process file'):
    if uploaded_file:
        data = uploaded_file.getvalue().decode('utf-8').splitlines()
        print(data)
        print(type(data))
        file = extract_chat_info(data)
        file['Date'] = pd.to_datetime(file["Date"], format="%d/%m/%y")  
        df,contacts = chat_processing(file)
        charts = create_graphs(df)
        '# Whatsapp Dash'
        for i in charts:
            st.plotly_chart(i)
        word_clouds(df)
else:
    st.write('Upload file')
















