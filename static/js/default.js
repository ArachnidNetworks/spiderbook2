function ctrl_aside(state) {
    const aside = document.querySelector("#popular-cats-a");
    if (state) {
        aside.classList.add("closed");
    }
    else {
        aside.classList.remove("closed");
    }
}