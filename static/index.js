function validate() {
  const pass = document.getElementById("pass").value;
  fetch("/validate", { method: "POST", body: JSON.stringify({ "password": pass }) }).then(res => res.json()).then(data => {
    if (data.content != null && data.content == "Valid") {
      window.location.reload();
    } else {
      alert("Invalid panel password provided");
    }
  })
}

function keyDown(e){
  if(e.keyCode == 13){ // Scuffed enter key support
    validate();
  }
}