var requestAjax=function(options, callback){

	var object = {
        url: window.location.origin,
        data:{},
        headers: { "X-CSRFToken": app_env.csrf_token },
        type:"GET",
        datatype:'jsonp'
    };
    $('.loaderContainer').show();
	$.extend(object,options);

	xhr = $.ajax(object).done(function(data){
		console.log(data);
        $('.loaderContainer').hide();
        callback(data['data']);
	}).fail(function( jqXHR, textStatus, errorThrown ) {
		console.log(jqXHR);
        $('.loaderContainer').hide();
        showDialog(jqXHR.responseJSON.data, 'error');
	});
}
