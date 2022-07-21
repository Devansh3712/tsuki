var modal1 = document.getElementById("modal-1")
var modal2 = document.getElementById("modal-2")

var btn1 = document.getElementById("btn-1")
var btn2 = document.getElementById("btn-2")

var span = document.getElementsByClassName("close-1")[0]
var span2 = document.getElementsByClassName("close-2")[0]

if (btn1 != null) {
    btn1.onclick = function() {
        modal1.style.display = "block";
    }
    span.onclick = function() {
        modal1.style.display = "none";
    }
}

if (btn2 != null) {
    btn2.onclick = function() {
        modal2.style.display = "block";
    }
    span2.onclick = function() {
        modal2.style.display = "none";
    }
}

window.onclick = function(event) {
    if (modal1 != null && event.target == modal1) {
        modal1.style.display = "none";
    }
    if (modal2 != null && event.target == modal2) {
        modal2.style.display = "none";
    }
}

const togglePassword = document.querySelector('#togglePassword')
const password = document.querySelector('#password')

if (togglePassword != null && password != null) {
    togglePassword.addEventListener("click", function (e) {
        const type = password.getAttribute("type") === "password" ? "text" : "password";
        password.setAttribute("type", type);
        this.classList.toggle("fa-eye-slash");
    });
}
