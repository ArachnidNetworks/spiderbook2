function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

document.getElementsByClassName("filein")[0].onchange = function () {
    document.getElementsByClassName("filein-btn")[0].innerHTML = this.value.replace("C:\\fakepath\\", "");
};

async function open_postcreator() {
    const postcreator = document.querySelector(".post-creator");
    console.log(postcreator.style);
    console.log(postcreator.style.height);
    if (postcreator.style.height == "") {
        postcreator.style.height = "620px";
    }
    else {
        postcreator.style.height = "";
    }
}
