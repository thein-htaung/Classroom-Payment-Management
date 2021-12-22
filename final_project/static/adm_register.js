let form = document.getElementById("registration");
form.onsubmit = function() {
var format = /[~ !@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/;
    if (form.username.value == "")
    {
        alert("Missing username");
        return false;
    }
    else if (format.test(form.username.value))
    {
        alert("Username contains unallowed characters.");
        return false;
    }
    else if (form.pword.value == "")
    {
        alert("Missing password");
        return false;
    }
    else if (form.pword.value.length < 6)
    {
        alert("Password length must have at least 6 characters");
        return false;
    }
    else if (form.pword.value != form.confirm.value)
    {
        alert("Passwords do not match");
        return false;
    }
    else
    {
        return true;
    }
};
