
document.addEventListener('DOMContentLoaded', function () {
    var signupButton = document.getElementById('signup-button');
    var signinButton = document.getElementById('signin-button');
    var registerTab = document.getElementById('register-tab');
    var signinTab = document.getElementById('signin-tab');

    signupButton.addEventListener('click', function () {
        // Activate the "Register" tab
        registerTab.click();
    });

    signinButton.addEventListener('click', function () {
        // Activate the "Sign In" tab
        signinTab.click();
    });
});

$(document).ready(function() {
  $('.carousel').on('slid.bs.carousel', function() {
    const activeSlide = $(this).find('.carousel-item.active');
    const videoElement = activeSlide.find('video');

    if (videoElement.length) {
      videoElement.get(0).muted = true; // Mute the video first
      videoElement.get(0).play(); // Play the video
    }
  });
});

