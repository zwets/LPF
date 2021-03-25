const { exec } = require('child_process');
const fs = require('fs');
const storage = require('electron-json-storage');

storage.get('currentConfig', function(error, data) {
  if (error) throw error;

  var element = document.getElementById('current-config');
  element.textContent = data.dbdir;

});

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
        displayContents(contents);
    };
    reader.readAsText(file);
}

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
    var configobj = JSON.parse(element);
    var init_path = configobj.dbdir;
    console.log(init_path);

    storage.set('currentConfig', { exepath: configobj.exepath, dbdir: configobj.dbdir }, function(error) {
        if (error) throw error;
    });


    alert("The current system configuration has been changed to " + init_path);

    var element = document.getElementById('current-config');
    element.textContent = init_path;

}

