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
