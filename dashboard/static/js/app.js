$(function(){
	$('#loader').hide();
	$('.analysis_loader').hide();
	$('.result_cont').hide()
	$('.result_nav_panel').css({'visibility':'hidden'})

	$('.nav_toggle').on('click',function(){
		$('.slider_nav').toggleClass('slider_nav_show');
	});

	// create a scene
	new ScrollMagic.Scene({
	    //duration: 100, // the scene should last for a scroll distance of 100px
	    offset: 100 // start this scene after scrolling for 50px
	}).setPin('#search_panel_pin',{pushFollowers: false}).addTo(controller);

	new ScrollMagic.Scene({
	    //duration: 100, // the scene should last for a scroll distance of 100px
	    offset: 0 // start this scene after scrolling for 50px
	}).setPin('#nav',{pushFollowers: false}).addTo(controller);


	$('#search_form').on('submit',function(e){
		e.preventDefault();
		$('#loader').show();
		$('.result_cont').hide()
		$('.result_nav_panel').css({'visibility':'hidden'})

		console.log(this.search.value);

		app_env.query = this.search.value;
		requestAjax({
					data:{
					    'email':this.user_email.value,
					    'password': this.user_password.value,
						'query':this.search.value,
					}
				},this.dataset, 'Search'
		);
	});

	$('#subscriber_form').on('submit',function(e){
	    e.preventDefault();

	    $('.analysis_cont').show();
	    $('.analysis_loader').show();

	    console.log(this.subscriber_email.value);
	    console.log(this.subscriber_topic.value);
	    console.log(this.subscription_start_date.value);
	    console.log(this.subscription_end_date.value);

	    requestAjax({
//	            url: 'http://localhost:8000/subscriber/add',
	            url:"https://tweet-summary.herokuapp.com/subscriber/add",
	            type: 'POST',
                data:{
                    'subscriber_email':this.subscriber_email.value,
                    'subscriber_topic':this.subscriber_topic.value,
                    'subscription_start_date':this.subscription_start_date.value,
                    'subscription_end_date':this.subscription_end_date.value
                }
            },this.dataset, 'Subscribe'
        );
	});

	$('#register_form').on('submit', function(e){
	    e.preventDefault();

	    $('.analysis_cont').show();
        $('.analysis_loader').show();

	    console.log(this.subscriber_email.value);
        console.log(this.subscriber_password.value);
        console.log(this.subscriber_plan.value);

        requestAjax({
//                url: 'http://localhost:8000/subscriber/register',
                url:"https://tweet-summary.herokuapp.com/subscriber/register",
                type: 'POST',
                data:{
                    'subscriber_email':this.subscriber_email.value,
                    'subscriber_password':this.subscriber_password.value,
                    'subscriber_plan':this.subscriber_plan.value
                }
            },
            this.dataset,
            'register',
            function(data){
                alert(data);
            }
        );
	});

	$('#subscription_form').on('submit', function(e){
        e.preventDefault();

        $('.analysis_cont').show();
        $('.analysis_loader').show();

        console.log(this.subscriber_email.value);
        console.log(this.subscriber_password.value);
        console.log(this.subscriber_topic.value);
        console.log(this.subscription_start_date.value);
        console.log(this.subscription_end_date.value);

        requestAjax({
//                url: 'http://localhost:8000/subscriber/add',
                url:"https://tweet-summary.herokuapp.com/subscriber/add",
                type: 'POST',
                data:{
                    'subscriber_email':this.subscriber_email.value,
                    'subscriber_password':this.subscriber_password.value,
                    'subscriber_topic':this.subscriber_topic.value,
                    'subscription_start_date':this.subscription_start_date.value,
                    'subscription_end_date':this.subscription_end_date.value
                }
            },
            this.dataset,
            'subscription',
            function(data){
                alert(data);
            }
        );
    });

    var loadProfileData = function(data){
        var user = JSON.parse(data.user)[0]
        var plan = JSON.parse(data.plan)[0]

        $('.profile_email').text(user.fields.email);
        $('.profile_email').attr('value',user.fields.email);

        $('.profile_password').text(user.fields.password);
        $('.profile_password').attr('value',user.fields.password);

        var plan_class_name = '.subscriber_plan_' + plan.fields.plan_name.toLowerCase();

        $(plan_class_name).toggleClass('selected_plan');
        $(plan_class_name + '>input').prop("checked", true);

        data.subscriptions.forEach(function(raw_subscription, index){
            var subscription = JSON.parse(raw_subscription)[0];
            var tr = $('<tr></tr>');
            var sno = $('<td></td>', {
                text: index+1
            });
            var topic = $('<td></td>', {
                text:subscription.fields.topic
            });
            var from = $('<td></td>', {
                text:subscription.fields.subscription_from
            });
            var to = $('<td></td>', {
                text:subscription.fields.subscription_to
            });
            var status = $('<td></td>', {
                 text:subscription.fields.subscription_status
             });
            var remove = $('<td></td>');
            var checkbox = $('<input/>',{
                type:'checkbox',
                class:'subscription_id',
                value:subscription.pk
            });

            remove.append(checkbox);
            tr.append(sno, topic, from, to, status, remove);
            $('.profile_subscriptions').append(tr);
        });
    };

    $('#view_and_update_form').on('submit', function(e){
        e.preventDefault();

        $('.analysis_cont').show();
        $('.analysis_loader').show();

        console.log(this.subscriber_email.value);
        console.log(this.subscriber_password.value);

        requestAjax({
//                url: 'http://localhost:8000/subscriber/view_or_update',
                url:"https://tweet-summary.herokuapp.com/subscriber/view_or_update",
                type: 'GET',
                data:{
                    'subscriber_email':this.subscriber_email.value,
                    'subscriber_password':this.subscriber_password.value
                }
            },
            this.dataset,
            'view',
            function(data){
                $('.subscriber_plan').removeClass('selected_plan');
                $('.profile_subscriptions').empty();
                loadProfileData(data)
                $('.profile_view_edit_light_box').show();
            }
        );
    });

    $('.close_light_box').on('click', function(){
        $('.profile_view_edit_light_box').hide();
        $('.analysis_cont').hide();
    });

    $('.update_form').on('submit', function(e){
        e.preventDefault();

        console.log(this.subscriber_email.value);
        console.log(this.subscriber_email.password);
        console.log(this.subscriber_plan.value);

        var sub_ids = [];

        for(var i=0;i<$('.subscription_id').length;i++){
            if($('.subscription_id')[i].checked){
                sub_ids.push($('.subscription_id')[i].value);
            }
        }

        console.log(sub_ids);

        var post_data = {
            'subscriber_email':this.subscriber_email.value,
            'subscriber_password':this.subscriber_password.value,
            'subscriber_plan':this.subscriber_plan.value,
            'subscription_ids':sub_ids
        }

        requestAjax({
//                url: 'http://localhost:8000/subscriber/view_or_update',
                url:"https://tweet-summary.herokuapp.com/subscriber/view_or_update",
                type: 'POST',
                data: post_data
            },
            this.dataset,
            'update',
            function(data){
                $('.subscriber_plan').removeClass('selected_plan');
                $('.profile_subscriptions').empty();
                $('.profile_view_edit_light_box').hide();
                alert(data);
            }
        );
    });

    $('.portal_service').on('mouseenter', function(){
        $(this).find('.display-after').fadeIn(2000, function(){
            $(this).find('.service_name').hide();
        });
    });
    $('.portal_service').on('mouseleave', function(){
        $(this).find('.display-after').hide();
        $(this).find('.service_name').show();
    });

});