function delete_file_ajax(url, self) {
  const csrf_token = getCookie('csrftoken');
    $.ajax({
      url: url,
      type: 'DELETE',
    });
    self.parent().slideToggle();
}