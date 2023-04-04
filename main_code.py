import time
import tweepy as tw
import pandas as pd
import re
from datetime import datetime


# Initiate client with custom Twitter developer app keys
def get_client():
    api = tw.Client(bearer_token=bt,
                    consumer_key=ck,
                    consumer_secret=cks,
                    access_token=at,
                    access_token_secret=ats)
    return api


# Return boolean value to determine if string includes non-English characters
def is_english(s):
    return s.isascii()


# Access Twitter API client with specific query - if initial search, stage = 1, else stage = 2
def get_data(query, theme):
    global exit_loop, collected_tweets, next_token, initial_search
    client = get_client()  # initialise each time to prevent API timeout
    if not client:
        print('----- Connection Unsuccessful -------')
        return None
    else:
        try:
            if initial_search is True:
                paginator = tw.Paginator(client.search_recent_tweets, query=query, max_results=100)
            else:
                paginator = tw.Paginator(client.search_recent_tweets, query=query, max_results=100,
                                         next_token=next_token)


            j = 1
            # Paginator through recent search results with query input maximum count parameters (basic access)
            for tweet in paginator:
                if len(collected_tweets) > 2000:
                    return collected_tweets
                else:
                    meta = tweet.meta  # dict
                    data = tweet.data  # class
                    next_token = meta.get("next_token")
                    text = str(data[1])
                    tweet_id = str(data[0])
                    j += 1
                    word_list = text.split()
                    number_of_words = len(word_list)
                    # remove non-English tweets and de-duplicate collected tweets
                    if not is_english(text) or text in collected_ids or number_of_words < 4:
                        # non_eng_count += 1
                        continue
                    else:
                        # append tweet text to list of collected tweets
                        collected_tweets.append(str(text))
                        collected_ids.append(str(tweet_id))
                    if j % 50 == 0:
                        print(f"Page {j}: {len(collected_tweets)} tweets collected")
            # print(f"Number of non-English tweets discarded = {non_eng_count}")
            list_to_csv(len(collected_tweets), collected_tweets, "tweets", theme)
            return collected_tweets
        # catch API exception (e.g. tweet retrieval rate have been reached)
        except tw.TweepyException as e:
            print('Tweepy responded with error: ' + str(e))
            # end search
            exit_loop = True
            list_to_csv(len(collected_tweets), collected_tweets, "tweets", theme)
            return collected_tweets


def create_df(list_in):
    dataframe = pd.DataFrame(list_in, columns=['Tweet'])
    print(f'Number of rows in INITIAL dataframe: {dataframe.shape[0]}')
    df_prepared = prepare_data(dataframe)
    print(f'Number of rows in PREPARED dataframe: {df_prepared.shape[0]}')
    return df_prepared


def prepare_data(dataframe):

    # convert to lowercase characters
    dataframe['tweet'] = dataframe['tweet'].str.lower()

    # remove any @ names for anonymisation and for token matching
    dataframe.replace(regex=[pattern1], value=' USER ', inplace=True)
    dataframe.replace(regex=[pattern2], value=' calories ', inplace=True)
    dataframe.replace(regex=[pattern3], value=' so much ', inplace=True)
    dataframe.replace(regex=[pattern4], value=' because ', inplace=True)
    dataframe.replace(regex=[pattern5], value=' just ', inplace=True)
    dataframe.replace(regex=[pattern6], value=' i don\'t know ', inplace=True)
    dataframe.replace(regex=[pattern7], value=' really ', inplace=True)
    dataframe.replace(regex=[pattern8], value=' do not ', inplace=True)
    dataframe.replace(regex=[pattern9], value=' want to ', inplace=True)
    dataframe.replace(regex=[pattern10], value=' just saying ', inplace=True)
    dataframe.replace(regex=[pattern11], value=' saying ', inplace=True)
    dataframe.replace(regex=[pattern12], value=' can\'t ', inplace=True)
    dataframe.replace(regex=[pattern13], value=' won\'t ', inplace=True)

    # remove URLs
    dataframe.replace(regex=[pattern17], value=' ', inplace=True)
    # remove digits
    dataframe.replace(regex=[pattern14], value=' ', inplace=True)
    # remove punctuation
    dataframe.replace(regex=[pattern15], value=' ', inplace=True)
    # address negation
    dataframe.replace(regex=[pattern16], value='NOT_', inplace=True)

    # remove any outstanding duplicate rows
    dataframe.drop_duplicates(inplace=True)
    # remove rows with missing data
    dataframe.dropna(inplace=True)

    print(dataframe.head())
    return dataframe


def df_to_csv(file_name, dataframe):
    dataframe.to_csv(file_name, index=False, encoding='utf-8')
    print(f"{file_name} created with {len(dataframe)} tweets")


