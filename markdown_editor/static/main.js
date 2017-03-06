
function preview() {
  $.ajax({
    type: 'POST',
    url: '/preview',
    data: $('#raw').val(),
    contentType: 'text/plain',
    success: function(data) {
      $('#mirror').html(data);
    }
  });
}

function createDoc() {
  $.ajax({
    type: 'GET',
    url: '/create',
    success: function(data) {
      $('#raw').val('');
      $('#mirror').html('');
      $('#doc_id').html(data['fid']);
      document.title = data['title'];
    }
  });
}

function previewDoc() {
  fid = $('#doc_id').html();
  window.location.href = '/showpreview/' + fid
}

function test() {
    fid = $('#doc_id').html();
    window.location.href = '/showpreview/' + fid
}

function exportDoc() {
    window.print()
}


function sidebar() {
    $('.ui.labeled.icon.sidebar').sidebar('toggle');
}

function deleteDoc(fid, title) {
    $('.ui.icon.header').html('<i class="trash icon"></i>彻底删除文件&nbsp<span style="color:#00B5AD">' + title + '</span>');
    $(".ui.basic.modal").modal({
        onApprove: function() {
            var delfid = fid.toString();
            var curfid = $('#doc_id').html();
            $.ajax({
                type: 'POST',
                url: '/delete',
                data: JSON.stringify({delfid: delfid, curfid: curfid}),
                contentType: 'json',
                success: function(data) {
                    if(data['refresh'] == '1') {
                        window.location.href = '/'
                    } else {
                        sidebar();
                    }
                }
            });
        }
    }).modal('show');
}

$(document).ready(function() {
  $(document).on('keydown', function(e){
      if(e.ctrlKey && e.which === 83){ // Check for the Ctrl key being pressed, and if the key = [S] (83)
          $('#sync_tooltip').show();
          raw = $('#raw').val(),
          html = $('#mirror').html();
          fid = $('#doc_id').html();
          $.ajax({
            type: 'POST',
            url: '/save',
            data: JSON.stringify({fid: fid, raw: raw, html: html}),
            contentType: 'json',
            success: function(data) {
                $('#sync_tooltip').hide();
                document.title = data['title'];
                $('#doc_id').html(data['fid']);
            }
          });
          e.preventDefault();
      }
  });


  $('#doc_bar').on('click', function() {
    $.ajax({
      type: 'GET',
      url: '/mydocs',
      success: function(data) {
        $('#sidebar').html(data);
      }
    });
  });

});
