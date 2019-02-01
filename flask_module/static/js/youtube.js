// 2. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');
var player;

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
// change_video(localStorage['part_url'],convertSecond(localStorage['part_start']) ,convertSecond(localStorage['part_end']))
// change_video(curr_video_id, curr_start_time, curr_end_time);
var part_id = localStorage['part_id'];
var curr_video_id = localStorage['part_url'];
var curr_start_time = convertSecond(localStorage['part_start']);
var curr_end_time = convertSecond(localStorage['part_end']);
var continue_flag = false;



function add_player_div(){
  $('.video-area').prepend($('<div>').attr("id","player"));
}

function remove_player(){
  $('iframe#player').remove();
}

function return_playerConfig(video_id, startTime, endTime){
  var playerConfig = {
    height: '500px',
    width: '90%',
    videoId: video_id,
    host: "https://www.youtube.com",
    playerVars: {
      start:startTime,
      end:endTime,
      loop:1,
      rel:0,
      enablejsapi:1,
      origin:"http://46.101.135.64:5000"
    },
    events: {
      'onReady': onPlayerReady,
      'onStateChange': onPlayerStateChange
    }
  }
  return playerConfig
}

function create_player(videoId,startTime,endTime){
  player = new YT.Player('player', return_playerConfig(videoId,startTime,endTime));
  add_player_div();
}

function onYouTubeIframeAPIReady() {
  create_player(curr_video_id,curr_start_time,curr_end_time);
  change_video(curr_video_id,curr_start_time,curr_end_time);
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
  if(continue_flag){
    continue_flag = false;
    event.target.playVideo();
  }

}

// 5. The API calls this function when the player's state changes.
function onPlayerStateChange(event) {
  if (event.data == YT.PlayerState.ENDED){
    remove_player();
    create_player(curr_video_id,curr_start_time,curr_end_time);
    // $('#continue-part').slideDown(800).css("visibility","visible");
    $('#continue-part').attr("disabled", false);
    $('#prev-part').attr("disabled", false);
    $('#next-part').attr("disabled", false);
  }
}

function change_video(new_video_id, startTime, endTime){
  // $('#continue-part').slideUp(800).css("visibility","hidden");
  $('#continue-part').attr("disabled", false);
  $('#prev-part').attr("disabled", false);
  $('#next-part').attr("disabled", false);
  curr_video_id = new_video_id;
  curr_start_time = startTime;
  curr_end_time = endTime;
  remove_player();
  create_player(new_video_id,startTime,endTime);
}

function play_video(){
  player.playVideo();
}

function convertSecond(time){
  t = time.split(':');
  return String(parseInt(t[0])*3600 + parseInt(t[1])*60 + parseInt(t[2]))
}
