$(function(){
    $('#remove_button').prop('disabled', true);
    $('#remove_button').hide();

    var loadAccountDetails = function(){
        requestAjax(
             {
                url: window.location.origin + "/api/account/details",
                type: "GET",
                data:{}
            },
            function(data){
                $('.subscription_row').empty();

                var user = JSON.parse(data.user)
                var plan = JSON.parse(data.plan)

                $('.account_email').text(user.email);

                $('.account_password').text(user.password);
                $('.account_status').text(user.status);

                if(plan === null){
                    $('.account_quick_analysis').text('0');
                    $('.account_plan_name').text(user.plan_status);
                    $('.account_expiry').text('None');
                }
                else{
                    $('.account_quick_analysis').text(parseInt(plan.quick_analysis_quota) - parseInt(user.quick_analysis_counter));
                    $('.account_plan_name').text(plan.plan_name.toLowerCase());
                    $('.account_expiry').text(getFormattedDatetime(getFutureDate(user.plan_subscribed_at, parseInt(plan.plan_duration))));
                }

                data.subscriptions.forEach(function(raw_subscription, index){
                    var subscription = JSON.parse(raw_subscription);
                    var tr = $('<tr></tr>', {
                        class: 'subscription_row'
                    });
                    var sno = $('<td></td>', {
                        text: index+1
                    });
                    var topic = $('<td></td>', {
                        text:subscription.topic
                    });
                    var from = $('<td></td>', {
                        text:subscription.subscription_from
                    });
                    var to = $('<td></td>', {
                        text:subscription.subscription_to
                    });
                    var status = $('<td></td>', {
                         text:subscription.subscription_status
                    });
                    var remove = $('<td></td>');
                    var checkbox = $('<input/>',{
                        type:'checkbox',
                        class:'subscription_id',
                        name:'subscription',
                        value:subscription.id
                    });

                    remove.append(checkbox);
                    tr.append(sno, topic, from, to, status, remove);
                    $('.account_subscriptions').append(tr);
                });

                if(data.subscriptions.length > 0){
                    $('#remove_button').show();
                }
            }
        );
    }

    loadAccountDetails();


    $('body').delegate('.subscription_id','change',function(){
        var found_checked = false;

        for(var i=0;i<$('.subscription_id').length;i++){
            if($('.subscription_id')[i].checked){
                found_checked = true;
            }
        }

        if(found_checked){
            $('#remove_button').prop('disabled', false);
        }
        else{
            $('#remove_button').prop('disabled', true);
        }
    });


    $('#removeSubscriptionsForm').on('submit',function(e){
        e.preventDefault();

        var subscription_ids = [];

        for(var i=0;i<$('.subscription_id').length;i++){
            if($('.subscription_id')[i].checked){
                subscription_ids.push($('.subscription_id')[i].value);
            }
        }

        console.log(subscription_ids);

        requestAjax(
             {
                url: window.location.origin + "/api/account/details",
                type: "POST",
                data:{
                    'subscription_ids':subscription_ids
                }
            },
            function(data){
                showDialog(data, 'success');
            }
        );
    });
});