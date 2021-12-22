// Array to store generated months beginning from the starting month of a class
let generatedmonths = [];

// Store paid months with respect to student name and class
let paidMonthIds = [];

// Store all the checkbox ids
let chkboxIds = [];

// Starting months of the month-lists in the table
let monthListGen = [];

// Index for next months; Button pressed -> it increments by 1
let indexNex = 0;

let  nextIsPressed = false;
let  prevIsPressed = false;

let startingMonth;
let startingYear;
let nextYear;

let state = 'false';

// Toggle the update button function if the change payment button is pressed beforehand
let changePaidtoggle = 0;

// For GET request
$(document).ready(function() {

  state = sessionStorage.getItem('clicked');
  console.log(state);
  if (state === null)
  {
    state = 'false';
  }

  if (state == 'true')
  {

    monthListGen = JSON.parse(sessionStorage.getItem('monthListGen'));
    indexNex = Number(sessionStorage.getItem('indexNex'));
    startingYear = Number(sessionStorage.getItem('startingYear'));
    nextYear = Number(sessionStorage.getItem('nextYear'));
    startingMonth = monthListGen[indexNex];
  }
  main();
});

function studentpay(){
  if (state === 'true')
  {
    state = 'false';
  }
  monthListGen = [];
  indexNex = 0;
  main();
}


function getstudents(month, year, payment, selectedclass){
  var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var paymentlist = payment;
  var nexPrevbuttons = "";
  var chkbox_yr;

  paidMonthIds = [];
  chkboxIds = [];
  console.log(state);

  if (nextIsPressed == true) {
    startingMonth = monthListGen[indexNex];
    startingYear = nextYear;
    nextYear = nextYear + 1;
  }
  else if (prevIsPressed == true) {
    startingMonth = monthListGen[indexNex];
    startingYear--;
    nextYear--;
  }
  else {
      if (state == 'false')
      {
        startingMonth = parseInt(month);
        startingYear = parseInt(year);
        monthListGen.push(startingMonth);
        nextYear = startingYear + 1;
      }
  }
  sessionStorage.setItem('clicked', 'false');


  var fstcolspan = (12 - startingMonth) + 1; // Add one to offset the zeroth index
  var scndcolspan = (12 - fstcolspan);
  content = "<table class='table table-striped table-bordered'><thead class='text-center'><tr> <th rowspan='2'>#</th> <th rowspan='2'>Name</th> <th rowspan='2'>Nickname</th>";
  content += "<th colspan=" + fstcolspan.toString() + ">"+ startingYear +"</th>";
  if (scndcolspan == 0)
  {
    content += "</tr>";
  }
  else
  {
    content += "<th colspan="+ scndcolspan.toString() + ">"+ nextYear +"</th> </tr>";
  }
  content += "<tr>";

  //Print Months
  content += generateMonths(startingMonth, months);

  content += "</tr></thead>";
  content += "<div><tbody>";
  let parameters = {
    program : selectedclass
  };
  $.getJSON("/getstudents", parameters, function(data, textStatus, jqXHR) {

    for (var i = 0; i < data.length; i++)
    {
      var counter = 0;
      var stdHasPaid = false;
      content += "<tr class='text-center'>";
      content += "<td>" + (i + 1) + "</td>" + "<td>" + data[i].name + "</td>" + "<td>" + data[i].nickname + "</td>";

      for (var k = 0; k < payment.length; k++)
      {
        var name = payment[k].name + payment[k].nickname;
        if (name == data[i].name + data[i].nickname)
        {
          stdHasPaid = true;
        }
          //Get the checkbox ids of the paid months from the students who have paid
          if (stdHasPaid)
          {
            for (var key in payment[k]){
              if (payment[k][key] === "PAID")
                {
                  var index = cnvtToMonthIndex(key);
                  if ((payment[k].Paidyear == startingYear && index < fstcolspan) || (payment[k].Paidyear == nextYear && index >= fstcolspan))
                  {
                    paidMonthIds.push("chkbox" + i + index + payment[k].Paidyear);
                  }
                }
            }
            stdHasPaid = false;
          }
      }

      for(var j = 0; j < months.length; j++)
      {
        if (scndcolspan != 0) {
          if (j < fstcolspan) {
              chkbox_yr = startingYear;
          }
          else {
              chkbox_yr = nextYear;
          }
        }
        else {
          chkbox_yr = startingYear;
        }
        var chkbox_ids = 'chkbox' + i + j + chkbox_yr;
        content += '<td><input type="checkbox" name="student" id="' + chkbox_ids + '" value="' + data[i].name + "+" + data[i].nickname + "," + generatedmonths[j];
        chkboxIds.push(chkbox_ids);
        content += "+" + chkbox_yr + '"></td>';
      }
      content +="</tr>";
    }

    content += "</tbody></div></table>";

    //Add buttons if there is data in the table
    if (data.length != 0)
    {
      // Next and Prev buttons
      nexPrevbuttons = "<div class='text-right'><div class='btn-group'>";
      var prev = "<button class='btn btn-info' id='prev' type='button' onclick='prevbutton()'><</button>";
      var next = "<button class='btn btn-info' id='next' type='button' onclick='nextbutton()'>></button></div></div>";
      nexPrevbuttons += prev + next;

      // Update and changePaid buttons
      content += "<div class='text-right'><div class='btn-group'>"
      if (paidMonthIds.length != 0)
      {
        content += "<button class='btn btn-info' type='button' onclick='changePaid()'>Change Paid</button>"
      }
      content += "<button class='btn btn-primary' type='submit'>Update Payment</button></div></div>";
    }

    document.getElementById("display").innerHTML = content;
    document.getElementById("nexPrev").innerHTML = nexPrevbuttons;

    for(var i = 0; i < paidMonthIds.length; i++)
    {
      document.getElementById(paidMonthIds[i]).checked = true;
      document.getElementById(paidMonthIds[i]).disabled = true;
    }

    if (data.length != 0)
    {
      if (indexNex != 0)
      {
        if (indexNex < 6) {
            document.getElementById('prev').disabled = false;
            document.getElementById('next').disabled = false;
          }
          else {
            document.getElementById('next').disabled = true;
          }
      }
      else {
        document.getElementById('prev').disabled = true;
      }
    }
  });

  $(document).ajaxComplete(function(){
      $("#wait").css("display", "none");
  });
    // Resets the next/prev buttons
    nextIsPressed = false;
    prevIsPressed = false;
}

