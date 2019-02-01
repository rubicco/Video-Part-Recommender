console.log("JS IMPORTED");
$("#signIn-button").click(function(){
  var d = {'user_name':$('#user_name').val(),'password':$('#password').val()}
  $.ajax({
      type: 'post',
      url: '/signInUser',
      data: d,
      success: function(response) {
          var a = JSON.parse(response)
          if(a.status=="OK"){
            localStorage['user_name']=d.user_name;
            localStorage['user_id']=a['user_id'];
            window.location = "/search"
          }
          else{
            alert("Username or Password Wrong.");
          }
      },
      error: function(error) {
          console.log(error);
      }
  });
});
