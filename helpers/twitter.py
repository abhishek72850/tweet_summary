import requests
from datetime import datetime, timedelta, timezone
import pandas as pd


class TwitterHelper:

    def __init__(self, query):
        self.header = {}
        self.params = {}
        self.query = query
        self.result = []

        self.define_header()
        self.define_params()

    def define_header(self):
        self.header = {
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAHjECwEAAAAAwqEc7QSMg0JP9isaXEcbfUIVaaE' +
                             '%3DEqkWaDiyu9fwdM3IJHjbBLQNkCv5kmuc7EKs4ZgsNpIuPa7fsd'
        }

    def define_params(self):
        self.params = {
            'q': self.query,
            'include_entities': 1,
            'result_type': 'mixed',
            'until': datetime.today().strftime("%Y-%m-%d"),
            'count': 100
        }

    def fetch_result(self, max_range=7):
        for i in range(0, max_range):
            new_date = datetime.today() - timedelta(days=i)
            self.params['until'] = new_date.strftime("%Y-%m-%d")
            if 'max_id' in self.params.keys():
                del self.params['max_id']
            session = requests.session()
            for j in range(0, 10):
                response = session.get(url="https://api.twitter.com/1.1/search/tweets.json", params=self.params,
                                       headers=self.header)
                data = response.json()
                if response.status_code == 200 and 'statuses' in data.keys():
                    self.result.extend(data['statuses'][:])
                    if 'next_results' in data['search_metadata'].keys():
                        self.params['max_id'] = data['search_metadata']['next_results'].split('&')[0][8:]
                    else:
                        break
                else:
                    break

    def increase_in_tweets(self):
        date_count = {}
        for tweet in self.result:
            date_obj = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y")
            date_str = date_obj.date().strftime("%Y-%m-%d")

            if date_str not in date_count.keys():
                date_count[date_str] = 1
            else:
                date_count[date_str] += 1

        date_sort = dict(sorted(date_count.items(), key=lambda k: k[0], reverse=True))
        count_lst = list(date_sort.values())
        total_tweets_before_current = sum(count_lst[:-1])

        # if total_tweets_before_current == 0:
        #     return count_lst[-1] * 100
        if len(count_lst) > 1:
            return count_lst[-2] - count_lst[-1]
        else:
            return count_lst[-1]

        # increase = (count_lst[-1] / sum(count_lst[:-1])) * 100

        # return increase

    def stats_for_24_hour(self):
        now_datetime = datetime.now(timezone.utc)

        todays_tweets = []
        result_24_hour = []
        mentions_24_hour = []
        retweets_24_hour = 0
        favorite_24_hour = 0
        verified_user_tweets_24_hour = []
        verified_user_tweets_mentions_24_hour = []
        verified_user_tweets_retweets_24_hour = 0
        verified_user_tweets_favorite_24_hour = 0

        tweet_obj = {}

        for tweet in self.result:
            if tweet['user']['verified']:
                tweet_obj = tweet
                break

        for tweet in self.result:
            date_obj = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y")
            if (now_datetime - date_obj).days == 0:
                todays_tweets.append(tweet)
                result_24_hour.append(tweet)
                mentions_24_hour.extend(tweet['entities']['user_mentions'])
                retweets_24_hour += tweet['retweet_count']
                favorite_24_hour += tweet['favorite_count']

                if tweet['user']['verified']:
                    verified_user_tweets_24_hour.append(tweet)
                    verified_user_tweets_mentions_24_hour.extend(tweet['entities']['user_mentions'])
                    verified_user_tweets_retweets_24_hour += tweet['retweet_count']
                    verified_user_tweets_favorite_24_hour += tweet['favorite_count']

                    if tweet['retweet_count'] > tweet_obj['retweet_count']:
                        tweet_obj = tweet

        response = {
            'tweet_list': todays_tweets,
            'total_tweets':len(result_24_hour),
            'mentions': mentions_24_hour,
            'total_retweets': retweets_24_hour,
            'total_favorite': favorite_24_hour,
            'verified_total_tweets': len(verified_user_tweets_24_hour),
            'verified_mentions': verified_user_tweets_mentions_24_hour,
            'verified_total_retweets': verified_user_tweets_retweets_24_hour,
            'verified_total_favorite': verified_user_tweets_favorite_24_hour,
            'most_active_tweet': tweet_obj
        }

        return response

    def retweets_favorite_count(self):
        date_stats = {}
        retweet_count = 0
        favorite_count = 0
        for tweet in self.result:
            date_obj = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y")
            date_str = date_obj.date().strftime("%Y-%m-%d")

            if date_str not in date_stats.keys():
                date_stats[date_str] = {
                    "retweet_count": 0,
                    "favorite_count": 0
                }

            date_stats[date_str]["retweet_count"] += tweet["retweet_count"]
            date_stats[date_str]["favorite_count"] += tweet["favorite_count"]

        if len(date_stats) > 0:
            df = pd.DataFrame(date_stats)
            retweet_count = df.loc['retweet_count'].sum()
            favorite_count = df.loc['favorite_count'].sum()

        return retweet_count, favorite_count

    def total_user_mentioned(self, verified=True):
        user_mentions = []
        for tweet in self.result:
            if verified:
                if tweet['user']['verified']:
                    user_mentions.extend(tweet['entities']['user_mentions'])
            else:
                user_mentions.extend(tweet['entities']['user_mentions'])
        return user_mentions

    def mentioned_user_tweets(self, verified=True):
        user_mentions = self.total_user_mentioned(verified)
        mentioned_tweets = []
        for tweet in self.result:
            if tweet['user']['id'] in [x['id'] for x in user_mentions]:
                mentioned_tweets.append(tweet)

        return mentioned_tweets

    def most_retweeted_verified_tweet(self):
        tweet_obj = {}

        for tweet in self.result:
            if tweet['user']['verified']:
                if len(tweet_obj) == 0:
                    tweet_obj = tweet
                elif tweet['retweet_count'] > tweet_obj['retweet_count']:
                    tweet_obj = tweet

        if len(tweet_obj) == 0:
            tweet_obj = {
                'user': {
                    'id': 0
                }
            }
        # for tweet in self.result:
        #     if tweet['user']['verified']:
        #         tweet_obj = tweet
        #         break
        #
        # for tweet in self.result:
        #     if tweet['retweet_count'] > tweet_obj['retweet_count'] and tweet['user']['verified']:
        #         tweet_obj = tweet

        return tweet_obj

    def verified_account_tweets(self):
        verified_account = []
        for tweet in self.result:
            if tweet['user']['verified'] and tweet['user']['id'] != self.most_retweeted_verified_tweet()['user']['id']:
                verified_account.append((tweet['user']['id'], tweet['user']['name']))

        return verified_account

    def most_tweeted_verified_account(self):
        verified_account = self.verified_account_tweets()
        verified_count = {}

        for account in verified_account:
            if account[1] not in verified_count.keys():
                verified_count[account[1]] = 1
            else:
                verified_count[account[1]] += 1

        verified_sort = sorted(verified_count.items(), key=lambda k: k[1], reverse=True)

        return verified_sort

    def most_tweets_by_verified_user(self):
        verified_user = self.most_tweeted_verified_account()[0:2]
        response = []

        for user in verified_user:
            retweets_count = 0
            favorite_count = 0
            mentions = []
            tweet_text = []

            for tweet in self.result:
                if tweet['user']['name'] == user[0]:
                    retweets_count += tweet['retweet_count']
                    favorite_count += tweet['favorite_count']
                    mentions.extend(tweet['entities']['user_mentions'])
                    tweet_text.append(tweet['text'])

            response.append({
                "user_name": user[0],
                "tweet_content": tweet_text,
                "mentions": mentions,
                "favorite_count": favorite_count,
                "retweets_count": retweets_count
            })
        return response

    def fetch_analysis(self):
        self.fetch_result(max_range=1)
        total_retweets, total_favorite = self.retweets_favorite_count()

        if len(self.result) > 0:
            response = {
                "success": True,
                "data": {
                    "query": self.query,
                    "total_tweets": len(self.result),
                    "total_retweets": total_retweets,
                    "total_favorite": total_favorite,
                    "total_mentions": self.total_user_mentioned(verified=False),
                    "increase_in_tweets": self.increase_in_tweets(),
                    "total_verified_mentions": self.total_user_mentioned(verified=True),
                    "most_active_verified_tweet": self.most_retweeted_verified_tweet(),
                    "noticeable_user": self.most_tweeted_verified_account(),
                    "noticeable_user_tweet": self.most_tweets_by_verified_user(),
                    "24_hour_stats": self.stats_for_24_hour()
                }
            }
        else:
            response = {
                "success": False,
                "status": 404,
                "message": "No tweets found!!"
            }

        return response
