$(function(){
    $('.result').hide();
    $('.resultHeading').hide();

    $('#quickAnalysisForm').on('submit',function(e){
        e.preventDefault();

        console.log(this.query.value);

        requestAjax(
             {
                url: window.location.origin + "/api/analysis/summary",
                type: "GET",
                data:{
                    'query':this.query.value
                }
            },
            function(data){
                data = data['data'];
                $('.result').show();
                $('.resultHeading').show();

                $('.data_timestamp').text(Date());

                $('.query').text(data['query']);

                if(data['increase_in_tweets'] > 0){
                    inc_or_dec = data['increase_in_tweets'] + ' increase';
                    $('.increase').removeClass('red');
                    $('.increase').addClass('green');
                }
                else{
                    inc_or_dec = (data['increase_in_tweets'] * -1) + ' decrease';
                    $('.increase').removeClass('green');
                    $('.increase').addClass('red');
                }
                $('.increase').text(inc_or_dec);

                $('.total_tweets').text(data['total_tweets']);
                $('.total_mentions').text(data['total_mentions'].length);
                $('.total_retweets').text(data['total_retweets']);
                $('.total_favorite').text(data['total_favorite']);


                var mention_list = new Set();
                for(var value of data['noticeable_user']){
                    mention_list.add(value[0]);
                }

                mention_list = Array.from(mention_list);

                if(mention_list.length > 0){
                    if(mention_list.length < 5){
                        $('.noticeable_user').text(mention_list.join(", "));    
                    }
                    else{
                        var top_5_user = mention_list.slice(0,5).join(", ");
                        var other_user = " and " + (mention_list.length - 5) + "other's."
                        $('.noticeable_user').text(top_5_user + other_user);
                    }
                }
                else{
                    $('.noticeable_user').text('None');
                }


                $('.most_active_verified_tweet_user_name').text(data['most_active_verified_tweet']['user']['name']);
                $('.most_active_verified_tweet_retweets').text(data['most_active_verified_tweet']['retweet_count']);
                $('.most_active_verified_tweet_favorite').text(data['most_active_verified_tweet']['favorite_count']);
                $('.most_active_verified_tweet').html(createTextLinks_(data['most_active_verified_tweet']['text']));

                mention_list = new Set();

                for(var value of data['most_active_verified_tweet']['entities']['user_mentions']){
                    mention_list.add(value['name']);
                }
                mention_list = Array.from(mention_list);

                if(mention_list.length > 0){
                    $('.most_active_verified_tweet_mentions').text(mention_list.join(", "));
                }
                else{
                    $('.most_active_verified_tweet_mentions').text('None');
                }

                if(data['noticeable_user_tweet'].length > 0){
                    if(data['noticeable_user_tweet'][0]['tweet_content'].length == 0){
                        $('.active_user_1').hide()
                    }

                    if(data['noticeable_user_tweet'].length == 1){
                        $('.active_user_2').hide()
                    }
                }
                else{
                    $('.active_users').hide()
                }

                $('.noticeable_user_tweet_user_name_1').text(data['noticeable_user_tweet'][0]['user_name']);
                $('.noticeable_user_tweet_total_1').text(data['noticeable_user_tweet'][0]['tweet_content'].length);
                $('.noticeable_user_tweet_total_retweets_1').text(data['noticeable_user_tweet'][0]['retweets_count']);
                $('.noticeable_user_tweet_total_favorite_1').text(data['noticeable_user_tweet'][0]['favorite_count']);

                mention_list = new Set();

                for(var value of data['noticeable_user_tweet'][0]['mentions']){
                    mention_list.add(value['name']);
                }
                mention_list = Array.from(mention_list);

                if(mention_list.length > 0){
                    $('.noticeable_user_tweet_mentions_1').text(mention_list.join(", "));
                }
                else{
                    $('.noticeable_user_tweet_mentions_1').text('None');
                }

                $('.noticeable_user_tweet_user_name_2').text(data['noticeable_user_tweet'][1]['user_name']);
                $('.noticeable_user_tweet_total_2').text(data['noticeable_user_tweet'][1]['tweet_content'].length);
                $('.noticeable_user_tweet_total_retweets_2').text(data['noticeable_user_tweet'][1]['retweets_count']);
                $('.noticeable_user_tweet_total_favorite_2').text(data['noticeable_user_tweet'][1]['favorite_count']);

                mention_list = new Set();

                for(var value of data['noticeable_user_tweet'][1]['mentions']){
                    mention_list.add(value['name']);
                }
                mention_list = Array.from(mention_list);

                if(mention_list.length > 0){
                    $('.noticeable_user_tweet_mentions_2').text(mention_list.join(", "));
                }
                else{
                    $('.noticeable_user_tweet_mentions_2').text('None');
                }


                //24 hour stats
                var data_24 = data['24_hour_stats'];

                $('.stats_24_total_tweets').text(data_24['total_tweets']);
                $('.stats_24_total_retweets').text(data_24['total_retweets']);
                $('.stats_24_total_favorite').text(data_24['total_favorite']);

                mention_list = new Set();

                for(var value of data_24['verified_mentions']){
                    mention_list.add(value['name']);
                }
                mention_list = Array.from(mention_list);

                if(mention_list.length > 0){
                    $('.stats_24_noticeable_mentions').text(mention_list.join(", "));
                }
                else{
                    $('.stats_24_noticeable_mentions').text('None');
                }

                $('.stats_24_noticeable_retweets').text(data_24['verified_total_retweets']);
                $('.stats_24_noticeable_favorite').text(data_24['verified_total_favorite']);
                $('.stats_24_most_active_tweet_user_name').text(data_24['most_active_tweet']['user']['name']);
                $('.stats_24_most_active_tweet_text').text(data_24['most_active_tweet']['text']);
                $('.stats_24_most_active_tweet_retweets').text(data_24['most_active_tweet']['retweet_count']);
                $('.stats_24_most_active_tweet_favorite').text(data_24['most_active_tweet']['favorite_count']);

                mention_list = new Set();

                for(var value of data_24['most_active_tweet']['entities']['user_mentions']){
                    mention_list.add(value['name']);
                }
                mention_list = Array.from(mention_list);

                if(mention_list.length > 0){
                    $('.stats_24_most_active_tweet_mentions').text(mention_list.join(", "));
                }
                else{
                    $('.stats_24_most_active_tweet_mentions').text('None');
                }
            }
        );
    });
});