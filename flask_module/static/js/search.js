var search_box_text = "";
var search_list = {};
var part_id = -1;


$("#searchButton").click(function(){
  search_box_text = $("#search").val();
  var d = {'search':search_box_text};
  var address = '/searchingText/' + search_box_text
  console.log(address);
  $.ajax({
      type: 'post',
      url: '/searchingText',
      data: $('form').serialize(),
      success: function(response) {
          search_list = JSON.parse(response)
          console.log(search_list);
          get_parts_from_ids(search_list.parts);
      },
      error: function(error) {
          console.log(error);
      }
  });
})

function get_parts_from_ids(part_ids){
  var json_dat = {'parts':part_ids};
  $.ajax({
      url: '/getDataFromPartIds',
      data: json_dat,
      type: 'post',
      success: function(response) {
          res = JSON.parse(response)
          append_parts(res.parts_data);
      },
      error: function(error) {
          console.log(error);
      }
  });
}

function append_parts(parts){
  $('#listing-contents').html('');
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
    $('#listing-contents').append(a);
  }
  $('#listing-contents a').click(function(){
    localStorage["part_id"] = $(this).attr('part_id');
    localStorage["part_url"] = $(this).attr('part_url');
    var times = $($(this).children()[2]).text().split(' - ');
    localStorage["part_start"] = times[0];
    localStorage["part_end"] = times[1];
    window.location = "/video"
  })
}
