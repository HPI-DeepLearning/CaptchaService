/*
*
*       Requirements: - form must have class "captcha-form"
*                     - form button must have class "captcha-button"
*
*/


var captchaSolved = false, /* if set to true form gets submitted on form button click - if set to false captcha overlay gets summoned */
    HTMLOverlay = { /* HTML markup for each captcha type supported. You should only adjust the content of the .captcha-content element */
        text: '<div class="overlay">' + /* in order to support more captcha types in future! */
          '<div class="captcha-card">' +
            '<div class="captcha-content">' +
                '<p class="task">Type the following words: </p>' +
                '<div class="captcha-image-container">' +
                    '<div class="first-captcha"><img id="first-text-token"></div>' +
                    '<div class="second-captcha"><img id="second-text-token"></div></div>' +
                '</div>' +
                '<div class="captcha-input"><input type="text" placeholder="Answer..."></input></div>' +
                '<div class="captcha-actions">' +
                    '<a href="#" id="submit"><svg viewBox="0 0 7 7" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:1.41421;"><path id="paper-plane-o" d="M6.615,0.042c0.079,0.056 0.117,0.146 0.102,0.24l-0.96,5.76c-0.012,0.071 -0.056,0.131 -0.12,0.169c-0.034,0.019 -0.075,0.03 -0.116,0.03c-0.03,0 -0.06,-0.008 -0.09,-0.019l-1.977,-0.806l-1.117,1.226c-0.045,0.053 -0.109,0.079 -0.176,0.079c-0.03,0 -0.06,-0.004 -0.086,-0.015c-0.094,-0.038 -0.154,-0.128 -0.154,-0.225l0,-1.695l-1.77,-0.724c-0.086,-0.034 -0.143,-0.113 -0.15,-0.206c-0.008,-0.09 0.041,-0.177 0.12,-0.222l6.24,-3.6c0.078,-0.048 0.18,-0.045 0.255,0.008l-0.001,0Zm-1.282,5.621l0.829,-4.961l-5.378,3.101l1.26,0.514l3.236,-2.396l-1.792,2.989l1.845,0.753Z" style="fill:#bebebe;fill-rule:nonzero;"/></svg></a>' +
                    '<a href="#" id="refresh"><svg viewBox="0 0 6 6" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:1.41421;"><path id="refresh" d="M5.666,3.48c0,0.007 0,0.019 -0.003,0.026c-0.319,1.328 -1.414,2.254 -2.798,2.254c-0.731,0 -1.44,-0.289 -1.972,-0.795l-0.484,0.484c-0.045,0.045 -0.105,0.071 -0.169,0.071c-0.131,0 -0.24,-0.109 -0.24,-0.24l0,-1.68c0,-0.131 0.109,-0.24 0.24,-0.24l1.68,0c0.131,0 0.24,0.109 0.24,0.24c0,0.064 -0.026,0.124 -0.071,0.169l-0.514,0.514c0.352,0.33 0.821,0.517 1.305,0.517c0.667,0 1.286,-0.345 1.635,-0.915c0.09,-0.146 0.135,-0.289 0.199,-0.439c0.018,-0.052 0.056,-0.086 0.112,-0.086l0.72,0c0.068,0 0.12,0.056 0.12,0.12l0,0Zm0.094,-3l0,1.68c0,0.131 -0.108,0.24 -0.24,0.24l-1.68,0c-0.131,0 -0.24,-0.109 -0.24,-0.24c0,-0.064 0.026,-0.124 0.072,-0.169l0.517,-0.517c-0.356,-0.33 -0.825,-0.514 -1.309,-0.514c-0.667,0 -1.286,0.345 -1.635,0.915c-0.09,0.146 -0.135,0.289 -0.199,0.439c-0.018,0.052 -0.056,0.086 -0.112,0.086l-0.746,0c-0.068,0 -0.12,-0.056 -0.12,-0.12l0,-0.026c0.322,-1.331 1.428,-2.254 2.812,-2.254c0.735,0 1.452,0.293 1.984,0.795l0.488,-0.484c0.044,-0.045 0.105,-0.071 0.168,-0.071c0.132,0 0.24,0.109 0.24,0.24l0,0Z" style="fill:#bebebe;fill-rule:nonzero;"/></svg></a>' +
                '</div>' +
            '</div>' +
          '</div>' +
        '</div>',
        image: '<div class="overlay"><div class="captcha-card"><div class="captcha-content"><p class="task"></p>' +
                '<div class="captcha-image-container" id="image-captcha">' +
                    '<input name="captcha" type="checkbox" id="image1" class="input"/><label for="image1" class="label" ><img alt="captcha_image1"></label>' +
                    '<input name="captcha" type="checkbox" id="image2" class="input"/><label for="image2" class="label" ><img alt="captcha_image2"></label>' +
                    '<input name="captcha" type="checkbox" id="image3" class="input"/><label for="image3" class="label" ><img alt="captcha_image3"></label>' +
                    '<input name="captcha" type="checkbox" id="image4" class="input"/><label for="image4" class="label" ><img alt="captcha_image4"></label>' +
                    '<input name="captcha" type="checkbox" id="image5" class="input"/><label for="image5" class="label" ><img alt="captcha_image5"></label>' +
                    '<input name="captcha" type="checkbox" id="image6" class="input"/><label for="image6" class="label" ><img alt="captcha_image6"></label>' +
                    '<input name="captcha" type="checkbox" id="image7" class="input"/><label for="image7" class="label" ><img alt="captcha_image7"></label>' +
                    '<input name="captcha" type="checkbox" id="image8" class="input"/><label for="image8" class="label" ><img alt="captcha_image8"></label>' +
                    '<input name="captcha" type="checkbox" id="image9" class="input"/><label for="image9" class="label" ><img alt="captcha_image9"></label>' +
                '</div></div>' +
                '<div class="captcha-actions">' +
                    '<a href="#" id="submit"><svg viewBox="0 0 7 7" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:1.41421;"><path id="paper-plane-o" d="M6.615,0.042c0.079,0.056 0.117,0.146 0.102,0.24l-0.96,5.76c-0.012,0.071 -0.056,0.131 -0.12,0.169c-0.034,0.019 -0.075,0.03 -0.116,0.03c-0.03,0 -0.06,-0.008 -0.09,-0.019l-1.977,-0.806l-1.117,1.226c-0.045,0.053 -0.109,0.079 -0.176,0.079c-0.03,0 -0.06,-0.004 -0.086,-0.015c-0.094,-0.038 -0.154,-0.128 -0.154,-0.225l0,-1.695l-1.77,-0.724c-0.086,-0.034 -0.143,-0.113 -0.15,-0.206c-0.008,-0.09 0.041,-0.177 0.12,-0.222l6.24,-3.6c0.078,-0.048 0.18,-0.045 0.255,0.008l-0.001,0Zm-1.282,5.621l0.829,-4.961l-5.378,3.101l1.26,0.514l3.236,-2.396l-1.792,2.989l1.845,0.753Z" style="fill:#bebebe;fill-rule:nonzero;"/></svg></a>' +
                    '<a href="#" id="refresh"><svg viewBox="0 0 6 6" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:1.41421;"><path id="refresh" d="M5.666,3.48c0,0.007 0,0.019 -0.003,0.026c-0.319,1.328 -1.414,2.254 -2.798,2.254c-0.731,0 -1.44,-0.289 -1.972,-0.795l-0.484,0.484c-0.045,0.045 -0.105,0.071 -0.169,0.071c-0.131,0 -0.24,-0.109 -0.24,-0.24l0,-1.68c0,-0.131 0.109,-0.24 0.24,-0.24l1.68,0c0.131,0 0.24,0.109 0.24,0.24c0,0.064 -0.026,0.124 -0.071,0.169l-0.514,0.514c0.352,0.33 0.821,0.517 1.305,0.517c0.667,0 1.286,-0.345 1.635,-0.915c0.09,-0.146 0.135,-0.289 0.199,-0.439c0.018,-0.052 0.056,-0.086 0.112,-0.086l0.72,0c0.068,0 0.12,0.056 0.12,0.12l0,0Zm0.094,-3l0,1.68c0,0.131 -0.108,0.24 -0.24,0.24l-1.68,0c-0.131,0 -0.24,-0.109 -0.24,-0.24c0,-0.064 0.026,-0.124 0.072,-0.169l0.517,-0.517c-0.356,-0.33 -0.825,-0.514 -1.309,-0.514c-0.667,0 -1.286,0.345 -1.635,0.915c-0.09,0.146 -0.135,0.289 -0.199,0.439c-0.018,0.052 -0.056,0.086 -0.112,0.086l-0.746,0c-0.068,0 -0.12,-0.056 -0.12,-0.12l0,-0.026c0.322,-1.331 1.428,-2.254 2.812,-2.254c0.735,0 1.452,0.293 1.984,0.795l0.488,-0.484c0.044,-0.045 0.105,-0.071 0.168,-0.071c0.132,0 0.24,0.109 0.24,0.24l0,0Z" style="fill:#bebebe;fill-rule:nonzero;"/></svg></a>' +
                '</div></div></div>'
    },
    insertSessionKey = function(key) { // insert hidden input field containing the captcha session id
        var inputElementString = '<input id="session_key" type="hidden" name="captcha-key" value="' + key + '" />',
            form = document.querySelectorAll('.captcha-form')[0],
            div = document.createElement('div');
        div.innerHTML = inputElementString;
        var input = div.firstChild;
        form.appendChild(input);
    },
    insertTask = function(task) { // insert image captcha task dynamically
        var text = document.querySelectorAll(".captcha-content .task")[0];
        text.innerHTML = 'Select all images below that match ' + task + ':';
    },
    insertCaptchaData = { // depending on the captcha type captcha tokens get embedded
        text: function (response) { // into overlayed captcha html elements
            var firstImage = document.querySelectorAll('.first-captcha > img')[0],
                secondImage = document.querySelectorAll('.second-captcha > img')[0];
            if (!firstImage || !secondImage) {
                throw new Error('missing text captcha markup!');
            }
            if (response.session_key){ // do not do this on reload, since session id does not change on reload
                insertSessionKey(response.session_key);
            }
            firstImage.setAttribute('src', baseURL + response.first_url);
            secondImage.setAttribute('src', baseURL + response.second_url);
            var setMaxImageDimensions = function (imageOne, imageTwo, fi_w, fi_h, si_w, si_h) {
                var container = document.getElementsByClassName('captcha-image-container')[0],
                    availableSpace = container.clientWidth,
                    availableImageWidth = availableSpace - 36, // 8px border on image + 5 px outer paddding
                    maxHeight = window.innerHeight * 0.4;
                var fi_dimension = fi_w / fi_h,
                    si_dimension = si_w / si_h,
                    fi_resultingWidth = fi_dimension * availableImageWidth / (fi_dimension + si_dimension),
                    si_resultingWidth = availableImageWidth - fi_resultingWidth;
                imageOne.style.width = '' + fi_resultingWidth + 'px';
                imageTwo.style.width = '' + si_resultingWidth + 'px';
            }
            secondImage.onload = function() {
                var firstImageWidth  = firstImage.naturalWidth;
                var firstImageHeight = firstImage.naturalHeight;
                var secondImageWidth  = secondImage.naturalWidth;
                var secondImageHeight = secondImage.naturalHeight;
                setMaxImageDimensions(firstImage, secondImage, firstImageWidth,
                                      firstImageHeight, secondImageWidth, secondImageHeight);
            }
        },
        image: function(response) {
            if(!response.url_list){
                throw new Error('Captcha response invalid. Captcha url\'s are missing!');
            }
            // uncheck all previously checked checkboxes
            var checkboxes = document.querySelectorAll('.captcha-image-container > .input');
            checkboxes.forEach(function(el) {
                el.checked = false;
            });
            if (response.session_key){ // do not do this on reload, since session id does not change on reload
                insertSessionKey(response.session_key);
            }
            insertTask(response.task);
            var imgElements = document.querySelectorAll('.input ~ label img')
            for(i = 0; i < 9; i++) {
                var imgElement = imgElements[i];
                if (!imgElement) {
                    throw new Error('Img element is missing in markup!');
                }
                imgElement.setAttribute('src', baseURL + response.url_list[i]);
            }
            // calculate tile size - independent of screen size there should be 3x3 tiles rendered
            var container = document.getElementsByClassName('captcha-image-container')[0],
                availableSpace = container.clientWidth,
                tileWidth = (availableSpace - 20) / 3 - 20; //20 px padding(left and right) and 10px space between tiles

            var labelElements = document.querySelectorAll('.captcha-image-container .input ~ label');
            for(i = 0; i < 9; i++) {
                //size each label element
                labelElements[i].style.width = '' + tileWidth + 'px';
                labelElements[i].style.height = '' + tileWidth + 'px';
            }
        }
    },
    feedbackUserOnWrongInput = function(message) {
        var captchaCard = document.querySelectorAll('.captcha-card')[0];
        captchaCard.classList.add('shake');
        setTimeout(function(){captchaCard.classList.remove('shake')}, 1000);
    },
    reactOnValidationResponse = function(response) {
        if(response.valid) {
            captchaSolved = true;
            document.querySelectorAll('.captcha-button')[0].click();
        } else {
            var captchaCard = document.querySelectorAll('.captcha-card')[0];
            captchaCard.classList.add('shake');
            // load new captcha tokens on wrong input to prevent brute force
            insertCaptchaData[response.type](response);
            setTimeout(function(){captchaCard.classList.remove('shake')}, 1000);
        }
    },
    obtainResult = { // retrieve user input
        text: function() {
            var result = document.querySelectorAll(".captcha-input > input")[0].value;
            if (result) {
                return result;
            } else {
                feedbackUserOnWrongInput('Please provide a solution!');
                return null
            }
        },
        image: function() {
            var checkboxes = document.querySelectorAll(".captcha-image-container input"),
            results = [];
            for(i = 0; i < 9; i++){
                var current_checkbox = checkboxes[i],
                    selected = current_checkbox.checked? 1 : 0;
                results.push(selected);
            }
            return results
        }
    };

