$(document).ready(function () {
    $(".file-comment").focusout(function () {
        console.log(this.id);
        const text = this.value;
        const url = '/file/' + this.id + '/update-comment/';
        const csrf_token = getCookie('csrftoken');

        $.ajax({
            url: url,
            data: {comment: text, csrfmiddlewaretoken: csrf_token,},
            type: 'POST',
        });

        $('#saved-'+this.id).fadeIn("slow").delay(1000).fadeOut("slow");
    })
});