const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');

function update_moss(){
    var current_moss_system = require('/opt/moss_db/config.json')["current_working_db"] + "/";
    var cmd = `conda run -n base python3 /opt/moss/moss_install.py -light`;
    var loader = document.getElementById('loader');
    loader.style.display = 'block';
    document.getElementById('loadermessage').innerHTML = "Basecalling is running";
    exec(cmd, (error, stdout, stderr) => {

            if (error) {
                alert(`exec error: ${error}`);
                document.getElementById('loadermessage').innerHTML = `Update has failed: ${error}`;
                loader.style.display = 'none';
              console.error(`exec error: ${error}`);
              return;
            } else {
                alert("Base calling has completed.");
                document.getElementById('loadermessage').innerHTML = `Update has been completed: ${stdout}`;
                loader.style.display = 'none';
            }


        });
}