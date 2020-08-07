$(function(){
    var getFormattedDatetime = function(date_str){
        date = new Date(date_str);

        month = (date.getMonth() + 1) >= 10 ? (date.getMonth() + 1) : "0" + (date.getMonth() + 1);
        day = date.getDate() >= 10 ? date.getDate() : "0" + date.getDate();

        hours = date.getHours() >= 10 ? date.getHours() : "0" + date.getHours();
        seconds = date.getSeconds() >= 10 ? date.getSeconds() : "0" + date.getSeconds();
        minutes = date.getMinutes() >= 10 ? date.getMinutes() : "0" + date.getMinutes()

        return date.getFullYear() + "-" + month + "-" + day + " " +  hours + ":" + minutes + ":" + seconds;
    }

    var loadUserDetails = function(){
        requestAjax(
            {
                url: window.location.origin + "/support/get_user",
                type: "GET",
                data:{
                    "user_id": app_env.user_id
                }
            },
            function(data){
                var user = JSON.parse(data['user'])[0];
                var plan = JSON.parse(data['plan'])[0];

                $('#user_email').attr('value', user.fields.email);
                $('#registered_on').attr('value', getFormattedDatetime(user.fields.created_at));
                $('#plan_subscribed').attr('value', plan.fields.plan_name);
                $('#quick_analysis_quota').attr('value', user.fields.quick_analysis_counter);
                $('#total_subscription').attr('value', data['subscriptions']);
                $('#email_verified').attr('value', user.fields.email_verified);
                $('#account_status').val(user.fields.status);
            }
        );
    }

    var loadSubscriptionDetails = function(){
        requestAjax(
            {
                url: window.location.origin + "/support/get_subscription",
                type: "GET",
                data:{
                    "subscription_id": app_env.subscription_id
                }
            },
            function(data){
                var user = JSON.parse(data['user'])[0];
                var plan = JSON.parse(data['plan'])[0];
                var subscription = JSON.parse(data['subscription'])[0];

                $('#user_email').attr('value', user.fields.email);
                $('#plan_subscribed').attr('value', plan.fields.plan_name);
                $('#subscription_topic').attr('value', subscription.fields.topic);
                $('#subscription_created_on').attr('value', getFormattedDatetime(subscription.fields.created_at));
                $('#subscription_from').attr('value', getFormattedDatetime(subscription.fields.subscription_from));
                $('#subscription_to').attr('value', getFormattedDatetime(subscription.fields.subscription_to));
                $('#subscription_status').val(subscription.fields.subscription_status);
            }
        );
    }

    if(window.location.pathname === '/support/update_user'){
        loadUserDetails();
    }
    else if(window.location.pathname === '/support/update_subscription'){
        loadSubscriptionDetails();
    }

    $('#update_user_form').on('submit', function(e){
        e.preventDefault();
        var status = this.account_status.value;

        requestAjax(
            {
                url: window.location.origin + "/support/update_user_status",
                type: "POST",
                data:{
                    "user_id": app_env.user_id,
                    "status": status
                }
            },
            function(data){
                alert(data);
            }
        );
    });

    $('#update_subscription_form').on('submit', function(e){
        e.preventDefault();
        var status = this.subscription_status.value;

        requestAjax(
            {
                url: window.location.origin + "/support/update_subscription_status",
                type: "POST",
                data:{
                    "subscription_id": app_env.subscription_id,
                    "status": status
                }
            },
            function(data){
                alert(data);
            }
        );
    });

    $('#send_user_verification').on('click', function(){
        requestAjax(
            {
                url: window.location.origin + "/support/send_user_verification",
                type: "POST",
                data:{
                    "user_id": app_env.user_id,
                }
            },
            function(data){
                alert(data);
            }
        );
    });

    $('#send_subscription_verification').on('click', function(){
        requestAjax(
            {
                url: window.location.origin + "/support/send_subscription_verification",
                type: "POST",
                data:{
                    "subscription_id": app_env.subscription_id
                }
            },
            function(data){
                alert(data);
            }
        );
    });

    $('#test_plan_assign_form').on('submit',function(e){
        e.preventDefault();

        var email = this.test_user_email.value;
        var password = this.test_user_password.value;
        var cnf_password = this.test_user_cnf_password.value;

        if(password.trim() !== cnf_password.trim()){
            alert('Password does not matched!!');
        }
        else{
            requestAjax(
                {
                    url: window.location.origin + "/support/assign",
                    type: "POST",
                    data:{
                        'test_user_email':email,
                        'test_user_password':password,
                        'test_user_cnf_password':cnf_password,
                    }
                },
                function(data){
                    alert(data);
                }
            );
        }
    });

    $('#search_users_form').on('submit',function(e){
        e.preventDefault();

        var email = this.search_by_email.value;

        requestAjax(
            {
                url: window.location.origin + "/support/all_users",
                type: "GET",
                data:{
                    'search_by_email':email
                }
            },
            function(data){
                console.log(JSON.parse(data));
                user_list = JSON.parse(data);

                $('.user_row_element').remove();

                for(user_index in user_list){

                    var user_row = $('<div></div>',{
                        'class':'user_row  user_row_element'
                    });
                    var sno = $('<span></span>',{
                        'text': parseInt(user_index) + 1
                    });
                    var email = $('<span></span>',{
                        'text': user_list[user_index]['fields']['email']
                    });
                    var registered_on = $('<span></span>',{
                        'text': user_list[user_index]['fields']['created_at']
                    });
                    var email_verified = $('<span></span>',{
                        'text': user_list[user_index]['fields']['email_verified']
                    });
                    var status = $('<span></span>',{
                        'text': user_list[user_index]['fields']['status']
                    });
                    var manage = $('<span></span>',{
                        'html': '<button class="manage_user_button" data-id="'+ user_list[user_index]['pk'] +'">Manage</button>'
                    });

                    user_row.append(sno);
                    user_row.append(email);
                    user_row.append(registered_on);
                    user_row.append(email_verified);
                    user_row.append(status);
                    user_row.append(manage);

                    $('.user_list').append(user_row);
                }
            }
        );
    });

    $('#search_subscriptions_form').on('submit',function(e){
        e.preventDefault();

        var email = this.search_by_email.value;

        requestAjax(
            {
                url: window.location.origin + "/support/all_subscriptions",
                type: "GET",
                data:{
                    'search_by_email':email
                }
            },
            function(data){
                subscription_list = data;

                $('.user_row_element').remove();

                for(index in subscription_list){
                    user = JSON.parse(subscription_list[index][0])[0];
                    subscription = JSON.parse(subscription_list[index][1])[0];
                    var user_row = $('<div></div>',{
                        'class':'user_row  user_row_element'
                    });
                    var sno = $('<span></span>',{
                        'text': parseInt(index) + 1
                    });
                    var email = $('<span></span>',{
                        'text': user['fields']['email']
                    });
                    var topic = $('<span></span>',{
                        'text': subscription['fields']['topic']
                    });
                    var created_on = $('<span></span>',{
                        'text': getFormattedDatetime(subscription['fields']['created_at'])
                    });
                    var from = $('<span></span>',{
                        'text': getFormattedDatetime(subscription['fields']['subscription_from'])
                    });
                    var to = $('<span></span>',{
                        'text': getFormattedDatetime(subscription['fields']['subscription_to'])
                    });
                    var status = $('<span></span>',{
                        'text': subscription['fields']['subscription_status']
                    });
                    var manage = $('<span></span>',{
                        'html': '<button class="manage_subscription_button" data-id="'+ subscription['pk'] +'">Manage</button>'
                    });

                    user_row.append(sno);
                    user_row.append(email);
                    user_row.append(topic);
                    user_row.append(created_on);
                    user_row.append(from);
                    user_row.append(to);
                    user_row.append(status);
                    user_row.append(manage);

                    $('.user_list').append(user_row);
                }
            }
        );
    });

    $('body').delegate('.manage_user_button','click',function(){
        window.location.href = window.location.origin + '/support/update_user?id=' + this.dataset.id;
    });

    $('body').delegate('.manage_subscription_button','click',function(){
        window.location.href = window.location.origin + '/support/update_subscription?id=' + this.dataset.id;
    });

});