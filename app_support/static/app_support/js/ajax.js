var requestAjax=function(options, callback){

	var object = {
		url: window.location.origin,
		data:{},
		headers: { "X-CSRFToken": app_env.csrf_token },
		type:"GET",
		datatype:'jsonp'
	};

	$.extend(object,options);

    $('.loader_cont').show();

	xhr = $.ajax(object).done(function(data){
		console.log(data);
		$('.loader_cont').hide();
		callback(data['data']);

	}).fail(function( jqXHR, textStatus, errorThrown ) {
		console.log(jqXHR);
		$('.loader_cont').hide();
        alert(jqXHR.responseJSON.data);
//		alert('Something went wrong. Please try again');
	});
}
