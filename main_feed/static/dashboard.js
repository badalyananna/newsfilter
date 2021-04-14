function updateUnread(data) {
  $.each(data[0].topic_unread_values, function(){
    $('#' + this.id).text(this.value);
    if (this.value > 0) {
      $('#' + this.id).show();
    } else if (this.value == 0) {
      $('#' + this.id).hide();
    }; 
  });
  $.each(data[0].website_unread_values, function(){
    $('#' + this.id).text(this.value);
    if (this.value > 0) {
      $('#' + this.id).show();
    } else if (this.value == 0) {
      $('#' + this.id).hide();
    }; 
  });
}


$(document).on('click', '.readbutton', function() {
  var catid;
  catid = $(this).attr("data-catid");
  $.ajax(
  {
      type:"GET",
      url: "/feed/read",
      data:{
               piece_id: catid
      },
      success: function( data ) 
      {
        if (data[0].status == false)  {
          $( '#piece'+ catid ).css("color", "#888");
        } else if (data[0].status == true) {
          $( '#piece'+ catid ).css("color", "");
        };
        updateUnread(data);
        
      }
   })
   return false
});

$(document).on('click', '.importantbtn', function() {
  var catid;
  catid = $(this).attr("data-catid");
  $.ajax(
  {
      type:"GET",
      url: "/feed/markimportant",
      data:{
               piece_id: catid
      },
      success: function( data ) 
      {
        if (data == "True")  {
          $( '#piece'+ catid ).css("background-color", "#eee");
        } else if (data == "False") {
          $( '#piece'+ catid ).css("background-color", "");
        }
        
      }
   })
   return false
});

$('.markallread').click(function(){
  $.ajax(
  {
      type:"GET",
      url: "/feed/markallread",
      data:{

      },
      success: function( data ) 
      { 
        $('.card').each(function() {
          if ($(this).css('background-color') == 'rgb(255, 255, 255)') {
            $(this).css('color', '#888')
          };
        });     
        updateUnread(data);
      }
   })
   return false
});

$('.update-btn').click(function(){
  var cat;
  cat = $(this).attr("data-category");
  var type;
  type = $(this).attr("data-type");
  $.ajax(
  {
      type:"GET",
      url: "/feed/update",
      data:{
        category: cat,
        pk: type,
      },
      dataType: 'json',
      beforeSend:function(){
        $(".last-updated").text("Loading ... ");
      },
      success: function( data ) 
      { 
        $('.no-news-message').remove();
        $('.last-updated').text("Last updated on " + data[0].last_upd);
        $('.news-container').prepend(data[0].updated_content);
        updateUnread(data);        
      }
   })
   return false
});

$('.load-old-btn').click(function(){
  var cat;
  cat = $(this).attr("data-category");
  var type;
  type = $(this).attr("data-type");
  var displayed;
  displayed = parseInt($(this).attr("data-displayed"));
  var undisplayed;
  undisplayed = parseInt($(this).attr("data-undisplayed"));
  $.ajax(
  {
      type:"GET",
      url: "/feed/loadold",
      data:{
        category: cat,
        pk: type,
        displayed_old_pieces: displayed,
      },
      success: function( data ) 
      { 
        $('.no-news-message').remove();
        $('.news-container').append(data);
        if ((displayed + 20) > undisplayed) {
          $('.load-old-btn').remove();
          $('.news-container').append("<p>No more news to display</p>");
        } else {
          $('.load-old-btn').attr("data-displayed", displayed + 20);
        }            
      }
   })
   return false
});


// deleting the topic and websites
var deleteWebsiteModal = document.getElementById('deleteWebsite')
deleteWebsiteModal.addEventListener('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);
  var id = button.attr("data-pk");
  var next = button.attr("data-trigger-page");
  $.ajax(
    {
        type:"GET",
        url: "/feed/remove-website/" + id,
        data:{
          next: next,
        },
        success: function( data ) 
        { 
          $( '#deleteWebsiteContent' ).html(data);
          console.log('the ajax call was completed')
        }
     });
    return false
});

// editing the topic and websites
var editTopicModal = document.getElementById('editTopic')
editTopicModal.addEventListener('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);
  var id = button.attr("data-pk");
  var next = button.attr("data-trigger-page");
  $.ajax(
    {
        type:"GET",
        url: "/feed/edit-topic/" + id,
        data:{
          next: next,
        },
        success: function( data ) 
        { 
          $( '#editTopicContent' ).html(data);
        }
     });
    return false
});

$(document).on('submit', '#editTopicForm', function(e){
  e.preventDefault();
  var pk = $(this).attr("data-pk")
  $.post('/feed/edit-topic/' + pk, $(this).serialize(), function(data) { 
    $('#editTopic').modal('hide');
    $('.topic' + pk).text(data);
  });
});

var editWebsiteModal = document.getElementById('editWebsite')
editWebsiteModal.addEventListener('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);
  var id = button.attr("data-pk");
  var next = button.attr("data-trigger-page");
  $.ajax(
    {
        type:"GET",
        url: "/feed/edit-website/" + id,
        data:{
          next: next,
        },
        success: function( data ) 
        { 
          $( '#editWebsiteContent' ).html(data);
        }
     });
    return false
});

$(document).on('submit', '#editWebsiteForm', function(e){
  e.preventDefault();
  var pk = $(this).attr("data-pk")
  $.post('/feed/edit-website/' + pk, $(this).serialize(), function(data) { 
    $('#editWebsite').modal('hide');
    $('#website' + pk).text(data);
  });
});

var newspieceTopicModal = document.getElementById('newspieceTopic')
newspieceTopicModal.addEventListener('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);
  var id = button.attr("data-pk");
  $.ajax(
    {
        type:"GET",
        url: "/feed/edit-newspiece/" + id,
        data:{
        },
        success: function( data ) 
        { 
          $( '#newspieceTopicContent' ).html(data);
        }
     });
    return false
});

$(document).on('submit', '#newspieceTopicForm', function(e){
  e.preventDefault();
  var pk = $(this).attr("data-pk")
  $.post('/feed/edit-newspiece/' + pk, $(this).serialize(), function(data){ 
    // $( '#newspieceTopicContent' ).html("<p>The topic has been updated </p>");
    $('#piece' + pk).replaceWith(data[0].updated_content);
    updateUnread(data);
    $('#newspieceTopic').modal('hide')

     // of course you can do something more fancy with your respone
  });
});