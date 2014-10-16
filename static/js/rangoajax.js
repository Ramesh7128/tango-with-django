$(document).ready(function() {


    $('#likes').click(function() {
        var catid;
        catid = $(this).attr("data-catid");
        $.get('/rango/like_category/', {category_id: catid}, function(data) {
            $('#like_count').html(data);
            $('#likes').hide();
        });
    });


    $('.rango-add').click(function() {
        var catid;
        var pagetitle;
        var pageurl;
        catid = $(this).attr("data-catid");
        pagetitle = $(this).attr("data-title");
        pageurl = $(this).attr("data-url");
        $.get('/rango/auto_addpage/', {category_id: catid, page_title: pagetitle, page_url: pageurl}, function(data) {
            $('#pages').html(data);
            $('#addlinks').hide();
        });
    });

    $('#test').keyup(function() {
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
            $('#cats').html(data);

        });
    });
});

