from helpers.twitter import TwitterHelper
from helpers.watson import Watson


watson = Watson()


def prepare_twitter_analysis(topic):
    tweet = TwitterHelper(topic)
    data = tweet.fetch_analysis()

    positive_tweet = 0
    neutral_tweet = 0
    negative_tweet = 0

    todays_tweets = tweet.stats_for_24_hour()['tweet_list']

    for tweet_obj in todays_tweets:
        keywords = watson.extractKeywords(tweet_obj['text'])
        if keywords['success']:
            sentiment = watson.extractSentiment(tweet_obj['text'], keywords['data'])
            if sentiment['success']:
                sentiment = sentiment['data']
                if sentiment['sentiment']['document']['label'] == 'positive':
                    positive_tweet += 1
                elif sentiment['sentiment']['document']['label'] == 'negative':
                    negative_tweet += 1
                elif sentiment['sentiment']['document']['label'] == 'neutral':
                    neutral_tweet += 1
        #     else:
        #         print(tweet_obj['text'], keywords)
        # else:
        #     print(tweet_obj['text'])

    if data['success']:
        print('Preparing....')
        data = data['data']
        analysis_data = {
            'query': data['query'],
            'increase': data['increase_in_tweets'],
            'total_tweets': data['total_tweets'],
            'total_mentions': len(data['total_mentions']),
            'total_retweets': data['total_retweets'],
            'total_favorite': data['total_favorite'],
            'total_todays_tweet': len(todays_tweets),
            'total_positive_tweets': positive_tweet,
            'total_negative_tweets': negative_tweet,
            'total_neutral_tweets': neutral_tweet
        }

        if data['increase_in_tweets'] < 0:
            analysis_data['increase_or_decrease'] = '{} decrease'.format(str(data['increase_in_tweets']*(-1)))
        else:
            analysis_data['increase_or_decrease'] = '{} increase'.format(str(data['increase_in_tweets']))

        mention_list = set()
        for value in data['noticeable_user']:
            mention_list.add(value[0])

        mention_list = list(mention_list)
        analysis_data['noticeable_user'] = ', '.join(mention_list[0:5])

        if len(mention_list) > 0:
            if len(mention_list) < 5:
                analysis_data['noticeable_user'] = ', '.join(mention_list[0:5])
            else:
                top_5_user = ', '.join(mention_list[0:5])
                other_user = " and {} other's.".format((len(mention_list) - 5))
                analysis_data['noticeable_user'] = '{}{}'.format(top_5_user, other_user)
        else:
            analysis_data['noticeable_user'] = 'None'

        analysis_data['most_active_verified_tweet_user_name'] = data['most_active_verified_tweet']['user'].get('name', '')
        analysis_data['most_active_verified_tweet_retweets'] = data['most_active_verified_tweet'].get('retweet_count', 0)
        analysis_data['most_active_verified_tweet_favorite'] = data['most_active_verified_tweet'].get('favorite_count', 0)
        analysis_data['most_active_verified_tweet'] = data['most_active_verified_tweet'].get('text', '')

        mention_list = set()

        for value in data['most_active_verified_tweet'].get('entities', {}).get('user_mentions', {}):
            mention_list.add(value['name'])

        mention_list = list(mention_list)

        if len(mention_list) > 0:
            analysis_data['most_active_verified_tweet_mentions'] = ', '.join(mention_list)
        else:
            analysis_data['most_active_verified_tweet_mentions'] = 'None'

        if len(data['noticeable_user_tweet']) > 0:
            analysis_data['noticeable_user_tweet_user_name_1'] = data['noticeable_user_tweet'][0]['user_name']
            analysis_data['noticeable_user_tweet_total_1'] = len(data['noticeable_user_tweet'][0]['tweet_content'])
            analysis_data['noticeable_user_tweet_total_retweets_1'] = data['noticeable_user_tweet'][0]['retweets_count']
            analysis_data['noticeable_user_tweet_total_favorite_1'] = data['noticeable_user_tweet'][0]['favorite_count']

            mention_list = set()

            for value in data['noticeable_user_tweet'][0]['mentions']:
                mention_list.add(value['name'])

            mention_list = list(mention_list)

            if len(mention_list) > 0:
                analysis_data['noticeable_user_tweet_mentions_1'] = ', '.join(mention_list)
            else:
                analysis_data['noticeable_user_tweet_mentions_1'] = 'None'

            analysis_data['noticeable_user_tweet_user_name_2'] = data['noticeable_user_tweet'][1]['user_name']
            analysis_data['noticeable_user_tweet_total_2'] = len(data['noticeable_user_tweet'][1]['tweet_content'])
            analysis_data['noticeable_user_tweet_total_retweets_2'] = data['noticeable_user_tweet'][1]['retweets_count']
            analysis_data['noticeable_user_tweet_total_favorite_2'] = data['noticeable_user_tweet'][1]['favorite_count']

            mention_list = set()

            for value in data['noticeable_user_tweet'][1]['mentions']:
                mention_list.add(value['name'])

            mention_list = list(mention_list)

            if len(mention_list) > 0:
                analysis_data['noticeable_user_tweet_mentions_2'] = ', '.join(mention_list)
            else:
                analysis_data['noticeable_user_tweet_mentions_2'] = 'None'

        return analysis_data
    else:
        return {'query': 'Something went wrong'}