function getpaymentlist(selectedclass, month, year){
    let parameters = {
      program :selectedclass
    };
    $.getJSON("/getpayment", parameters, function(data, textStatus, jqXHR){
              var payment = data;
              getstudents(month, year, payment, selectedclass);
    });
}


function main()
{
    changePaidtoggle = 0;
    var selectedclass = document.getElementById("program").value;
    if (selectedclass == "Select a class")
    {
          return false;
    }
    else {
        $(document).ajaxStart(function(){
            $("#wait").css("display", "block");
        });

      let parameters = {
        program : selectedclass
      };
      $.getJSON("/getclasses", parameters, function(data, textStatus, jqXHR) {
                var date = data[0].classDate;
                var month = date.slice(3, 5);
                var year = date.slice(-4);
                getpaymentlist(selectedclass, month, year);
      });
    }
}

function changePaid(){
  changePaidtoggle = 1;
  for(var i = 0; i < chkboxIds.length; i++)
  {
    document.getElementById(chkboxIds[i]).disabled = true;
  }
  for(var i = 0; i < paidMonthIds.length; i++)
  {
    document.getElementById(paidMonthIds[i]).disabled = false;
  }
}

function paymentsubmit(){
  // Get values for the unchecked checkboxes
    var uncheckedvalues = "";
    monthListGen.pop();
    sessionStorage.setItem('monthListGen', JSON.stringify(monthListGen));
    sessionStorage.setItem('indexNex', indexNex);
    sessionStorage.setItem('startingYear', startingYear);
    sessionStorage.setItem('nextYear', nextYear);
    sessionStorage.setItem('clicked', 'true');

    if (changePaidtoggle == 1)
    {
        for(var i = 0; i < paidMonthIds.length; i++)
        {
          if (document.getElementById(paidMonthIds[i]).checked == false)
          {
              uncheckedvalues += '<input name="unchecks" type="hidden" value="' + document.getElementById(paidMonthIds[i]).value + '">';
          }
        }
        document.getElementById("display").innerHTML += uncheckedvalues;

        return true;
    }
    else {
        return true;
    }
    changePaidtoggle = 0;
}

function generateMonths(startingMonth, months)
{
    generatedmonths = [];
    var members = 0;
    var head_cols = ""; // An empty string to store the months
    var i = startingMonth;
    // Only 12 months must exist per generation
    while (members < 12) {
        head_cols += "<th>" + months[i - 1] + "</th>";
        generatedmonths.push(months[i - 1]);
        members++;

        // Restrict the months within the 12 months; 13th month equals January
        i = (i + 1) % 13;
        if (i == 0)
          i = 1;
    }
    // Get the first months of the next generated months
    monthListGen.push(i);
    return head_cols;
}

function cnvtToMonthIndex(month)
{
  for (var i = 0; i < generatedmonths.length; i++){
    if (month == generatedmonths[i]){
      return i;
    }
  }
}

function nextbutton()
{
  if (indexNex < 9)
  {
    nextIsPressed = true;
    indexNex++;
  }
  main();
}

function prevbutton()
{
  if (indexNex > 0)
  {
    prevIsPressed = true;
    indexNex--;
  }
  main();
}