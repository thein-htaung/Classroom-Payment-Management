//Adding dynamic form fields
//https://stackoverflow.com/questions/14853779/
function addFields(){
   var number = document.getElementById("studentNumber").value;

   if ((number < 0) || (number > 10))
   {
      alert("The number entered is not valid");
   }
   else
   {
     var container1 = document.getElementById("container_name");
     var container2 = document.getElementById("container_nickname");
     while (container1.hasChildNodes()) {
         container1.removeChild(container1.lastChild);
     }
     while (container2.hasChildNodes()) {
         container2.removeChild(container2.lastChild);
     }
     for (i = 0; i < number; i++){
         var input1 = document.createElement("input");
         input1.type = "text";
         input1.placeholder = "Name";
         input1.name = "studentName" + i;
         input1.className = "form-control";
         input1.required = true;
         container1.appendChild(input1);
         container1.appendChild(document.createElement("br"));
         container1.appendChild(document.createElement("br"));

         var input2 = document.createElement("input");
         input2.type = "text";
         input2.placeholder = "Nickname";
         input2.name = "nickname" + i;
         input2.className = "form-control";
         container2.appendChild(input2);
         container2.appendChild(document.createElement("br"));
         container2.appendChild(document.createElement("br"));
     }
  }
}
