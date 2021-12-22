$(document).ready(function() {
    getstudents();
});

function getstudents(){
  selectedclass = document.getElementById("program").value;
  content = "<table class='table'><thead class='text-center'><tr> <th>#</th> <th>Name</th> <th>Nickname</th> <th>Registerd Date</th> <th>Select student(s) to remove</th></tr></thead>";
  content += "<tbody class='text-center'>";
  let parameters = {
    program : selectedclass
  };
  $.getJSON("/getstudents", parameters, function(data, textStatus, jqXHR) {

    for(var i = 0; i < data.length; i++)
    {
      var date = convertUTCDateToLocalDate(new Date(data[i].registered_date));
      content += "<tr>";
      content += "<td>" + (i + 1) + "</td>" + "<td>" + data[i].name + "</td>" + "<td>" + data[i].nickname + "</td>" + "<td>" + date.toString() + "</td>";
      content += "<td><div class='text-center'><input type='checkbox' name='student' value=" + data[i].name + "+" + data[i].nickname + "></div></td>";
      content +="</tr>";
    }
    if (data.length != 0)
    {
      content += "<tr> <td></td> <td></td> <td></td> <td></td> <td><div class='text-center'><button class='btn btn-danger' type='submit'>Remove</button></div></td> </tr>";
    }
    content += "</tbody></table>";

    document.getElementById("display").innerHTML = content;
  });
  //https://stackoverflow.com/questions/6525538/convert-utc-date-time-to-local-date-time
  function convertUTCDateToLocalDate(date) {
    var newDate = new Date(date.getTime()+date.getTimezoneOffset()*60*1000);

    var offset = date.getTimezoneOffset() / 60;
    var hours = date.getHours();

    newDate.setHours(hours - offset);

    return newDate;
  }
}
