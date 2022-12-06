const box = document.getElementById('hide');

function handleRadioClick() {
    if (document.getElementById('secUserYes').checked) {
        box.style.display = 'block';
    } else {
        box.style.display = 'none';
    }
}

const radioButtons = document.querySelectorAll('input[name="secondUser"]');
radioButtons.forEach(radio => {
    radio.addEventListener('click', handleRadioClick);
});