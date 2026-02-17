function f1() {
    const passwordSection = document.getElementById("passwordbox");
    const emailInput = document.getElementById("Email");
    const email = (emailInput?.value || "").trim();
    const loginError = document.getElementById("login-error");

    const showLoginError = (message) => {
        if (!loginError) return;
        loginError.textContent = message;
        loginError.classList.remove("d-none");
    };

    const clearLoginError = () => {
        if (!loginError) return;
        loginError.textContent = "";
        loginError.classList.add("d-none");
    };

    if (!email) {
        // Validation failure: stay on login, keep button visible, no redirect
        clearLoginError();
        showLoginError("Please enter your email to continue.");
        document.getElementById("div-1")?.classList.remove("d-none");
        document.getElementById("div-2")?.classList.add("d-none");
        passwordSection?.classList.add("d-none");
        emailInput?.focus();
        return;
    }

    clearLoginError();

    if (passwordSection.classList.contains("d-none")) {
        const form = new FormData();
        form.append("Email", email);
        fetch("/login/submit", {
            method: "POST",
            body: form
        }).then(response => response.json()).then(data => {
            if (data.message === true) {
                passwordSection.classList.remove("d-none");
                showOrderBanner("success","Email Verified","Please enter your password to login.");
            } else {
                const email_in_otp = document.getElementById("Email_readonly");
                email_in_otp.value = email;
                document.getElementById("div-1").classList.add("d-none");
                document.getElementById("div-2").classList.remove("d-none");
                    showOrderBanner(
  "error",
  "Subscription Failed",
  "Please try again."
);
            }
        });
    }
    else {
        const form = new FormData();
        const passwordInput = document.getElementById("password").value;
        form.append("Email", email);
        form.append("Password", passwordInput);

        fetch("/login/save-user", {
            method: "POST",
            body: form
        }).then(response => response.json()).then(data => {
            if (data.success === true) {
                // Hide modal backdrop & freeze UI
                document.getElementById("loginModal").classList.remove("show");
                document.querySelector(".modal-backdrop")?.remove();

                // Show spinner
                document.getElementById("login-spinner").classList.remove("d-none");

                // Redirect after short delay
                setTimeout(() => {
                    window.location.href = "/login/dashboard";
                }, 1500);

            } else {
                showOrderBanner(
  "error",
  "Login Failed",
  "Wrong password. Please try again."
);
            }
        });
    }
}

// Clear validation error as user types
document.getElementById("Email")?.addEventListener("input", () => {
    const loginError = document.getElementById("login-error");
    if (!loginError) return;
    loginError.textContent = "";
    loginError.classList.add("d-none");
});



// ---------- STEP 2: SIGNUP ----------
function step2() {
    const email = document.getElementById("Email").value;
    const username = document.getElementById("username").value;

    // validation of Username
    if (!isValidUsername(username)) {
        showOrderBanner(
  "error",
  "Invalid Username",
  "Username must be 3–15 characters long and contain only letters."
);
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

    if (isValidPassword(pass1)) {

        showOrderBanner("error", "Weak password", isValidPassword(pass1));
        // clear both fields
        pass1Input.value = "";
        pass2Input.value = "";

        // focus first password field again
        pass1Input.focus();

        return;
    }

    if (pass1 !== pass2) {
        showOrderBanner(
  "error",
  "Password Mismatch",
  "Both passwords must be the same."
);
        // clear both again
        pass2Input.value = "";

        pass1Input.focus();

        return;
    }


    const form = new FormData();
    form.append("Email", email);
    form.append("Username", username);
    form.append("Password", pass1);

    fetch("/login/signup", {
        method: "POST",
        body: form
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            if (data.message) {

                document.getElementById("div-2").classList.add("d-none");
                document.getElementById("div-3").classList.remove("d-none");
            } else {
                showOrderBanner(
  "error",
  "Signup Failed",
  "Please try again."
);
            }

        });

}


// ---------- STEP 3: VERIFY OTP ----------
function step3() {

    const otp = document.getElementById("otp").value;
    const email = document.getElementById("Email").value;
    const form = new FormData();
    form.append("otp", otp);
    form.append("email", email); 

    fetch("/login/verify-otp", {
        method: "POST",
        body: form
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            if (data.message === true) {
                showOrderBanner(
  "success",
  "Account Created",
  "Your account has been created successfully 🎉",
);
                window.location.href = "/login/dashboard";
            } else {
                showOrderBanner(
  "error",
  "Invalid OTP",
  "Please try again."
);
            }
        });

}

function isValidPassword(password) {

    if (password.length < 8) {
    return "Password must be at least 8 characters long";
  }
  if (!/[A-Z]/.test(password)) {
    return "Password must contain at least one uppercase letter";
  }
  if (!/[a-z]/.test(password)) {
    return "Password must contain at least one lowercase letter";
  }
  if (!/[0-9]/.test(password)) {
    return "Password must contain at least one digit";
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return "Password must contain at least one special character";
  }
  return null; // ✅ valid password
}


function isValidUsername(username) {

    if (username.length < 3 || username.length > 15) {
        return false;
    }

    if (!/^[a-zA-Z]+$/.test(username)) {
        return false;
    }

    return true;
}

// ---------- AUTH STATE / HISTORY HANDLING ----------
function hideLoginSpinner() {
    const spinner = document.getElementById("login-spinner");
    if (spinner) spinner.classList.add("d-none");
}

async function checkAuthAndRedirect() {
    try {
        const res = await fetch("/login/status", { method: "GET" });
        if (!res.ok) {
            hideLoginSpinner();
            return;
        }
        const data = await res.json();
        if (data && data.authenticated === true) {
            window.location.replace("/login/dashboard");
            return;
        }
        hideLoginSpinner();
    } catch (e) {
        hideLoginSpinner();
    }
}

// Ensure spinner never sticks on back/forward cache restores
window.addEventListener("pageshow", () => {
    hideLoginSpinner();
    checkAuthAndRedirect();
});

// Handle browser back/forward navigation
window.addEventListener("popstate", () => {
    hideLoginSpinner();
    checkAuthAndRedirect();
});

function showOrderBanner(type, message, detail = "") {
  const banner = document.getElementById("orderBanner");
  if (!banner) return;

  const icon =
    type === "success"
      ? '<i class="bi bi-check-lg"></i>'
      : '<i class="bi bi-x-lg"></i>';

  banner.className = `order-banner ${type}`;
  banner.innerHTML = `
    <div class="order-banner-icon">${icon}</div>
    <div>
      <div class="order-banner-title">${message}</div>
      ${detail ? `<div class="order-banner-detail">${detail}</div>` : ""}
    </div>
    <button class="order-banner-close">&times;</button>
  `;

  banner.classList.add("show");

  banner.querySelector(".order-banner-close").onclick = () => {
    banner.classList.remove("show");
  };

  clearTimeout(banner._timer);
  banner._timer = setTimeout(() => {
    banner.classList.remove("show");
  }, 3500);
}