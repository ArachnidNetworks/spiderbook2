document.getElementsByClassName("filein")[0].onchange = function () {
    document.getElementsByClassName("filein-btn")[0].innerHTML = this.value.replace("C:\\fakepath\\", "");
};
