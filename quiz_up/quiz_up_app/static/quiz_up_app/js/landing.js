document.addEventListener('DOMContentLoaded', function () {
    function openPopup(url) {
        fetch(url)
        .then(response => response.text())
        .then(data => {
            var popupContainer = document.getElementById('popup-container');
            popupContainer.innerHTML = data;
            popupContainer.style.display = 'flex';
            popupContainer.classList.add('overlay');  // Add the overlay class

            if(url == '/signup/'){
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
            };}
                
        })
        .catch(error => console.error('Error fetching content:', error));
    }



    document.getElementById('start-button').addEventListener('click', function () {
        openPopup('/signin/');
    });


    window.addEventListener('popstate', function (event) {
        closePopup();
    });

});

function closeSignIn() {
    document.querySelector('.wrap').style.display = 'none';
    removeOverlay();
}

document.addEventListener('DOMContentLoaded', function () {
    var closeButton = document.querySelector('.closebutton');
    if (closeButton) {
        closeButton.addEventListener('click', closeSignIn);
    }
});

function closeSignUp() {
    document.querySelector('.popup').style.display = 'none';
    removeOverlay();
}

document.addEventListener('DOMContentLoaded', function () {
    var closeButton = document.querySelector('.close-btn');
    if (closeButton) {
        closeButton.addEventListener('click', closeSignUp);
    }
});

function removeOverlay() {
    var popupContainer = document.getElementById('popup-container');
    popupContainer.innerHTML = '';  // Clear the content when closing
    popupContainer.style.display = 'none';
    popupContainer.classList.remove('overlay');  // Remove the overlay class
}