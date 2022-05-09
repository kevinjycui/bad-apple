// Disable CSP and inject JavaScript via Browser Extension

const chart = [...document.getElementsByClassName("line-series")];

let frame = 1;

const interval = setInterval(() => {        
    xhr = new XMLHttpRequest();
    xhr.open("GET", `http://127.0.0.1:5000/?frame=${frame}`);
    xhr.send();
    xhr.onload = function(e) {
        lines = JSON.parse(xhr.response);

        if (lines.result === null)
            clearInterval(interval);
    
        chart.forEach((series, l) => {
            let points = series.getAttribute("d").split(",");
            for (let i=1; i<points.length; i++) {
                let coordinates = points[i].split("L");
                coordinates[0] = lines.result[l][i].toString();
                points[i] = coordinates.join("L");
            }
            series.setAttribute("d", points.join(","));
        });
    }

    frame++;

}, 500);

