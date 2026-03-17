import re
import pandas as pd

def preprocess(data):
    # Regex pattern to match: DD/MM/YY, HH:MM am/pm - 
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s*[\u202f\s]*[a-zA-Z]{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create the initial dataframe
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Clean the date string: remove the trailing dash and hidden WhatsApp spaces
    df['message_date'] = df['message_date'].str.replace(' - ', '')
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ')
    df['message_date'] = df['message_date'].str.strip()

    # Convert to datetime using the 12-hour format (%I:%M %p) and 2-digit year (%y)
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p', errors='coerce')

    # Drop any rows where the date couldn't be parsed (corrupted lines)
    df = df.dropna(subset=['message_date'])

    # Separate users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # User name is present
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract additional time features for the Streamlit dashboard
    df['only_date'] = df['message_date'].dt.date
    df['year'] = df['message_date'].dt.year
    df['month_num'] = df['message_date'].dt.month
    df['month'] = df['message_date'].dt.month_name()
    df['day'] = df['message_date'].dt.day
    df['day_name'] = df['message_date'].dt.day_name()
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute

    return df
