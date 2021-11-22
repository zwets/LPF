const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');




storage.get('currentConfig', function(error, data) {
  if (error) throw error;

  var element = document.getElementById('current-config');
  element.textContent = data.db_dir;
  var element = document.getElementById('current-exepath');
  element.textContent = data.exepath;


});

function ubuntu_show() {
    document.getElementById("ubuntu_section").style.display = "block";
    document.getElementById("mac_section").style.display = "none";
}

function mac_show() {
    document.getElementById("mac_section").style.display = "block";
    document.getElementById("ubuntu_section").style.display = "none";

}

function ubuntu_update_soft() {
    var exepath = document.getElementById('current-exepath').innerHTML;
    var loader = document.getElementById('loader');
    loader.style.display = 'block';

    cmd = `python3 ${exepath}src/moss_update.py -exepath ${exepath}`;
    console.log(cmd);

    document.getElementById('loadermessage').innerHTML = "Updating dependencies";

    console.log("Moss dependency update has begun.");

    alert("Moss dependency update has begun.");

    exec(cmd, (error, stdout, stderr) => {

        if (error) {
            alert(`exec error: ${error}`);
            document.getElementById('loadermessage').innerHTML = `Updating dependencies has failed: ${error}`;
            loader.style.display = 'none';
          console.error(`exec error: ${error}`);
          return;
        } else {
            alert("Update has completed.");
            document.getElementById('loadermessage').innerHTML = `Updating dependencies has been completed: ${stdout}`;
            loader.style.display = 'none';
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);



      });

}

function ubuntu_update_force() {

    var exepath = document.getElementById('current-exepath').innerHTML;
    var loader = document.getElementById('loader');
    loader.style.display = 'block';

    cmd = `python3 ${exepath}src/moss_update.py -exepath ${exepath} -force`;
    console.log(cmd);

    document.getElementById('loadermessage').innerHTML = "Updating dependencies";

    console.log("Moss dependency update has begun.");

    alert("Moss dependency update has begun.");

    exec(cmd, (error, stdout, stderr) => {

        if (error) {
            alert(`exec error: ${error}`);
            document.getElementById('loadermessage').innerHTML = `Updating dependencies has failed: ${error}`;
            loader.style.display = 'none';
          console.error(`exec error: ${error}`);
          return;
        } else {
            alert("Base calling has completed.");
            document.getElementById('loadermessage').innerHTML = `Updating dependencies has been completed: ${stdout}`;
            loader.style.display = 'none';
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);



      });

}

function mac_update_soft() {

    var exepath = document.getElementById('current-exepath').innerHTML;
    var loader = document.getElementById('loader');
    loader.style.display = 'block';

    cmd = `python3 ${exepath}src/moss_update.py -exepath ${exepath} -mac`;
    console.log(cmd);

    document.getElementById('loadermessage').innerHTML = "Updating dependencies";

    console.log("Moss dependency update has begun.");

    alert("Moss dependency update has begun.");

    exec(cmd, (error, stdout, stderr) => {

        if (error) {
            alert(`exec error: ${error}`);
            document.getElementById('loadermessage').innerHTML = `Updating dependencies has failed: ${error}`;
            loader.style.display = 'none';
          console.error(`exec error: ${error}`);
          return;
        } else {
            alert("Base calling has completed.");
            document.getElementById('loadermessage').innerHTML = `Updating dependencies has been completed: ${stdout}`;
            loader.style.display = 'none';
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);



      });;

}

function mac_update_force() {

    var exepath = document.getElementById('current-exepath').innerHTML;
    var loader = document.getElementById('loader');
    loader.style.display = 'block';

    cmd = `python3 ${exepath}src/moss_update.py -exepath ${exepath} -mac -force`;
    console.log(cmd);

    document.getElementById('loadermessage').innerHTML = "Updating dependencies";

    console.log("Moss dependency update has begun.");

    alert("Moss dependency update has begun.");

    exec(cmd, (error, stdout, stderr) => {

        if (error) {
            alert(`exec error: ${error}`);
            document.getElementById('loadermessage').innerHTML = `Updating dependencies has failed: ${error}`;
            loader.style.display = 'none';
          console.error(`exec error: ${error}`);
          return;
        } else {
            alert("Base calling has completed.");
            document.getElementById('loadermessage').innerHTML = `Updating dependencies has been completed: ${stdout}`;
            loader.style.display = 'none';
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);



      });
}