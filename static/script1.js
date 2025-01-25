function showDoctorsField(){
    const roleSelect = document.getElementById("role");
    const doctorField = document.getElementById("doctorFields");

    if (roleSelect.value === "2"){
        doctorField.style.display = "block";
    }
    else{
        doctorField.style.display = "none";
    }

}


window.onload = function(){
    document.getElementById('role').addEventListener("change" , showDoctorsField);
    showDoctorsField();
}