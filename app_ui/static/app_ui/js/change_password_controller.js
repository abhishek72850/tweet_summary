$(function(){
    $('#changePasswordForm').on('submit',function(e){
        e.preventDefault();

        console.log(this.current_password.value);
        console.log(this.new_password.value);
        console.log(this.confirm_password.value);

        if(this.new_password.value !== this.confirm_password.value){
            showDialog('Password does not match', 'error');
            return;
        }

        requestAjax(
             {
                url: window.location.origin + "/api/account/change_password",
                type: "POST",
                data:{
                    'current_password':this.current_password.value,
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