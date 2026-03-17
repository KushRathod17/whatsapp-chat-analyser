import re
import pandas as pd

def preprocess(data):
    # 1. Regex specifically for your file's 12-hour format: "18/06/23, 9:40 pm - "
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s*[\u202f\s]*[a-zA-Z]{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # 2. Clean the hidden WhatsApp space and trailing dash
    df['message_date'] = df['message_date'].str.replace(' - ', '')
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ')
    df['message_date'] = df['message_date'].str.strip()

    # 3. Flexible datetime conversion! Let pandas handle the AM/PM automatically
    df['message_date'] = pd.to_datetime(df['message_date'], dayfirst=True, errors='coerce')

    # 4. CRITICAL: Rename column to 'date' so your helper.py doesn't crash!
    df.rename(columns={'message_date': 'date'}, inplace=True)
    
    # Drop rows where date parsing failed
    df = df.dropna(subset=['date'])

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name is present
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # 5. Extract all your timeline features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    return df
