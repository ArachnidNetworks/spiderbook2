function ctrl_aside(s) {
    const aside = document.querySelector("#popular-cats-a");
    const open_aside = document.querySelector("#open-aside");
    if (s) {
        aside.classList.add("closed");
        open_aside.classList.add("oa-active");
    }
    else {
        aside.classList.remove("closed");
        open_aside.classList.remove("oa-active");
    }
}

function mclickpc(cat) {
    cat.classList.add("touched");
}