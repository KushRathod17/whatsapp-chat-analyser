import re
import pandas as pd

def preprocess(data):
    # 1. Match the exact 12-hour pattern from your file
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s*[\u202f\s]*[a-zA-Z]{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # 2. Clean the dates (remove the dash and hidden spaces)
    df['message_date'] = df['message_date'].str.replace(' - ', '', regex=False)
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ', regex=False)
    df['message_date'] = df['message_date'].str.strip()

    # 3. CRITICAL: Convert 'am/pm' to uppercase 'AM/PM' so Pandas doesn't crash
    df['message_date'] = df['message_date'].str.upper()

    # 4. Explicitly parse using the exact format for your chat
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p', errors='coerce')

    # 5. Rename to 'date' for helper.py and drop invalid rows
    df.rename(columns={'message_date': 'date'}, inplace=True)
    df = df.dropna(subset=['date'])

    # 6. Extract users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # user name is present
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # 7. Extract timeline features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    return df
