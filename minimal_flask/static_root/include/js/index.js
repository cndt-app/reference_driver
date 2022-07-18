import 'flatpickr';
import Chocolat from "chocolat";

require("./common/customComponents");

import 'flatpickr/dist/themes/light.css';
import 'chocolat/dist/css/chocolat.css';
import '../styles/style.css';


// Init plugins here
document.addEventListener("DOMContentLoaded", function (event) {
    Chocolat(document.querySelectorAll('.chocolat-image'));
});
