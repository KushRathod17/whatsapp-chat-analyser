import pandas as pd
import re


def preprocess(data):
    # Regex to capture the date pattern
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    messages_raw = re.split(pattern, data)[1:]
    dates_raw = re.findall(pattern, data)

    # Sync lengths to prevent ValueError
    min_length = min(len(messages_raw), len(dates_raw))
    df = pd.DataFrame({
        'user_message': messages_raw[:min_length],
        'message_date': dates_raw[:min_length]
    })

    # Convert to datetime and rename
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    message_content = []

    for message in df['user_message']:
        # Split username from message
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            message_content.append(entry[2])
        else:
            users.append('group_notifications')
            message_content.append(entry[0])

    df['user'] = users
    df['message'] = message_content
    df.drop(columns=['user_message'], inplace=True)

    # Extract time features correctly
    df['year'] = df['date'].dt.year
    df['month_num']=df['date'].dt.month
    df['month'] = df['date'].dt.month_name()  # Fixed typo: removed 's'
    df['day'] = df['date'].dt.day
    df['day_name']=df['date'].dt.day_name()
    df['only_date'] = df['date'].dt.date
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period
    return df

    return df