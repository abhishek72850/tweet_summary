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

	})
});