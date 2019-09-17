function ctrl_aside(state) {
    const aside = document.querySelector("#popular-cats-a");
    // const open_aside = document.querySelector("#open-aside");
    if (state) {
        aside.classList.add("closed");
        //open_aside.classList.add("oa_active");
    }
    else {
        aside.classList.remove("closed");
        //open_aside.classList.remove("oa-active");
    }
}