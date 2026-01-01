function f1() {
    const form = new FormData();
    const email = document.getElementById("Email").value;
    console.log(email);
    form.append("Email", email);
    fetch("/login/submit", {
        method: "POST",
        body: form
    }).then(response => response.json()).then(data => {
        if (data.message === true) {
            showPasswordField();

        } else {
            const email_in_otp = document.getElementById("Email_readonly");
            email_in_otp.value = email;
            document.getElementById("div-1").classList.add("d-none");
            document.getElementById("div-2").classList.remove("d-none");
            alert("Subscription failed. Please try again.");
        }
    });
}

function showPasswordField() {
    const passwordSection = document.getElementById("passwordbox");
    passwordSection.classList.remove("d-none");
}


// ---------- STEP 2: SIGNUP ----------
function step2() {
    const email = document.getElementById("Email").value;
    const username = document.getElementById("username").value;

    // validation of Username
    if (!isValidUsername(username)) {
        alert("Username must be 5-15 characters long and contain only letters.");
        // clear the field
        input.value = "";
        // focus again so user can re-enter
        input.focus();
        return;
    }

    // validation of Passwords
    const pass1Input = document.getElementById("password1");
    const pass2Input = document.getElementById("password2");

    const pass1 = pass1Input.value;
    const pass2 = pass2Input.value;

    if (!isValidPassword(pass1)) {

        alert("Password must be at least 8 characters long and include at least one digit, one uppercase letter, one lowercase letter, and one special character.");

        // clear both fields
        pass1Input.value = "";
        pass2Input.value = "";

        // focus first password field again
        pass1Input.focus();

        return;
    }

    if (pass1 !== pass2) {
        alert("Passwords do not match");

        // clear both again
        pass2Input.value = "";

        pass1Input.focus();
        
        return;
    }
    
    
    const form = new FormData();
    form.append("Email", email);
    form.append("username", username);
    form.append("password", pass1);

    fetch("/login/submit", {
        method: "POST",
        body: form
    })
        .then(res => res.json())
        .then(data => {

            if (data.message === false) {

                document.getElementById("div-2").classList.add("d-none");
                document.getElementById("div-3").classList.remove("d-none");
            } else {
                alert("Signup failed");
            }

        });

}



// ---------- STEP 3: VERIFY OTP ----------
function step3() {

    const otp = document.getElementById("otp").value;
    const form = new FormData();
    form.append("otp", otp);

    fetch("/verify-otp", {
        method: "POST",
        body: form
    })
        .then(res => res.json())
        .then(data => {

            if (data.verified === true) {
                alert("Account Created Successfully 🎉");
            } else {
                alert("Invalid OTP");
            }

        });

}

function isValidPassword(password) {

    if (password.length < 8) {
        return false;
    }

    if (!/[0-9]/.test(password)) {   // must contain a digit
        return false;
    }

    if (!/[A-Z]/.test(password)) {   // must contain uppercase
        return false;
    }

    if (!/[a-z]/.test(password)) {   // must contain lowercase
        return false;
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) { // must contain special char
        return false;
    }
    return true;
}


function isValidUsername(username) {

    if (username.length < 5 || username.length > 15) {
        return false;
    }

    if (!/^[a-zA-Z]+$/.test(username)) {
        return false;
    }

    return true;
}