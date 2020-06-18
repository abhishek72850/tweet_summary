var requestAjax=function(options, dataset, call_type){

	var object = {
		url:"https://tweet-summary.herokuapp.com/api/fetch/summary/",
//		url:"http://localhost:8000/api/fetch/summary/",
		data:{},
		type:"GET",
		datatype:'jsonp'
	};

	$.extend(object,options);

	xhr = $.ajax(object).done(function(data){
		console.log(data);

		if(call_type=='Search'){
            $('.result_cont').show()
            $('.result_nav_panel').css({'visibility':'visible'})

            if(data['status'] == 200){

                app_env.data = data['data'];
                data = data['data'];

                $('.query').text(data['query']);
                $('.increase').text(data['increase_in_tweets']);

                $('.total_tweets').text(data['total_tweets']);
                $('.total_mentions').text(data['total_mentions'].length);
                $('.total_retweets').text(data['total_retweets']);
                $('.total_favorite').text(data['total_favorite']);


                var mention_list = new Set();
                for(var value of data['noticeable_user']){
                    mention_list.add(value[0]);
                }

                mention_list = Array.from(mention_list);
                $('.noticeable_user').text(mention_list.slice(0,5).join(", "));

                $('.most_active_verified_tweet_user_name').text(data['most_active_verified_tweet']['user']['name']);
                $('.most_active_verified_tweet_retweets').text(data['most_active_verified_tweet']['retweet_count']);
                $('.most_active_verified_tweet_favorite').text(data['most_active_verified_tweet']['favorite_count']);
                $('.most_active_verified_tweet').html(data['most_active_verified_tweet']['text']);

                mention_list = new Set();

                for(var value of data['most_active_verified_tweet']['entities']['user_mentions']){
                    mention_list.add(value['name']);
                }
                mention_list = Array.from(mention_list);
                $('.most_active_verified_tweet_mentions').text(mention_list.join(", "));

                $('.noticeable_user_tweet_user_name_1').text(data['noticeable_user_tweet'][0]['user_name']);
                $('.noticeable_user_tweet_total_1').text(data['noticeable_user_tweet'][0]['tweet_content'].length);
                $('.noticeable_user_tweet_total_retweets_1').text(data['noticeable_user_tweet'][0]['retweets_count']);
                $('.noticeable_user_tweet_total_favorite_1').text(data['noticeable_user_tweet'][0]['favorite_count']);

                mention_list = new Set();

                for(var value of data['noticeable_user_tweet'][0]['mentions']){
                    mention_list.add(value['name']);
                }
                mention_list = Array.from(mention_list);
                $('.noticeable_user_tweet_mentions_1').text(mention_list.join(", "));

                $('.noticeable_user_tweet_user_name_2').text(data['noticeable_user_tweet'][1]['user_name']);
                $('.noticeable_user_tweet_total_2').text(data['noticeable_user_tweet'][1]['tweet_content'].length);
                $('.noticeable_user_tweet_total_retweets_2').text(data['noticeable_user_tweet'][1]['retweets_count']);
                $('.noticeable_user_tweet_total_favorite_2').text(data['noticeable_user_tweet'][1]['favorite_count']);

                mention_list = new Set();

                for(var value of data['noticeable_user_tweet'][1]['mentions']){
                    mention_list.add(value['name']);
                }
                mention_list = Array.from(mention_list);
                $('.noticeable_user_tweet_mentions_2').text(mention_list.join(", "));


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
                $('.stats_24_noticeable_mentions').text(mention_list.join(", "));

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
                $('.stats_24_most_active_tweet_mentions').text(mention_list.join(", "));
            }
            $('#loader').hide();
            $('.analysis_loader').hide();
        }
        else{
            $('.analysis_cont').hide();
            $('.analysis_loader').hide();
            alert(data['data'])
        }

	}).fail(function( jqXHR, textStatus, errorThrown ) {
		console.log(jqXHR);
		$('.analysis_cont').hide();
        $('.analysis_loader').hide();
		alert('Something went wrong. Please try again');

		$('#loader').hide();
	});
}

var loadContent = function(data){

}
