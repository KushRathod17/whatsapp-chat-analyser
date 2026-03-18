import re
import pandas as pd

def preprocess(data):
    # 1. THE UNIVERSAL REGEX
    # Matches DD/MM/YY or DD/MM/YYYY
    # Matches HH:MM or H:MM
    # Optional AM/PM/am/pm with optional hidden spaces
    # Ends with ' - '
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:[\s\u202f]*[a-zA-Z]{1,2})?\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # If the file format is completely unrecognized, return empty df safely
    if not dates:
        return pd.DataFrame()

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # 2. Clean the dates
    df['message_date'] = df['message_date'].str.replace(r'\s-\s$', '', regex=True) # Remove trailing dash
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ') # Fix WhatsApp hidden space
    df['message_date'] = df['message_date'].str.strip()

    # 3. Smart Datetime Conversion (Handles 12h and 24h automatically)
    df['date'] = pd.to_datetime(df['message_date'], errors='coerce', dayfirst=True)

    # Drop any corrupted rows
    df = df.dropna(subset=['date'])

    # 4. Extract users and messages
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
    df.drop(columns=['user_message', 'message_date'], inplace=True)

    # 5. Extract Timeline Features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    
    # 24-hour format integer (0-23) - Perfect for the heatmap!
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # 6. Create the 'Period' column needed for Heatmaps
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
            
    df['period'] = period

    return df
