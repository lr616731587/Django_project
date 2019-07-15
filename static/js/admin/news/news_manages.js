$(function () {
  let $startTime = $("input[name=start_time]");
  let $endTime = $("input[name=end_time]");
  const config = {
    // �Զ��ر�
    autoclose: true,
    // ���ڸ�ʽ
    format: 'yyyy/mm/dd',
    // ѡ������Ϊ����
    language: 'zh-CN',
    // �Ż���ʽ
    showButtonPanel: true,
    // ��������
    todayHighlight: true,
    // �Ƿ������е������ʾ����
    calendarWeeks: true,
    // ���
    clearBtn: true,
    // 0 ~11  ��վ���ߵ�ʱ��
    startDate: new Date(2018, 10, 1),
    // ����
    endDate: new Date(),
  };
  $startTime.datepicker(config);
  $endTime.datepicker(config);

  // ɾ����ǩ
  let $newsDel = $(".btn-del");  // 1. ��ȡɾ����ť
  $newsDel.click(function () {   // 2. ��������¼�
    let _this = this;
    let sNewsId = $(this).data('news-id');
    swal({
      title: "ȷ��ɾ����ƪ������?",
      text: "ɾ��֮�󣬽��޷��ָ���",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "ȷ��ɾ��",
      cancelButtonText: "ȡ��",
      closeOnConfirm: true,
      animation: 'slide-from-top',
    }, function () {

      $.ajax({
        // �����ַ
        url: "/admin/news/" + sNewsId + "/",  // urlβ����Ҫ���/
        // ����ʽ
        type: "DELETE",
        dataType: "json",
      })
        .done(function (res) {
          if (res.errno === "0") {
            // ���±�ǩ�ɹ�
            message.showSuccess("��ǩɾ���ɹ�");
            $(_this).parents('tr').remove();
          } else {
            swal({
              title: res.errmsg,
              type: "error",
              timer: 1000,
              showCancelButton: false,
              showConfirmButton: false,
            })
          }
        })
        .fail(function () {
          message.showError('��������ʱ�������ԣ�');
        });
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