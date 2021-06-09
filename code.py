# pip3 install --user python_graphql_client

from python_graphql_client import GraphqlClient
import csv
import datetime
import pandas as pd
import numpy as np


def pull_data(username):
    # Instantiate the client with an endpoint.
    client = GraphqlClient(endpoint="https://leetcode.com/graphql")

    # Create the query string and variables required for the request.
    query = """
    query getUserProfile($username: String!) {
        allQuestionsCount {
            difficulty
            count
        }
        matchedUser(username: $username) {
            username
            submissionCalendar
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                    submissions
                }
            } 
        }
    }
    """
    variables = {"username": username}

    # Synchronous request
    response = client.execute(query=query, variables=variables)
    return response


def extract_data(user_data):
    total = user_data['data']['matchedUser']['submitStats']['acSubmissionNum'][0]['count']
    easy = user_data['data']['matchedUser']['submitStats']['acSubmissionNum'][1]['count']
    medium = user_data['data']['matchedUser']['submitStats']['acSubmissionNum'][2]['count']
    hard = user_data['data']['matchedUser']['submitStats']['acSubmissionNum'][3]['count']
    return total, easy, medium, hard


def write_data(total, easy, medium, hard, username):
    data = pd.read_csv("database.csv")

    date = datetime.datetime.now()
    str_date = date.strftime("%x")

    data.query(
        f'username == "{username}" and all == {total} and date == "{str_date}"', inplace=True)

    if len(data.index) < 1:
        with open('database.csv', mode='a') as database:
            writer = csv.writer(database, delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerow([username, str_date, total, easy, medium, hard])
            # #Close the file object
            database.close()


def add_new_user(username, user_set):
    with open('user_database.csv', mode='a') as database:
        writer = csv.writer(database, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if username in user_set:
            print("exists")
        else:
            print("added " + username)
            user_set.add(username)

            cleanup_db()
            for usr in user_set:
                writer.writerow([usr])
        # Close the file object
        database.close()


def cleanup_db():
    with open('user_database.csv', mode='w') as database:
        writer = csv.writer(database, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["username"])
        # Close the file object
        database.close()


def delete_user_by_name(username, user_set):
    if username in user_set:
        print("exists")
        print("removed " + username)
        # cleanup_db()
        users = pd.read_csv("user_database.csv")
        users.query(f'username != "{username}"', inplace=True)
        users.to_csv('user_database.csv', index=False)
        # clean database too
        data = pd.read_csv("database.csv")
        data.query(f'username != "{username}"', inplace=True)
        data.to_csv('database.csv', index=False)


def get_all_users():
    with open('user_database.csv', mode='r') as database:
        csv_reader = csv.DictReader(database)
        user_set = set()
        for row in csv_reader:
            user_set.add(row['username'])
        # Close the file object
        database.close()
        return user_set


def update_database():
    # get user list
    user_list = get_all_users()
    for user in user_list:
        user_data = pull_data(user)
        if 'errors' not in user_data:
            total, medium, hard, easy = extract_data(user_data)
            write_data(total, medium, hard, easy, user)
        else:
            return user
    return None


def range_generator():
    now = datetime.datetime.now()
    today_num = now.weekday()

    delta = datetime.timedelta(today_num)
    week_start = now - delta
    week_start = week_start.replace(hour=0, minute=0)

    delta = datetime.timedelta(6-today_num)
    week_end = now + delta
    week_end = week_end.replace(hour=23, minute=59)

    res = {'start': week_start, 'end': week_end}
    return res


def copy_previous_day_data():
    # get user list
    data = pd.read_csv("database.csv")

    # get date range
    date_range = range_generator()
    # get data in range
    data['date'] = pd.to_datetime(data['date'])
    data.query(
        f'date < "{date_range["start"]}"', inplace=True)
    # group by user
    grouped = data.groupby(by=['username']).agg(
        all=('all', 'last'),
        easy=('easy', 'last'),
        medium=('medium', 'last'),
        hard=('hard', 'last')
    )

    if len(grouped) != 0:
        for username, row in grouped.iterrows():
            write_data(row['all'], row['easy'],
                       row['medium'], row['hard'], username)


def get_all_user_progress():
    # just to duplicate progress
    copy_previous_day_data()
    # get user list
    data = pd.read_csv("database.csv")

    # get date range
    date_range = range_generator()
    # get data in range
    data['date'] = pd.to_datetime(data['date'])
    data.query(
        f'date > "{date_range["start"]}" and date < "{date_range["end"]}"', inplace=True)
    # group by user
    grouped = data.groupby(by=['username']).agg(
        start=('all', 'min'), end=('all', 'max'))
    # count difference between last n first
    grouped['progress'] = grouped['end'].sub(grouped['start'])
    # order by progress
    ordered = grouped.sort_values(by='progress', ascending=False)
    # add emojis
    emojis = ['\U0001F947', '\U0001F948', '\U0001F949']

    ordered["#"] = ''
    df = ordered
    c = 0
    for row in df.itertuples():
        if c < 3:
            df.at[row.Index, '#'] = emojis[c]
        else:
            break
        c += 1

    return df.to_markdown(index=True)
