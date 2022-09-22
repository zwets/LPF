const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');

function merge_fastq() {
    var current_moss_system = require('/opt/moss_db/config.json')["current_working_db"] + "/";
    var execstring = `~/anaconda3/bin/conda run -n base python3 /opt/moss/src/moss_merge_fastq.py -config_name ${current_moss_system}`
    console.log(execstring);
    console.log("job submitted");
    alert("job submitted.");
    var loader = document.getElementById('loader');
    loader.style.display = 'block';
    document.getElementById('loadermessage').innerHTML = "Merging fastq files. This might take some time, if there are a lot of files.";
    exec(execstring, (error, stdout, stderr) => {
        if (error) {
          //If error, change accepted ui to failure, which attached message.
          console.error(`exec error: ${error}`);
          alert(`exec error: ${error}`);
          return;
        }
        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);
        //Automatic change of correct system config to
        alert("Your fastq files have been merged!");
        loader.style.display = 'none';
        document.getElementById('loadermessage').innerHTML = "Your fastq files have been merged.";
    }
}


function submitinit() {
  var config_name = document.getElementById("config-name").value;

  var kmaindex_path = getfolder("kmaindex-path");

  var execstring = `~/anaconda3/bin/conda run -n base python3 /opt/moss/src/moss_init.py -config_name ${config_name} -db ${kmaindex_path}`
  console.log(execstring);


  console.log("job submitted");

  alert("job submitted.");

  var loader = document.getElementById('loader');
  loader.style.display = 'block';
  document.getElementById('loadermessage').innerHTML = "Setting up database system. Depending on the database size, this might take some time (>20 min).";

  exec(execstring, (error, stdout, stderr) => {



    if (error) {
      //If error, change accepted ui to failure, which attached message.
      console.error(`exec error: ${error}`);
      alert(`exec error: ${error}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);

    //Automatic change of correct system config to
    alert("Your database has been set up!");

    loader.style.display = 'none';
    document.getElementById('loadermessage').innerHTML = "Your database system has been set up.";



      });

}


