const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');

function getfolder(id) {
    var trypath = document.getElementById(id).files[0].path;
    var Folder = trypath.split("/");
    var returnstring = "";
    for (var i = 0; i < Object.keys(Folder).length - 1; i++ ) returnstring = returnstring + Folder[i] + "/";
    return returnstring;
 }

function merge_fastq() {
  var fastq_name = document.getElementById("fastq-name").value;
  var current_moss_system = require('/opt/moss_db/config.json')["current_working_db"] + "/";
  var folder = getfolder("fastq_folder_path");
  /*
  var execstring = `~/anaconda3/bin/conda run -n base python3 /opt/moss/src/moss_merge_fastq.py -folder ${folder} -name ${fastq_name}`;
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
    */
}
