let form = document.getElementById("login")
form.onsubmit = function() {

  if (form.username.value == "")
  {
    alert("Please provide username");
    return false;

  }
  if (form.password.value == "")
  {
    alert("Please provide password");
    return false;
  }
  else {
    return true;
  }
};
