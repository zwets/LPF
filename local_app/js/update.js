const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');

function update_moss(argument){
    var current_moss_system = require('/opt/moss_db/config.json')["current_working_db"] + "/";
    if (argument == 'pab') {
        var cmd = `~/anaconda3/bin/conda run -n moss python3 /opt/moss/ubuntu_22_install.py -pab`;
    }
    var loader = document.getElementById('loader');
    loader.style.display = 'block';
    document.getElementById('loadermessage').innerHTML = "Updating....";
    console.log(cmd);
    exec(cmd, (error, stdout, stderr) => {

            if (error) {
                alert(`exec error: ${error}`);
                document.getElementById('loadermessage').innerHTML = `Update has failed: ${error}`;
                loader.style.display = 'none';
              console.error(`exec error: ${error}`);
              return;
            } else {
                alert("Update has completed. Please restart the MOSS app for full effect.");
                document.getElementById('loadermessage').innerHTML = `Update has been completed.`;
                loader.style.display = 'none';
            }


        });
}