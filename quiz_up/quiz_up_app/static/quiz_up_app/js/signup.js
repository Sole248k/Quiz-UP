let password = document.getElementById ("password");
let confirmpassword = document.getElementById ("confirmpassword");
let showpassword = document.getElementById ("showpassword");

showpassword.onclick = function (){
    if(password.type == "password") {
        password.type = "text";
        confirmpassword.type = "text"
    }else{
        password.type = "password";
        confirmpassword.type = "password"
    }

    password.classList.toggle("show-password");
    confirmpassword.classList.toggle("show-password");
};