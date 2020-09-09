var showDialog = function(message, dialogType){
    $('#' + dialogType + 'DialogMessage').text(message);
    $('.' + dialogType + 'Dialog').show();
}

var getFutureDate = function(date_str, days){
    date = new Date(date_str);
    date.setDate(date.getDate() + days);

    return date.toDateString();
}

var getFormattedDatetime = function(date_str){
    date = new Date(date_str);

    month = (date.getMonth() + 1) >= 10 ? (date.getMonth() + 1) : "0" + (date.getMonth() + 1);
    day = date.getDate() >= 10 ? date.getDate() : "0" + date.getDate();

    hours = date.getHours() >= 10 ? date.getHours() : "0" + date.getHours();
    seconds = date.getSeconds() >= 10 ? date.getSeconds() : "0" + date.getSeconds();
    minutes = date.getMinutes() >= 10 ? date.getMinutes() : "0" + date.getMinutes()

    return date.getFullYear() + "-" + month + "-" + day + " " +  hours + ":" + minutes + ":" + seconds;
}

function createTextLinks_(text) {

  return (text || "").replace(
    /([^\S]|^)(((https?\:\/\/)|(www\.))(\S+))/gi,
    function(match, space, url){
      var hyperlink = url;
      if (!hyperlink.match('^https?:\/\/')) {
        hyperlink = 'http://' + hyperlink;
      }
      return space + '<a href="' + hyperlink + '">' + url + '</a>';
    }
  );
};

$(function(){
    $('.loaderContainer').hide();
    $('.dialogBox').hide();
});