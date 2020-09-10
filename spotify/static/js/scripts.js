$(function () {
    var resfresh=setInterval(function(){
        $.ajax({
                type: 'GET',
                url: '/ajax/get/orders',
                cache:false,
                datatype: 'html',
                success: function (data) {
                    $('#table').html(data)

                }
            });

    },6000)



});
