const img = document.getElementById('post-image');
img.onclick = () => {
    if (img.style.cssFloat == "left") {
        img.style.cssFloat = "none";
        img.style.maxWidth = "100%";
        img.style.maxHeight = "100%";
        img.style.minWidth = "0%";
    }
    else {
        img.style.cssFloat = "left";
        img.style.maxWidth = "20%";
        img.style.maxHeight = "700px";
        img.style.minWidth = "5%";
    }
};