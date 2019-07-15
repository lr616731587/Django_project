


$(function () {
  // δ��¼��ʾ��
  let $loginComment = $('.please-login-comment input');
  let $send_comment = $('.logged-comment .comment-btn');

  $('.comment-list').delegate('a,input', 'click', function () {

    let sClassValue = $(this).prop('class');

    if (sClassValue.indexOf('reply_a_tag') >= 0) {
      $(this).next().toggle();
    }

    if (sClassValue.indexOf('reply_cancel') >= 0) {
      $(this).parent().toggle();
    }

    if (sClassValue.indexOf('reply_btn') >= 0) {
      // ��ȡ����id������id����������
      let $this = $(this);
      let news_id = $this.parent().attr('news-id');
      let parent_id = $this.parent().attr('comment-id');
      let content = $this.prev().val();

      if (!content) {
        message.showError('�������������ݣ�');
        return
      }
      // ���巢����˵Ĳ���
      let sDataParams = {
        "content": content,
        "parent_id": parent_id
      };
      $.ajax({
        url: "/news/" + news_id + "/comments/",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(sDataParams),
        dataType: "json",
      })
        .done(function (res) {
          if (res.errno === "0") {
            let one_comment = res.data;
            let html_comment = ``;
            html_comment += `
          <li class="comment-item">
            <div class="comment-info clearfix">
              <img src="/static/images/avatar.jpeg" alt="avatar" class="comment-avatar">
              <span class="comment-user">${one_comment.author}</span>
            </div>
            <div class="comment-content">${one_comment.content}</div>

                <div class="parent_comment_text">
                  <div class="parent_username">${one_comment.parent.author}</div>
                  <br/>
                  <div class="parent_content_text">
                    ${one_comment.parent.content}
                  </div>
                </div> 

              <div class="comment_time left_float">${one_comment.update_time}</div>
              <a href="javascript:;" class="reply_a_tag right_float">�ظ�</a>
              <form class="reply_form left_float" comment-id="${one_comment.content_id}" news-id="${one_comment.news_id}">
                <textarea class="reply_input"></textarea>
                <input type="button" value="�ظ�" class="reply_btn right_float">
                <input type="reset" name="" value="ȡ��" class="reply_cancel right_float">
              </form>

          </li>`;

            $(".comment-list").prepend(html_comment);
            $this.prev().val('');   // ��������
            $this.parent().hide();  // �ر����ۿ�

          } else if (res.errno === "4101") {
            // �û�δ��¼
            message.showError(res.errmsg);
            setTimeout(function () {
              // �ض��򵽴򿪵�¼ҳ��
              window.location.href = "/users/login/";
            }, 800)

          } else {
            // ʧ�ܣ���ӡ������Ϣ
            message.showError(res.errmsg);
          }
        })
        .fail(function () {
          message.showError('��������ʱ�������ԣ�');
        });

    }
  });


  // ������ۿ��ض����û���¼ҳ��
  $loginComment.click(function () {

    $.ajax({
      url: "/news/" + $(".please-login-comment").attr('news-id') + "/comments/",
      type: "POST",
      contentType: "application/json; charset=utf-8",
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "4101") {
          message.showError("���¼֮�������ۣ�");
          setTimeout(function () {
            // �ض��򵽴򿪵�¼ҳ��
            window.location.href = "/users/login/";
          }, 800)

        } else {
          // ʧ�ܣ���ӡ������Ϣ
          message.showError(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('��������ʱ�������ԣ�');
      });
  });

  // ��������
  $send_comment.click(function () {
    // ��ȡ����id������id����������
    let $this = $(this);
    let news_id = $this.parent().attr('news-id');
    // let parent_id = $this.parent().attr('comment-id');
    let content = $this.prev().val();

    if (!content) {
      message.showError('�������������ݣ�');
      return
    }
    // ���巢����˵Ĳ���
    let sDataParams = {
      "content": content
    };
    $.ajax({
      url: "/news/" + news_id + "/comments/",
      type: "POST",
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(sDataParams),
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          let one_comment = res.data;
          let html_comment = ``;
          html_comment += `
          <li class="comment-item">
            <div class="comment-info clearfix">
              <img src="/static/images/avatar.jpeg" alt="avatar" class="comment-avatar">
              <span class="comment-user">${one_comment.author}</span>
            </div>
            <div class="comment-content">${one_comment.content}</div>

              <div class="comment_time left_float">${one_comment.update_time}</div>
              <a href="javascript:;" class="reply_a_tag right_float">�ظ�</a>
              <form class="reply_form left_float" comment-id="${one_comment.content_id}" news-id="${one_comment.news_id}">
                <textarea class="reply_input"></textarea>
                <input type="button" value="�ظ�" class="reply_btn right_float">
                <input type="reset" name="" value="ȡ��" class="reply_cancel right_float">
              </form>

          </li>`;

          $(".comment-list").prepend(html_comment);
          $this.prev().val('');   // ��������
          // $this.parent().hide();  // �ر����ۿ�

        } else if (res.errno === "4101") {
          // �û�δ��¼
          message.showError(res.errmsg);
          setTimeout(function () {
            // �ض��򵽴򿪵�¼ҳ��
            window.location.href = "/users/login/";
          }, 800)

        } else {
          // ʧ�ܣ���ӡ������Ϣ
          message.showError(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('��������ʱ�������ԣ�');
      });
  });

  // get cookie using jQuery
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  // Setting the token on the AJAX request
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });
});