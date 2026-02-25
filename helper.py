from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user, df):
    # 1. Filter the dataframe FIRST
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    # 2. NOW count the messages
    num_messages = df.shape[0]

    # 3. NOW count the words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # 4. Count Media
    num_media_messages = df[df['message'].str.contains('<Media omitted>')].shape[0]

    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    # 5. Return ALL FOUR values back to app.py
    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()

    # Calculate the percentages
    new_df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()

    # Fix the column names
    new_df.columns = ['Name', 'Percent']

    # JUST RETURN THE DATA. No zombie code here!
    return x, new_df

def create_wordcloud(selected_user, df):
    # REMEMBER: If you used the absolute path earlier, update this line!
    f = open('Whatsapp_chats/stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    # 1. NUKE SYSTEM MESSAGES
    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]

    # 2. THE NUKE: Kills ANY message that contains the word "edited", regardless of case!
    temp = temp[~temp['message'].str.contains('edited', case=False, na=False)]

    def remove_stop_words(message):
        y = []
        # The ultimate banned list
        banned = ['media', 'omitted', 'message', 'deleted', 'edited', 'this', 'was']
        for word in message.lower().split():
            clean_word = word.strip(".,!?-@*\"'~:;<>")
            if clean_word not in stop_words and clean_word not in banned:
                if not clean_word.isnumeric() and len(clean_word) > 1:
                    y.append(clean_word)
        return " ".join(y)

    temp['message'] = temp['message'].apply(remove_stop_words)
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white', collocations=False)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))

    return df_wc

def most_common_words(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    # 1. NUKE SYSTEM MESSAGES
    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]

    # 2. THE NUKE (Repeated here so your table stays clean too)
    temp = temp[~temp['message'].str.contains('edited', case=False, na=False)]

    # REMEMBER: If you used the absolute path earlier, update this line!
    f = open('Whatsapp_chats/stop_hinglish.txt', 'r')
    stop_words = f.read()

    words = []
    banned = ['media', 'omitted', 'message', 'deleted', 'edited', 'this', 'was']

    for message in temp['message']:
        for word in message.lower().split():
            clean_word = word.strip(".,!?-@*\"'~:;<>")
            if clean_word not in stop_words and clean_word not in banned:
                if not clean_word.isnumeric() and len(clean_word) > 1:
                    words.append(clean_word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['Word', 'Count'])
    return most_common_df


import emoji
import pandas as pd
from collections import Counter


def emoji_helper(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]


    emojis = []

    for message in df['message']:
        for char in message:

            if emoji.is_emoji(char):
                emojis.append(char)


    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))), columns=['Emoji', 'Count'])

    return emoji_df

 #timeline
def monthly_timeline(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    # Sort by year and month_num to ensure a smooth line
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline = timeline.sort_values(['year', 'month_num'])

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline
def daily_timeline(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby(['only_date']).count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    # This line MUST be indented with 4 spaces to stay inside the function
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    # This creates the matrix needed for the heatmap
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap





