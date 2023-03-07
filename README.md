# WhatsApp Chat Analyzer

This is a WhatsApp chat analyzer that uses Python to create a Streamlit app. With this app, you can upload your WhatsApp chat file, and the app will generate several charts and visualizations based on the chat data.

You can test the app here:
[Streamlit app](https://sloperab-whatsappdash-app-vxqtri.streamlit.app/)

## How to Use

1.  Clone this repository to your local machine.
    
2.  Install the required packages using the following command: `pip install -r requirements.txt`.
    
3.  Run the Streamlit app with the following command: `streamlit run app.py`.
    
4.  Upload your WhatsApp chat file in .txt format.
    
5.  The app will process the data and generate several charts and visualizations, including:
    
    -   Total number of messages and media files per contact
    -   Chat activity over time
    -   Messages per month
    -   Boxplot of messages per day of week
    -   Consecutive days of message (streak)
    -   Emoji distribution
    -   Mean response tiem per month
    -   Messages per hour
    -   Message type (long,short,mid)
6.  Explore the charts and visualizations to gain insights into your WhatsApp chat.
    
## How to download chat
<img src="https://github.com/sloperab/WhatsappDash/blob/main/images/1.png" width="200" height="400" class="center" />
<img src="https://github.com/sloperab/WhatsappDash/blob/main/images/2.png" width="200" height="400" class="center"/>
<img src="https://github.com/sloperab/WhatsappDash/blob/main/images/3.png" width="200" height="400" class="center"/>

## Requirements

To use this app, you will need to install the following packages:

-   dash
-   emoji
-   matplotlib
-   numpy
-   pandas
-   plotly
-   seaborn
-   streamlit

You can install these packages using the following command: `pip install dash emoji matplotlib numpy pandas plotly seaborn streamlib`.

## Limitations

This app has the following limitations:

-   It only works with WhatsApp chats in .txt format.
-   Currently only works with phones using 12 hour format, not 24. (Working on fix)
-   It may not work properly with non-English chats, especially those with non-Latin characters.

## Credits

This app was created by [Simon Lopera](https://github.com/sloperab). 
