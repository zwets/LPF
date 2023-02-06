const { exec } = require('child_process');
const fs = require('fs');
const storage = require('electron-json-storage');

function displayContents(contents) {
    var element = document.getElementById('file-content');
    element.textContent = contents;
    document.getElementById('prtt-arguments').style.display = "block";
}

function singleInputFunction() {
    document.getElementById('single-input').style.display = "block";
    document.getElementById('multiple-input').style.display = "None";
    document.getElementById('parameter-section').style.display = "block";
}
function multipleInputFunction() {
    document.getElementById('multiple-input').style.display = "block";
    document.getElementById('single-input').style.display = "None";
    document.getElementById('parameter-section').style.display = "block";
}



function submitAnalysis() {
    var element = document.getElementById('file-content').innerHTML;
    var config_json = require('/opt/LPF_db/config.json');

    storage.set('currentConfig', { exepath: configobj.exepath, db_dir: configobj.db_dir }, function(error) {
        if (error) throw error;
    });


    alert("The current system configuration has been changed to " + init_path);

    var element = document.getElementById('current-config');
    element.textContent = init_path;

}

