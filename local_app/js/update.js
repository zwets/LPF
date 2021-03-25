const { exec } = require('child_process');
const fs = require('fs')


var configfile = "None";
document.getElementById("configfile").innerHTML = configfile;

function readSingleFile(e) {
    var file = e.target.files[0];
    if (!file) {
        return;
    }
    var reader = new FileReader();
    reader.onload = function(e) {
        var contents = e.target.result;
        displayUpdateData(contents);
    };
    reader.readAsText(file);
}

function displayUpdateData(contents) {
    var configobj = JSON.parse(contents);
    var updateFile = configobj.dbdir + "syncFiles/update.log";

    readTextFile(updateFile, function(text){
            var data = JSON.parse(text);
            var datalist = [[],[]];

            let objlenght = Object.keys(data).length;
            for (i = 0; i < objlenght; i++) {
                datalist[0].push(Object.keys(data)[i]);
                datalist[1].push(Object.values(data)[i]);
            }

            console.log(datalist);

            //document.getElementById('showData').innerHTML = "";

            //document.getElementById('showData').appendChild(makeUL(datalist, configobj));


        });
}

function readTextFile(file, callback) {
    var rawFile = new XMLHttpRequest();
    rawFile.overrideMimeType("application/json");
    rawFile.open("GET", file, true);
    rawFile.onreadystatechange = function() {
        if (rawFile.readyState === 4 && rawFile.status == "200") {
            callback(rawFile.responseText);
        }
    }
    rawFile.send(null);
}

function readTextFileUpdateDiv(file, div, callback) {
    var rawFile = new XMLHttpRequest();
    rawFile.overrideMimeType("application/json");
    rawFile.open("GET", file, true);
    rawFile.onreadystatechange = function() {
        if (rawFile.readyState === 4 && rawFile.status == "200") {
            callback(rawFile.responseText);
        }
    }
    rawFile.send(null);
}

