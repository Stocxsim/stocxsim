function f1(){
    const form=new FormData();
    const email=document.getElementById("Email").value;
    console.log(email);
    form.append("Email",email);
    fetch("/submit",{
        method:"POST",
        body:form
    }).then(response=>response.json()).then(data=>{
        if(data.message===true){
            showPasswordField();
            
        }else{
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
function step2(){

  const email = document.getElementById("Email").value;
  const username = document.getElementById("username").value;
  const pass1 = document.getElementById("password1").value;
  const pass2 = document.getElementById("password2").value;

  if(pass1 !== pass2){
      alert("Passwords do not match");
      return;
  }

  const form = new FormData();
  form.append("Email", email);
  form.append("username", username);
  form.append("password", pass1);

  fetch("/submit", {
    method: "POST",
    body: form
  })
  .then(res => res.json())
  .then(data => {

      if(data.message === false){
        
          document.getElementById("div-2").classList.add("d-none");
          document.getElementById("div-3").classList.remove("d-none");
      } else {
          alert("Signup failed");
      }

  });

}



// ---------- STEP 3: VERIFY OTP ----------
function step3(){

  const otp = document.getElementById("otp").value;

  const form = new FormData();
  form.append("otp", otp);

  fetch("/verify-otp", {
    method: "POST",
    body: form
  })
  .then(res => res.json())
  .then(data => {

      if(data.verified === true){
          alert("Account Created Successfully 🎉");
      } else {
          alert("Invalid OTP");
      }

  });

}