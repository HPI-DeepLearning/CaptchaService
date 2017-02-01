/*
*
*       Requirements: - form must have class "captcha-form"
*                     - form button must have class "captcha-button"
*
*/

var captchaSolved = false,
    HTMLOverlay = {
        text: '<div class="overlay">' +
          '<div class="captcha-card">' +
            '<div class="captcha-content">' +
                '<div class="captcha-image-container">' +
                    '<div class="first-captcha"><img id="first-text-token"></div>' +
                    '<div class="second-captcha"><img id="second-text-token"></div></div>' +
                '</div>' +
                '<div class="captcha-input"><input type="text" placeholder="Answer..."></input></div>' +
                '<div class="captcha-actions">' +
                    '<a href="#" id="submit">Submit</a>' +
                    '<a href="#" id="refresh"><i class="fa fa-refresh">refresh</i></a>' +
                '</div>' +
            '</div>' +
          '</div>' +
        '</div>',
        image: '<div class="overlay"><div class="captcha-card"><div class="captcha-content"><div class="task"><p></p></div>' +
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
                    '<a href="#" id="submit">Submit</a><a href="#" id="refresh"><i class="fa fa-refresh">refresh</i></a>' +
                '</div></div></div>'
    },
    insertSessionKey = function(key) {
        var inputElementString = '<input id="session_key" type="hidden" name="captcha-key" value="' + key + '" />',
            form = document.querySelectorAll('.captcha-form')[0],
            div = document.createElement('div');
        div.innerHTML = inputElementString;
        var input = div.firstChild;
        form.appendChild(input);
    },
    insertCaptchaData = {
        text: function (response) {
            var firstImage = document.querySelectorAll('.first-captcha > img')[0],
                secondImage = document.querySelectorAll('.second-captcha > img')[0];
            if (!firstImage || !secondImage) {
                throw new Error('missing text captcha markup!');
            }
            if (response.session_key){
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
            if (response.session_key){
                insertSessionKey(response.session_key);
            }
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
        //TODO
    },
    obtainResult = {
        text: function() {
            var result = document.querySelectorAll(".captcha-input input").value;
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
            console.log(response);
            handleResponse(response);
        } else {
            response = JSON.parse(xhr.responseText); // IE bug fix
        }
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
                    insertCaptchaData[type](response);
                } else {
                    response = JSON.parse(xhr.responseText); // IE bug fix
                    insertCaptchaData[type](response);
                }
            } else {
              throw new Error('An error occurred during your request: ' +  captchaReq.status + ' ' + captchaReq.statusText);
            }
        };
        captchaReq.send('session_key=' + sessionKey);
    });

    // 5. Click on overlay should hide captcha card
    var captchaOverlay = document.getElementsByClassName('overlay')[0];
    captchaOverlay.addEventListener('click', function(e){
        captchaOverlay.classList.remove('fadeIn');
        captchaOverlay.classList.remove('show');
    });
    var captchaCard = document.getElementsByClassName('captcha-card')[0];
    captchaCard.addEventListener('click', function(e){
        e.stopPropagation();
    });

    // 6. POST Form on validation and secrect key generated by Web Service

    var submit = document.getElementById('submit');
    console.log(submit);
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
                    insertCaptchaData[type](response);
                } else {
                    response = JSON.parse(xhr.responseText); // IE bug fix
                    insertCaptchaData[type](response);
                }
            } else {
              throw new Error('An error occurred during your request: ' +  captchaReq.status + ' ' + captchaReq.statusText);
            }
        };
        captchaReq.send('session_key=' + sessionKey + '&result=' + result);
    });
}



/*

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
