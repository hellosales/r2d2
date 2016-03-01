var Site = {
    init : function (context) {
        var context = context || document;

        $(document).foundation();
        //fix foundation
        $( window ).resize(function() {
            $('data-magellan-expedition-clone').remove()
        });
    },
};


$(function () {
    Site.init();
});



