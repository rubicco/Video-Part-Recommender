$(document).ready(function(){
  getVideoPartsFromPartId(localStorage["part_id"]);
  get_apriori_lists(localStorage.user_id,localStorage.part_id);
});

function getVideoPartsFromPartId(p_id){
  var json_dat = {'part_id':p_id};
  $.ajax({
      url: '/getVideoParts',
      data: json_dat,
      type: 'post',
      success: function(response) {
          res = JSON.parse(response)
          append_parts_to_id('#tab-left', res.parts);
          // console.log(res);
      },
      error: function(error) {
          console.log(error);
      }
  });
}

function append_parts_to_id(div_id, parts){
  $(div_id).html('');
  for(var i=0; i<parts.length; i++){
    var part_id = parts[i].part_id;
    var thumbnail_url = parts[i].thumbnail_url;
    var title = parts[i].title;
    var start_time = parts[i].start_time;
    var end_time = parts[i].end_time;
    var category = parts[i].category;
    var url = parts[i].url;
    var a = $('<a>').attr("class","vid-obj").attr("part_id",part_id).attr("part_url",url);
    var thumb = $('<span>').attr("class","thumb").append($("<img>").attr("src",thumbnail_url));
    var desc = $('<span>').attr("class","desc").append($("<span>").attr("class","title").text(title))
    var clear = $('<div>').attr("class","clear");
    var times = $('<div>').attr('class','times');
    var s_time = $('<span>').attr('class','time').text(start_time.split(',')[0]);
    var e_time = $('<span>').attr('class','time').text(end_time.split(',')[0]);
    times.append(s_time).append($('<span>').text(' - ')).append(e_time);
    var category = $('<span>').attr('class','category').text(category);
    a.append(thumb).append(desc).append(clear).append(times).append(category).append(clear);
    $(div_id).append(a);
  }
  $(div_id+" a").click(function(){
    localStorage["part_id"] = $(this).attr('part_id');
    localStorage["part_url"] = $(this).attr('part_url');
    var times = $($(this).children()[2]).text().split(' - ');
    localStorage["part_start"] = times[0];
    localStorage["part_end"] = times[1];
    window.location = "/video"
  })
}

function get_apriori_lists(user_name, part_id){
  var json_dat = {'user_name': user_name, 'part_id':part_id}
  $.ajax({
      url: '/getAprioriLists',
      data: json_dat,
      type: 'post',
      success: function(response) {
          res = JSON.parse(response)
          append_parts_to_id_from_partids('#tab1', res.general_apriori);
          append_parts_to_id_from_partids('#tab2', res.category_apriori);
      },
      error: function(error) {
          console.log(error);
      }
  });
}

function append_parts_to_id_from_partids(div_id, part_ids){
  json_dat = {'parts':part_ids}
  $.ajax({
      url: '/getDataFromPartIds',
      data: json_dat,
      type: 'post',
      success: function(response) {
          res = JSON.parse(response);
          append_parts_to_id(div_id, res.parts_data);
          // console.log(res);
      },
      error: function(error) {
          console.log(error);
      }
  });
}

$('#continue-part').click(function(){
  change_video(curr_video_id,curr_end_time,player.getDuration());
  continue_flag=true;
});

$('#prev-part').click(function(){
  var a = get_pre_part();
  a.click();
});

$('#next-part').click(function(){
  var a = get_next_part();
  a.click();
});

// Tab Selection
$(".tab-area li").click(function(){
  if($(this).attr("class")!="selected"){
    var all_li = $(".tab-area li");
    for(var i = 0; i<all_li.length; i++){
      $(all_li[i]).attr("class","");
    }
    $(this).attr("class","selected");

    var all_tab_ids = [];
    var tabs = $(".tab-area li").children();
    var clicked_tab_id = $(this).children().attr("href").replace("#","");
    for(var i = 0; i<tabs.length; i++){
      all_tab_ids.push(tabs.eq(i).attr("href"))
    }
    all_tab_ids.forEach(function(e){
      if($(e).attr("id")==clicked_tab_id){
        $(e).attr("style","display:block");
      }
      else{
        $(e).attr("style","display:none");
      }
    });
  }
});

function get_pre_part(){
  var parts = $('#tab-left a');
  for(var i=0; i<parts.length; i++){
    if ($(parts[i]).attr('part_id') == String(parseInt(localStorage.part_id)-1)){
      return $(parts[i]);
    }
  }
}

function get_next_part(){
  var parts = $('#tab-left a');
  for(var i=0; i<parts.length; i++){
    if ($(parts[i]).attr('part_id') == String(parseInt(localStorage.part_id)+1)){
      return $(parts[i]);
    }
  }
}

// Video Selection
// video yuklenecek sonrasinda video degistiren
// fonksiyonun sonunda sayfa uzerindeki tum
// o partlari secen bir fonksiyon calisacak.
// YUKLENEN VIDEOYA GORE TUM SAYFA GUNCELLENMELIDIR!
// Hem soldaki tab
// Hem de sagdaki tabler.
