function checkPass()
{
    var pass1 = document.getElementById('password');
    var pass2 = document.getElementById('password-confirm');

    var message = document.getElementById('confirmMessage');

    var goodColor = "#66cc66";
    var badColor = "#ff6666";

    if(pass1.value == pass2.value){
        pass2.style.backgroundColor = goodColor;
        message.style.color = goodColor;
        message.innerHTML = "Passwords Match!";
    }else{
        pass2.style.backgroundColor = badColor;
        message.style.color = badColor;
        message.innerHTML = "Passwords Do Not Match!";
    }
}

function validateEmail(inputText)
{
    var goodColor = "#66cc66";
    var badColor = "#ff6666";

    var status = document.getElementById('status');
    var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;

    if(inputText.value.match(mailformat))
    {
        inputText.style.backgroundColor = goodColor;
        status.style.color = goodColor;
        status.innerHTML = "You have entered an valid email address!";
        return true;
    }
    else
    {
        inputText.style.backgroundColor = badColor;
        status.style.color = badColor;
        status.innerHTML = "You have entered an invalid email address!";
        return false;
    }
}

function phoneNumber(inputText)
{
    var goodColor = "#66cc66";
    var badColor = "#ff6666";

    var status = document.getElementById('phone-status');
    var phoneno =  /^\+?([0-9]{3})\)?[-. ]?([0-9]{4})[-. ]?([0-9]{4})$/;

    if(inputText.value.match(phoneno))
    {
        inputText.style.backgroundColor = goodColor;
        status.style.color = goodColor;
        status.innerHTML = "A Valid Phone Number!";
        return true;
    }
    else
    {
        inputText.style.backgroundColor = badColor;
        status.style.color = badColor;
        status.innerHTML = "Not a valid Phone Number!";
        return false;
    }
}