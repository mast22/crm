$(document).ready(function () {
  $("button[name='reply']").click(function () {
    let comment_id = $(this).parent().attr("id");
    $("#commentForm").css({ display: "block" });
    $("input[name='comment-id']").attr({ value: comment_id });
    $("h6").text("Ответить на комментарий " + comment_id);
  });
});
