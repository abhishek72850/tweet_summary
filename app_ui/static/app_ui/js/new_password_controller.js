$(function(){
    $('#resetPasswordForm').on('submit',function(e){
        e.preventDefault();

        console.log(this.new_password.value);
        console.log(this.confirm_password.value);

        if(this.new_password.value !== this.confirm_password.value){
            showDialog('Password does not match', 'error');
            return;
        }

        requestAjax(
             {
                url: window.location.origin + "/api/account/reset_password",
                type: "POST",
                data:{
                    'verification_code':app_env.verification_code,
                    'new_password':this.new_password.value,
                    'confirm_password':this.confirm_password.value
                }
            },
            function(data){
                showDialog(data, 'success');
            }
        );
    });
});