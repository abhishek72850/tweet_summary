$(function(){
    $('#planAssignForm').on('submit',function(e){
        e.preventDefault();

        console.log(this.plan_id.value);

        requestAjax(
             {
                url: window.location.origin + "/api/account/plan",
                type: "POST",
                data:{
                    'plan_id':this.plan_id.value
                }
            },
            function(data){
                showDialog(data, 'success');
            }
        );
    });
});