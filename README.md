# CaptchaService
A captcha service that helps researchers label their datasets


## Integrate into Web application

In order to integrate the captcha service into your Web application it is essential to satisfy the following requirements:
- It is essential to integrate `captcha.min.js` and `captcha.min.css` into your delivered html file (you can customize the css file to match your design)
- The form element on your site, which needs to be captcha protected must have the class `captcha-form` and the corresponding submit button must have the class `captcha-button`
- When a user solves the captcha you will receive all your form parameters plus one extra key-value pair named `captcha-key` representing the session key
- In order to assure that your user has correctly solved the captcha you have to send a POST Request to `{captcha-service-url}/validate_session/` including this key-value pair -> you will receive a boolean which is telling you whether the client really solved the captcha correctly
- You can change the URL for your captcha service by declaring a JS var called baseURL, like `var baseURL = 'http://localhost:8000/'` before the included `captcha.min.js` script

It works by appending an absolute positioned overlay to your body node, which is fading in when your form button gets clicked but the captcha was not solved yet. As soon as the captcha is solved by the user the button gets clicked and behaves like before, thus submitting the form.
