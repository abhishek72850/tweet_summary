$(function(){
    $('#forgotPasswordForm').on('submit',function(e){
        e.preventDefault();

        console.log(this.user_email.value);

        requestAjax(
             {
                url: window.location.origin + "/api/account/forgot_password",
                type: "POST",
                data:{
                    'user_email':this.user_email.value
                }
            },
            function(data){
                showDialog(data, 'success');
            }
        );
    });
});