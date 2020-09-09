$(function(){
    $('#subscribeForm').on('submit',function(e){
        e.preventDefault();

        console.log(this.search_topic.value);
        console.log(this.subscribe_start_date.value);
        console.log(this.subscribe_end_date.value);

        requestAjax(
             {
                url: window.location.origin + "/api/account/subscribe",
                type: "POST",
                data:{
                    'search_topic':this.search_topic.value,
                    'subscribe_start_date':this.subscribe_start_date.value,
                    'subscribe_end_date':this.subscribe_end_date.value
                }
            },
            function(data){
                showDialog(data, 'success');
            }
        );
    });
});