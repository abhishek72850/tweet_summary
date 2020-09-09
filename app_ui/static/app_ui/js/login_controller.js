$(function(){

    $('#loginForm').on('submit',function(e){
        e.preventDefault();

        console.log(this.user_email.value);
        console.log(this.user_password.value);

        requestAjax(
             {
                url: window.location.origin + "/api/account/login",
                type: "POST",
                data:{
                    'user_email':this.user_email.value,
                    'user_password':this.user_password.value
                }
            },
            function(data){
                window.location.href = window.location.origin + "/app/home";
            }
        );
    });
});