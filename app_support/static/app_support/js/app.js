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
                var user = JSON.parse(data['user']);

                if(data['plan'] == null){
                    var plan = {}
                    $('#plan_subscribed').attr('value', plan.plan_status);
                }
                else{
                    var plan = JSON.parse(data['plan']);
                    $('#plan_subscribed').attr('value', plan.plan_name);
                }


                $('#user_email').attr('value', user.email);
                $('#registered_on').attr('value', getFormattedDatetime(user.created_at));

                $('#quick_analysis_quota').attr('value', user.quick_analysis_counter);
                $('#total_subscription').attr('value', data['subscriptions']);
                $('#email_verified').attr('value', user.email_verified);
                $('#account_status').val(user.status);
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

    $('#search_plan_requests_form').on('submit', function(e){
        e.preventDefault();

        var email = this.search_by_email.value;

        requestAjax(
            {
                url: window.location.origin + "/support/get_all_requests",
                type: "GET",
                data:{
                    'search_by_email':email
                }
            },
            function(data){
                request_list = data;

                $('.plan_request_row_element').remove();

                for(index in request_list){
                    user = JSON.parse(request_list[index][0]);
                    plan_request = JSON.parse(request_list[index][1]);

                    if(request_list[index][2] === null){
                        old_plan = {};
                    }
                    else{
                        old_plan = JSON.parse(request_list[index][2]);
                    }
                    new_plan = JSON.parse(request_list[index][3]);

                    var plan_request_row = $('<div></div>',{
                        'class':'plan_request_row  plan_request_row_element'
                    });
                    var sno = $('<span></span>',{
                        'text': parseInt(index) + 1
                    });
                    var email = $('<span></span>',{
                        'text': user['email']
                    });
                    var registered_on = $('<span></span>',{
                        'text': getFormattedDatetime(user['created_at'])
                    });
                    var old_plan = $('<span></span>',{
                        'text': old_plan.plan_name
                    });
                    var new_plan = $('<span></span>',{
                        'text': new_plan['plan_name']
                    });

                    if(plan_request['status'] === 'REQUESTED'){
                        var manage = $('<span></span>',{
                            'html': '<button class="accept_plan_change_request" data-request-id="'+ plan_request['id'] +'">Accept</button> <button class="decline_plan_change_request" data-request-id="'+ plan_request['id'] +'">Decline</button>'
                        });
                    }
                    else{
                        var manage = $('<span></span>',{
                            'text': plan_request['status']
                        });
                    }

                    plan_request_row.append(sno);
                    plan_request_row.append(email);
                    plan_request_row.append(registered_on);
                    plan_request_row.append(old_plan);
                    plan_request_row.append(new_plan);
                    plan_request_row.append(manage);

                    $('.plan_requests_list').append(plan_request_row);
                }
            }
        );
    });

    $('#search_upcoming_user_plans_form').on('submit', function(e){
        e.preventDefault();

        var email = this.search_by_email.value;

        requestAjax(
            {
                url: window.location.origin + "/support/get_all_upcoming_user_plans",
                type: "GET",
                data:{
                    'search_by_email':email
                }
            },
            function(data){
                request_list = data;

                $('.upcoming_user_plans_row_element').remove();

                for(index in request_list){
                    user = JSON.parse(request_list[index][0])[0];
                    upcoming_plan = JSON.parse(request_list[index][1])[0];

                    plan = JSON.parse(request_list[index][2])[0];

                    var upcoming_user_plans_row = $('<div></div>',{
                        'class':'upcoming_user_plans_row  upcoming_user_plans_row_element'
                    });
                    var sno = $('<span></span>',{
                        'text': parseInt(index) + 1
                    });
                    var email = $('<span></span>',{
                        'text': user['fields']['email']
                    });
                    var plan_name = $('<span></span>',{
                        'text': plan['fields']['plan_name']
                    });
                    var plan_starts_from = $('<span></span>',{
                        'text': getFormattedDatetime(upcoming_plan['fields']['plan_starts_from'])
                    });
                    var status = $('<span></span>',{
                        'text': upcoming_plan['fields']['status']
                    });

                    upcoming_user_plans_row.append(sno);
                    upcoming_user_plans_row.append(email);
                    upcoming_user_plans_row.append(registered_on);
                    upcoming_user_plans_row.append(old_plan);
                    upcoming_user_plans_row.append(new_plan);
                    upcoming_user_plans_row.append(manage);

                    $('.upcoming_user_plans_list').append(upcoming_user_plans_row);
                }
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

    $('#renew_user_plan').on('click', function(){
        requestAjax(
            {
                url: window.location.origin + "/support/renew_plan",
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
//                console.log(JSON.parse(data));
                user_list = data;

                $('.user_row_element').remove();

                for(user_index in user_list){
                    var user = JSON.parse(user_list[user_index]);

                    var user_row = $('<div></div>',{
                        'class':'user_row  user_row_element'
                    });
                    var sno = $('<span></span>',{
                        'text': parseInt(user_index) + 1
                    });
                    var email = $('<span></span>',{
                        'text': user['email']
                    });
                    var registered_on = $('<span></span>',{
                        'text': getFormattedDatetime(user['created_at'])
                    });
                    var email_verified = $('<span></span>',{
                        'text': user['email_verified']
                    });
                    var status = $('<span></span>',{
                        'text': user['status']
                    });
                    var manage = $('<span></span>',{
                        'html': '<button class="manage_user_button" data-id="'+ user['id'] +'">Manage</button>'
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

    $('body').delegate('.accept_plan_change_request','click',function(){
        var request_id = this.dataset.requestId;

        requestAjax(
            {
                url: window.location.origin + "/support/accept_requests",
                type: "POST",
                data:{
                    "plan_request_id": request_id
                }
            },
            function(data){
                alert(data);
            }
        );
    });

    $('body').delegate('.decline_plan_change_request','click',function(){
        var request_id = this.dataset.requestId;

        requestAjax(
            {
                url: window.location.origin + "/support/decline_requests",
                type: "POST",
                data:{
                    "plan_request_id": request_id
                }
            },
            function(data){
                alert(data);
            }
        );
    });

});