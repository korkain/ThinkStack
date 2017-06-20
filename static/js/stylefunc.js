function blurFunction(state) {
    var containerElement = document.getElementById('main_container');

    if (state) {
        containerElement.setAttribute('class', 'blur');
    } else {
        containerElement.setAttribute('class', null);
    }
}