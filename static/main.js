
$(document).ready(function(){
var count = 0
setInterval(function(){
    $.ajax({
        type: 'GET',
        url : "/refresh_div/",
        success: function(response){
        count++
        console.log(count, "------------------- Refreshed")
            $("#customers1").empty();
            $("#customers2").empty();
            var header1="<tr><th>File ID</th><th>File Name</th><th>Threshold</th><th>Start Date</th><th>Status</th></tr>"
            var header2="<tr><th>File ID</th><th>File Name</th><th>Threshold</th><th>Start Date</th><th>End Date</th><th>Status</th></tr>"
            $("#customers1").append(header1);
            $("#customers2").append(header2);

            for (var key in response.user_files)
            {
                if (response.user_files[key].Status == "Error") {

                    if (response.user_files[key].retry_value < 4) {
                     var temp="<tr><td>"+response.user_files[key].id+"</td>"+
                    "<td>"+response.user_files[key].file_name+"</td>"+
                    "<td>"+response.user_files[key].threshold_value+"</td>"+
                    "<td>"+response.user_files[key].created_at+"</td>"+
                    "<td>"+response.user_files[key].Status+
                    "<a href='/retry/"+response.user_files[key].id+"/'><i style='color: #0083f9; font-size:24px; right: 130px; position: absolute;' class='fa fa-repeat'></i></a>"+
                    "<i onclick='geekAlert"+response.user_files[key].id+"()' style='color: #0083f9; font-size:24px; right: 97px; position: absolute;' class='fa fa-eye'></i>"+
                    "<span style='right: 67px; position: absolute;'><a href='/delete/"+response.user_files[key].id+"/' style='font-size:24px; color: red;' class='fa'>&#xf014;</a></span></td></tr>";
                    }
                    else {
                     var temp="<tr><td>"+response.user_files[key].id+"</td>"+
                    "<td>"+response.user_files[key].file_name+"</td>"+
                    "<td>"+response.user_files[key].threshold_value+"</td>"+
                    "<td>"+response.user_files[key].created_at+"</td>"+
                    "<td>"+response.user_files[key].Status+
                    "<i onclick='geekAlert"+response.user_files[key].id+"()' style='color: #0083f9; font-size:24px; right: 97px; position: absolute;' class='fa fa-eye'></i>"+
                    "<span style='right: 67px; position: absolute;'><a href='/delete/"+response.user_files[key].id+"/' style='font-size:24px; color: red;' class='fa'>&#xf014;</a></span></td></tr>";
                    }
                }
                else {
                    var temp="<tr><td>"+response.user_files[key].id+"</td>"+
                    "<td>"+response.user_files[key].file_name+"</td>"+
                    "<td>"+response.user_files[key].threshold_value+"</td>"+
                    "<td>"+response.user_files[key].created_at+"</td>"+
                    "<td>"+response.user_files[key].Status+"</td></tr>";
                    //var temp="<div class='container darker'><b>"+response.messages[key].user_id_id+"</b><p>"+response.messages[key].body+"</p><span class='time-left'>"+response.messages[key].created_at+"</span></div>";
                    }
                $("#customers1").append(temp);
            }
            for (var key in response.user_files_complete)
            {
                var temp="<tr><td>"+response.user_files_complete[key].id+"</td>"+
                "<td>"+response.user_files_complete[key].file_name+"</td>"+
                "<td>"+response.user_files_complete[key].threshold_value+"</td>"+
                "<td>"+response.user_files_complete[key].created_at+"</td>"+
                "<td>"+response.user_files_complete[key].finished_at+"</td>"+
                "<td>"+response.user_files_complete[key].Status+
                "<span style='right: 67px; position: absolute;'><a href='/media/"+response.user_files_complete[key].file_name+"' style='font-size:24px;' class='fa'>&#xf019;</a></span></td></tr>";
                //var temp="<div class='container darker'><b>"+response.messages[key].user_id_id+"</b><p>"+response.messages[key].body+"</p><span class='time-left'>"+response.messages[key].created_at+"</span></div>";
                $("#customers2").append(temp);
            }
        },
        error: function(response){
        console.log("An error occured-----------------------")
            //alert('An error occured')
        }
    });
},10000);
})
