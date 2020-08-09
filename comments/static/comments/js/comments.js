function file_comment_ajax(url, comment_text) {
  const csrf_token = getCookie('csrftoken');
  $( document ).ready(function() {
    $.ajax({
      url: url,
      data: {comment: comment_text, csrfmiddlewaretoken: csrf_token,},
      type: 'POST',
    });
  });
}