/* 1. Open captcha session */
var baseURL = baseURL || 'http://localhost:8000/';
var captchaURL = baseURL + 'captcha/request';
var captchaReq = new XMLHttpRequest();
var response = "";
captchaReq.open('GET', captchaURL, true);
captchaReq.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
captchaReq.responseType = 'json';
captchaReq.onload = function (e) {
    if(captchaReq.status === 200) {
        var xhr = e.target;
        if (xhr.responseType === 'json') {
            response = xhr.response;
        } else {
            response = JSON.parse(xhr.responseText); // IE bug fix
        }
        handleResponse(response);
    } else {
      throw new Error('An error occurred during your request: ' +  captchaReq.status + ' ' + captchaReq.statusText);
    }
};
captchaReq.send();

var handleResponse = function (response) {
    var type = response.type,
        session_key = response.session_key;

    /* 2. Append captcha DOM Node to body */
    // cross browser trick (https://stackoverflow.com/questions/494143/creating-a-new-dom-element-from-an-html-string-using-built-in-dom-methods-or-pro)

    var div = document.createElement('div');
    div.innerHTML = HTMLOverlay[type];
    var captchaOverlay = div.firstChild;
    // Append overlay to body with rendered captcha (display: none)
    document.body.appendChild(captchaOverlay);
    // retrieve window size and append this size to overlay
    var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
    captchaOverlay.style.height = h;
    captchaOverlay.style.width = w;

    insertCaptchaData[type](response);

    /* 3. Lookup form and form button element */

    var form = (!document.querySelectorAll('.captcha-form'))? false : document.querySelectorAll('.captcha-form')[0],
        button = (!document.querySelectorAll('.captcha-button'))? false : document.querySelectorAll('.captcha-button')[0];
    if (!button) {
        throw new Error('form button element with class "captcha-button" does not exist');
    }
    if (!form) {
        throw new Error('form element with class "captcha-form" does not exist');
    }

    /* 4. Add eventlistener on form button to summon overlay */
    button.addEventListener('click', function(e) {
        if(!captchaSolved) { // when captcha is not solved yet summon captcha overlay
            e.preventDefault();
            // show captcha overlay
            captchaOverlay.classList.add('show');
            setTimeout(function(){captchaOverlay.classList.add('fadeIn');}, 10);
        }
    })

    /* 5. Add eventlistener refresh button */
    var refresh = document.getElementById('refresh');
    refresh.addEventListener('click', function(e){
        var sessionKey = document.querySelectorAll('#session_key')[0].getAttribute('value'),
            renewURL = baseURL + 'captcha/renew',
            captchaReq = new XMLHttpRequest(),
            response = "";
        captchaReq.open('POST', renewURL, true);
        captchaReq.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        captchaReq.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        captchaReq.responseType = 'json';
        captchaReq.onload = function (e) {
            if(captchaReq.status === 200) {
                var xhr = e.target;
                if (xhr.responseType === 'json') {
                    response = xhr.response;
                } else {
                    response = JSON.parse(xhr.responseText); // IE bug fix
                }
                insertCaptchaData[type](response);
            } else {
              throw new Error('An error occurred during your request: ' +  captchaReq.status + ' ' + captchaReq.statusText);
            }
        };
        captchaReq.send('session_key=' + sessionKey); // refresh session
    });

    /* 6. Click on overlay should hide captcha card */
    var captchaOverlay = document.getElementsByClassName('overlay')[0];
    captchaOverlay.addEventListener('click', function(e){
        captchaOverlay.classList.remove('fadeIn');
        captchaOverlay.classList.remove('show');
    });
    var captchaCard = document.getElementsByClassName('captcha-card')[0];
    captchaCard.addEventListener('click', function(e){
        e.stopPropagation(); // don't click overlay when clicking on captcha card
    });

    /* 7. POST Form on validation and session key generated by Web Service */
    var submit = document.getElementById('submit');
    submit.addEventListener('click', function(e){
        var sessionKey = document.querySelectorAll('#session_key')[0].getAttribute('value'),
            result = obtainResult[type](),
            submitURL = baseURL + 'captcha/validate',
            captchaReq = new XMLHttpRequest(),
            response = "";
        captchaReq.open('POST', submitURL, true);
        captchaReq.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        captchaReq.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        captchaReq.responseType = 'json';
        captchaReq.onload = function (e) {
            if(captchaReq.status === 200) {
                var xhr = e.target;
                if (xhr.responseType === 'json') {
                    response = xhr.response;
                } else {
                    response = JSON.parse(xhr.responseText); // IE bug fix
                }
                reactOnValidationResponse(response);

            } else {
              throw new Error('An error occurred during your request: ' +  captchaReq.status + ' ' + captchaReq.statusText);
            }
        };
        captchaReq.send('session_key=' + sessionKey + '&result=' + result);
    });

    // Enter on text input should submit it
    var textInput = document.querySelectorAll(".captcha-input > input")[0];
    if (textInput){
        textInput.addEventListener('keypress', function (e) {
            var key = e.which || e.keyCode;
            if (key === 13) { // 13 is enter key
              document.getElementById('submit').click();
            };
        });
    };
}
