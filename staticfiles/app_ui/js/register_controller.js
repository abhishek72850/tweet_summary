$(function(){

    $('#registerForm').on('submit',function(e){
        e.preventDefault();

        console.log(this.user_email.value);
        console.log(this.user_password.value);
        console.log(this.user_cnf_password.value);

        if(this.user_password.value !== this.user_cnf_password.value){
            showDialog('Password does not match', 'error');
            return;
        }

        requestAjax(
             {
                url: window.location.origin + "/api/account/register",
                type: "POST",
                data:{
                    'user_email':this.user_email.value,
                    'user_password':this.user_password.value,
                    'user_cnf_password':this.user_cnf_password.value,
                    'timezone_offset': moment().utcOffset()
                }
            },
            function(data){
                showDialog('User created successfully, please wait for the verification email', 'success');
            }
        );
    });
});