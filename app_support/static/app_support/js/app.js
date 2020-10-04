$(function(){
    var getFutureDate = function(date_str, days){
        return moment(date_str).utc().add({days:days}).format();
    }

    var getUTCDateTime = function(date_str){
        data = new Date(date_str)  
    }

    var getLocalDatetime = function(date_str, offset){
        return moment(date_str).utc().add({minutes:offset}).format();
    }

    var getFormattedDatetime = function(date_str){
        return moment(date_str).utc().format('DD MMM YYYY hh:mm:ssA');
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
                    $('#plan_subscribed').attr('value', '-');
                    $('#plan_subscribed_on').attr('value', '-');
                    $('#plan_status').attr('value', user.plan_status);
                    $('#plan_expires_on').attr('value','-');
                }
                else{
                    var plan = JSON.parse(data['plan']);
                    $('#plan_subscribed').attr('value', plan.plan_name);
                    $('#plan_subscribed_on').attr('value', getFormattedDatetime(getLocalDatetime(user.plan_subscribed_at, user['timezone_offset'])));
                    $('#plan_status').attr('value', user.plan_status);
                    $('#plan_expires_on').attr('value',getFormattedDatetime(getLocalDatetime(getFutureDate(user.plan_subscribed_at, parseInt(plan.plan_duration)), user['timezone_offset'])));
                }


                $('#user_email').attr('value', user.email);
                $('#registered_on').attr('value', getFormattedDatetime(getLocalDatetime(user.created_at, user['timezone_offset'])));

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
                var user = JSON.parse(data['user']);
                var plan = JSON.parse(data['plan']);
                var subscription = JSON.parse(data['subscription']);

                $('#user_email').attr('value', user.email);
                $('#plan_subscribed').attr('value', plan.plan_name);
                $('#subscription_topic').attr('value', subscription.topic);
                $('#subscription_created_on').attr('value', getFormattedDatetime(getLocalDatetime(subscription.created_at, user['timezone_offset'])));
                $('#subscription_from').attr('value', getFormattedDatetime(getLocalDatetime(subscription.subscription_from, user['timezone_offset'])));
                $('#subscription_to').attr('value', getFormattedDatetime(getLocalDatetime(subscription.subscription_to, user['timezone_offset'])));
                $('#subscription_status').val(subscription.subscription_status);
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
                        'text': getFormattedDatetime(getLocalDatetime(plan_request['created_at'], user['timezone_offset']))
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
                    user = JSON.parse(request_list[index][0]);
                    upcoming_plan = JSON.parse(request_list[index][1]);

                    plan = JSON.parse(request_list[index][2]);

                    var upcoming_user_plans_row = $('<div></div>',{
                        'class':'upcoming_user_plans_row  upcoming_user_plans_row_element'
                    });
                    var sno = $('<span></span>',{
                        'text': parseInt(index) + 1
                    });
                    var email = $('<span></span>',{
                        'text': user['email']
                    });
                    var created_on = $('<span></span>',{
                        'text': getFormattedDatetime(getLocalDatetime(upcoming_plan['created_at'], user['timezone_offset']))
                    });
                    var plan_name = $('<span></span>',{
                        'text': plan['plan_name']
                    });
                    var plan_starts_from = $('<span></span>',{
                        'text': getFormattedDatetime(getLocalDatetime(upcoming_plan['plan_starts_from'], user['timezone_offset']))
                    });
                    var plan_expires_on = $('<span></span>',{
                        'text': getFormattedDatetime(getLocalDatetime(getFutureDate(upcoming_plan['plan_starts_from'], plan['plan_duration']), user['timezone_offset']))
                    });
                    var status = $('<span></span>',{
                        'text': upcoming_plan['status']
                    });

                    upcoming_user_plans_row.append(sno);
                    upcoming_user_plans_row.append(email);
                    upcoming_user_plans_row.append(created_on);
                    upcoming_user_plans_row.append(plan_name);
                    upcoming_user_plans_row.append(plan_starts_from);
                    upcoming_user_plans_row.append(plan_expires_on);
                    upcoming_user_plans_row.append(status);

                    $('.upcoming_user_plans_list').append(upcoming_user_plans_row);
                }
            }
        );
    });


    $('#search_user_plan_history_form').on('submit', function(e){
        e.preventDefault();

        var email = this.search_by_email.value;

        requestAjax(
            {
                url: window.location.origin + "/support/get_all_plan_history",
                type: "GET",
                data:{
                    'search_by_email':email
                }
            },
            function(data){
                request_list = data;

                $('.user_plan_history_row_element').remove();

                for(index in request_list){
                    user = JSON.parse(request_list[index][0]);
                    plan_history = JSON.parse(request_list[index][1]);
                    plan = JSON.parse(request_list[index][2])

                    var user_plan_history_row = $('<div></div>',{
                        'class':'user_plan_history_row  user_plan_history_row_element'
                    });
                    var sno = $('<span></span>',{
                        'text': parseInt(index) + 1
                    });
                    var email = $('<span></span>',{
                        'text': user['email']
                    });
                    var plan_requested_on = $('<span></span>',{
                        'text': getFormattedDatetime(getLocalDatetime(plan_history['created_at'], user['timezone_offset']))
                    });
                    var plan_name = $('<span></span>',{
                        'text': plan['plan_name']
                    });
                    var plan_started_from = $('<span></span>',{
                        'text': getFormattedDatetime(getLocalDatetime(plan_history['plan_started_from'], user['timezone_offset']))
                    });
                    var plan_expires_on = $('<span></span>',{
                        'text': getFormattedDatetime(getLocalDatetime(getFutureDate(plan_history['plan_started_from'], plan['plan_duration']), user['timezone_offset']))
                    });
                    var payment_id = $('<span></span>',{
                        'text': plan_history['payment_id']
                    });
                    var payment_mode = $('<span></span>',{
                        'text': plan_history['payment_mode']
                    });

                    user_plan_history_row.append(sno);
                    user_plan_history_row.append(email);
                    user_plan_history_row.append(plan_requested_on);
                    user_plan_history_row.append(plan_name);
                    user_plan_history_row.append(plan_started_from);
                    upcoming_user_plans_row.append(plan_expires_on);
                    user_plan_history_row.append(payment_id);
                    user_plan_history_row.append(payment_mode);

                    $('.user_plan_history_list').append(user_plan_history_row);
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
        $('.payment_detail_overlay_cont').show();
        
        $('#renewPlanPaymentForm').on('submit', function(e){

            e.preventDefault();

            console.log(this.payment_id.value);
            console.log(this.payment_mode.value);

            requestAjax(
                {
                    url: window.location.origin + "/support/renew_plan",
                    type: "POST",
                    data:{
                        "user_id": app_env.user_id,
                        "payment_id":this.payment_id.value,
                        "payment_mode":this.payment_mode.value
                    }
                },
                function(data){
                    alert(data);
                    $('.payment_detail_overlay_cont').hide();
                }
            );
        });
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

        var email = this.user_email.value;
        // var password = this.test_user_password.value;
        // var cnf_password = this.test_user_cnf_password.value;
        // if(password.trim() !== cnf_password.trim()){
        //     alert('Password does not matched!!');
        // }

        requestAjax(
            {
                url: window.location.origin + "/support/assign",
                type: "POST",
                data:{
                    'user_email':email,
                    // 'test_user_password':password,
                    // 'test_user_cnf_password':cnf_password,
                }
            },
            function(data){
                alert(data);
            }
        );
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
                        'text': getFormattedDatetime(getLocalDatetime(user['created_at'], user['timezone_offset']))
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
                    user = JSON.parse(subscription_list[index][0]);
                    subscription = JSON.parse(subscription_list[index][1]);
                    var user_row = $('<div></div>',{
                        'class':'user_row  user_row_element'
                    });
                    var sno = $('<span></span>',{
                        'text': parseInt(index) + 1
                    });
                    var email = $('<span></span>',{
                        'text': user['email']
                    });
                    var topic = $('<span></span>',{
                        'text': subscription['topic']
                    });
                    var created_on = $('<span></span>',{
                        'text': getFormattedDatetime(getLocalDatetime(subscription['created_at'], user['timezone_offset']))
                    });
                    var from = $('<span></span>',{
                        'text': getFormattedDatetime(getLocalDatetime(subscription['subscription_from'], user['timezone_offset']))
                    });
                    var to = $('<span></span>',{
                        'text': getFormattedDatetime(getLocalDatetime(subscription['subscription_to'], user['timezone_offset']))
                    });
                    var status = $('<span></span>',{
                        'text': subscription['subscription_status']
                    });
                    var manage = $('<span></span>',{
                        'html': '<button class="manage_subscription_button" data-id="'+ subscription['id'] +'">Manage</button>'
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

    $('.close_plan_payment_form').on('click', function(){
        $('.payment_detail_overlay_cont').hide();
    })

    $('body').delegate('.manage_user_button','click',function(){
        window.location.href = window.location.origin + '/support/update_user?id=' + this.dataset.id;
    });

    $('body').delegate('.manage_subscription_button','click',function(){
        window.location.href = window.location.origin + '/support/update_subscription?id=' + this.dataset.id;
    });

    $('body').delegate('.accept_plan_change_request','click',function(){
        $('.payment_detail_overlay_cont').show();

        var request_id = this.dataset.requestId;

        $('#changePlanPaymentForm').on('submit', function(e){
            e.preventDefault();

            console.log(this.payment_id.value);
            console.log(this.payment_mode.value);

            requestAjax(
                {
                    url: window.location.origin + "/support/accept_requests",
                    type: "POST",
                    data:{
                        "plan_request_id": request_id,
                        "payment_id":this.payment_id.value,
                        "payment_mode":this.payment_mode.value
                    }
                },
                function(data){
                    alert(data);
                    $('.payment_detail_overlay_cont').hide();
                }
            );
        });
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