def list_to_csv(file_number, list_in, file_type, theme):
    dataframe = pd.DataFrame(list_in, columns=[file_type.capitalize()])
    file_name = f"THEME {theme} {file_type.upper()} Data CSV File {file_number}.csv"
    df_to_csv(file_name, dataframe)


def get_tweets(query, theme):
    global exit_loop, collected_tweets, collected_ids, initial_search
    # collected_tweets = []  # re-initialise empty list
    # collected_ids = []
    i = 1
    try:
        while len(collected_tweets) < 4000:
            if exit_loop is False:
                if not collected_tweets:
                    initial_search = True
                else:
                    initial_search = False
                    # initial search for tweets (no next_token)
                print("Searching for tweets.... Iteration #" + str(i))
                data = get_data(query, theme)  # search recent tweets with keyword input as a query, return as a data
                # variable
                list_to_csv(i, data,
                            "tweet", theme)  # save current list of tweets as CSV file as a back-up to prevent data loss
                i += 1

            else:
                for t in (range(30, 1, -5)):
                    localtime = time.localtime()
                    result = time.strftime("%I:%M:%S %p", localtime)
                    print(result)
                    print(f"{t} minutes until next search...\r", flush=True)
                    time.sleep(60 * 5)

                # if length of collected tweets list > 5000, break out of loop. Else, keep searching for tweets
                initial_search = False
                print("\nSearching for tweets.... Iteration #" + str(i))
                data = get_data(query, theme)

                # save backup every 1000 tweets
                list_to_csv(i, data,
                            "tweet", theme)  # save current list of tweets as CSV file as a back-up to prevent data loss
                i += 1

        # break out of loop if interrupted
    except KeyboardInterrupt:
        pass


def date_to_string():
    now = datetime.now()  # current date and time
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    return date_time


def search_to_csv(query, theme):
    global exit_loop, collected_tweets, initial_search
    # make sure exit_loop is set to False, to initiate first search
    exit_loop = False
    initial_search = True

    print(f"\n---------- {theme} TWEET DATA COLLECTION ----------")

    # the following call will run the get_tweets() function until number of tweets > 5000
    get_tweets(query, theme)

    # if no tweets have been collected
    if not collected_tweets:
        exit("No tweets collected. Terminating program.")
    else:
        print("Tweet data collection complete.")

    print(f"\n---------- {theme} TWEET PREPARATION ----------")
    tweet_df = pd.DataFrame(collected_tweets, columns=["tweet"])
    clean_df = prepare_data(tweet_df)
    df_to_csv(f"{theme} Clean Tweet Data.csv", clean_df)


def run(query, theme):
    print("PROGRAM RUNNING...")
    search_to_csv(query, theme)


# PERSONAL TWITTER API ACCESS KEYS  -INPUT REQUIRED
bt = ""
ck = ""
cks = ""
at = ""
ats = ""
keywords_bod = "#thighgap OR thigh gap OR #bikinibridge OR bikini bridge OR #skinnyleg OR skinny legs OR #skinny OR skinny OR #weightloss OR weight loss OR #chestbones OR chest bones OR #collarbones OR collarbones OR #fasting OR fasting OR #fat OR bodycheck OR #bodycheck OR #weight OR weight OR #ricecake"

pd.set_option('display.max_columns', 20)
pattern1 = re.compile(r"([@])\w+")
pattern2 = re.compile(r"(cal)+(s?)+\s")
pattern3 = re.compile(r"(sm)+\s")
pattern4 = re.compile(r"\s+(bc*)+\s")
pattern5 = re.compile(r"\s+(js+t+)+\s")
pattern6 = re.compile(r"\s+(idk+)+\s")
pattern7 = re.compile(r"\s+(rl+y+)+\s")
pattern8 = re.compile(r"\s+(don't|dont)+\s")
pattern9 = re.compile(r"\s+(wanna|wana)+\s")
pattern10 = re.compile(r"\s+(js)+\s")
pattern11 = re.compile(r"\s+(sayin+)+\s")
pattern12 = re.compile(r"\s+(cant+)+\s")
pattern13 = re.compile(r"\s+(wont+)+\s")
pattern14 = re.compile(r"([0-9])")
pattern15 = re.compile(r"[^-'a-zA-ZÀ-ÖØ-öø-ÿ\d\s]")
pattern16 = re.compile(r"(not)+\s")
pattern17 = re.compile(r"(http://|https://)+[a-zA-ZÀ-ÖØ-öø-ÿ]*")

classification_list = []
collected_tweets = []
collected_ids = []
list_of_author_ids = []
users_collected = []
exit_loop = False
filename = ""
timeline = []
next_token = ""
initial_search = True

if __name__ == "__main__":
    run(keywords_bod, "BOD")

