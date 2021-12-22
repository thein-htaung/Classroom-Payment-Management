var form = document.getElementById("profileUpdate");
form.onsubmit = function() {
  var format = /[~ !@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/;
  if ((form.username.value == "" && form.password.value == ""))
  {
    alert("Must enter new username and/or password");
    return false;
  }
  else if (form.password.value != "")
  {
      if (form.password.value.length < 6)
      {
        alert("New password must have at least 6 characters");
        return false;
      }
      if (form.confirmation.value == "")
      {
        alert("Missing confirmation password");
        return false;
      }

      else if (form.password.value != form.confirmation.value)
      {
        alert("Confirmed password does not match the new password");
        return false;
      }
  }
  else if (format.test(form.username.value))
  {
    alert("Username containers unallowed special characters");
    return false;
  }
  else
  {
    return true;
  }
};
