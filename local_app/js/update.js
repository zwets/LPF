const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');

function update_LPF(argument){
    var current_LPF_system = require('/opt/LPF_db/config.json')["current_working_db"] + "/";
    if (argument == 'pab') {
        var cmd = `~/anaconda3/bin/conda run -n LPF python3 /opt/LPF/ubuntu_22_install.py -pab`;
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
                alert("Update has completed. Please restart the LPF app for full effect.");
                document.getElementById('loadermessage').innerHTML = `Update has been completed.`;
                loader.style.display = 'none';
            }


        });
}