/*
*
*       Requirements: - form must have ID "captcha-form"
*                     - form button must have ID "captcha-button"
*
*/
var oldOverlay = '<div class="overlay"><div class="valign card blue-grey darken-2 hoverable">' +
   '<div class="card-image" style="display: flex; justify-content: space-around; padding: 20px 3%;">' +
         '<img id="first" style="width: 40%; border: 8px solid rgba(0, 0, 0, 0.1);" src="">' +
         '<img id="second" style="width: 40%; border: 8px solid rgba(0, 0, 0, 0.1);" src="">' +
         '<span class="card-title"></span>' +
       '</div>' +
       '<div class="card-content row" style="padding: 0 15px">' +
           '<div class="input-field col s12">' +
       '<i class="material-icons prefix">keyboard</i>' +
       '<input id="icon_prefix" type="text" class="validate input">' +
       '<label for="icon_prefix">Solution</label>' +
     '</div>' +
       '</div>' +
       '<div class="card-action right-align">' +
         '<a id="submit" href="">Submit</a>' +
         '<a id="reload" href=""><i class="material-icons" style="font-size: 1.2rem">refresh</i></a>' +
       '</div>' +
'</div></div>';
var captchaURL = captchaURL || 'http://localhost:8000/captcha/request';
var captchaReq = new XMLHttpRequest();
var response = "";
captchaReq.open('GET', captchaURL, true);
captchaReq.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
captchaReq.responseType = 'json';
captchaReq.onload = function (e) {
    if(captchaReq.status === 200) {
        var xhr = e.target;
        if (xhr.responseType === 'json') {
            response = xhr.response.message;
        } else {
            response = JSON.parse(xhr.responseText).message; // IE bug fix
        }
    } else {
      throw new Error('An error occurred during your request: ' +  captchaReq.status + ' ' + captchaReq.statusText);
    }
};
captchaReq.send();
console.log(response);
/*
$('#reload').on('click', function(e) {
    e.preventDefault();
    var session_key = $('.card').attr('key');
    console.log(session_key);
    $.ajax('http://localhost:8000/captcha/renew', {
        data: {session_key: session_key},
        dataType: 'json',
        type: 'POST',
        success: function(data) {
            var host = 'http://localhost:8000/'
            var first_url =  host + data.first_url;
            var second_url =  host + data.second_url;
            $('#first').attr('src', first_url);
            $('#second').attr('src', second_url);
        }
    })
});

$('#submit').on('click', function(e) {
    e.preventDefault();
    var result = $('.input').val();
    var session_key = $('.card').attr('key')
    var data = {result: result, session_key: session_key};
    $.ajax('http://localhost:8000/captcha/validate', {
        data: data,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
            console.log(data)
            if (data.valid) {
                $('.card').attr('id', '');
                $('.card').slideUp();
            }
            else {
                $('.card').effect('shake');
                $('.card').attr('id', 'wrong-input');
            }
        }
    })
});
*/

var captchaSolved = false,
    styledTextCaptchaOverlayHTML = '<div class="overlay">' +
      '<div class="captcha-card">' +
        '<div class="captcha-content">' +
            '<div class="captcha-image-container">' +
                '<div class="first-captcha"><img id="first-text-token"></div>' +
                '<div class="secondcaptcha"><img id="second-text-token"></div></div>' +
            '</div>' +
            '<div class="captcha-input"></div>' +
        '</div>' +
        '<div class="captcha-actions">' +
            '<a href="#" id="submit">Submit</a>' +
            '<a href="#" id="reload"><i class="fa fa-refresh">refresh</i></a>' +
        '</div>' +
      '</div>' +
    '</div>';

// append captcha DOM Node to body
// cross browser trick (https://stackoverflow.com/questions/494143/creating-a-new-dom-element-from-an-html-string-using-built-in-dom-methods-or-pro)
var div = document.createElement('div');
div.innerHTML = styledTextCaptchaOverlayHTML;
var captchaOverlay = div.firstChild;
// Append overlay to body with rendered captcha (display: none)
document.body.appendChild(captchaOverlay);
// retrieve window size and append this size to overlay
var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
captchaOverlay.style.height = h;
captchaOverlay.style.width = w;

// Lookup form and form button element
var form = (!document.querySelectorAll('#captcha-form'))? false : document.querySelectorAll('#captcha-form')[0],
    button = (!document.querySelectorAll('#captcha-button'))? false : document.querySelectorAll('#captcha-button')[0];
if (!button) {
    throw new Error('form button element with id "captcha-button" does not exist');
}
if (!form) {
    throw new Error('form element with id "captcha-form" does not exist');
}

// 3. Add eventlistener on form button to summon overlay
var showCaptchaOverlay = function () {
    var body = document.querySelectorAll('body');

}
button.addEventListener('click', function(e) {
    if(!captchaSolved) {
        e.preventDefault();
        // show captcha overlay
        captchaOverlay.classList.add('show');
        setTimeout(function(){captchaOverlay.classList.add('fadeIn');}, 10);
    }
})


// 4. POST Form on validation and secrect key generated by Web Service
