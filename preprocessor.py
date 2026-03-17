import re
import pandas as pd

def preprocess(data):
    # 1. Highly flexible pattern that catches both 12-hr and 24-hr formats automatically
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s*[\u202f\s]*[a-zA-Z]{0,2}\s*-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # 2. Rigorous cleaning function to strip weird spaces and standardize to UPPERCASE
    def clean_date(text):
        text = str(text).replace(' - ', '')
        text = text.replace('\u202f', ' ')
        return text.strip().upper()

    df['message_date'] = df['message_date'].apply(clean_date)

    # 3. THE FIX: Drop the strict format string entirely. Let Pandas infer it!
    df['date'] = pd.to_datetime(df['message_date'], errors='coerce', dayfirst=True)

    # 4. Drop rows where date parsing failed and clean up columns
    df = df.dropna(subset=['date'])

    # 5. Extract users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # User name is present
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message', 'message_date'], inplace=True, errors='ignore')

    # 6. Extract timeline features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    return df
