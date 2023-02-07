const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');
const mkdirp = require('mkdirp');
const path = require("path");
const Dialogs = require("dialogs");

function execute_command_as_subprocess(cmd, print_msg) {
    console.log(cmd);

    console.log("Analysis has been submitted");

    alert("Analysis has been submitted. Go to the Results section is the left menu to see progress and final results.");

    exec(cmd, (error, stdout, stderr) => {

        if (error) {
            alert(`exec error: ${error}`);
            document.getElementById('analysis-msg').innerHTML = `Analysis has failed: ${error}`;
          console.error(`exec error: ${error}`);
          return;
        } else {
            alert("Analysis has been completed.");
            document.getElementById('analysis-msg').innerHTML = `Analysis has been completed`;
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);



      });

}

function hasDuplicates(array) {
    return (new Set(array)).size !== array.length;
}

function isExperimentNameValid(experiment_name) {
    if (experiment_name.endsWith('.json')) {
        alert("Experiment name cannot end with .json");
        return false;
    }
    return true;
}
function create_meta_data_table_fastq(){
    const experiment_name = document.getElementById('experiment-name').value;

    !(isExperimentNameValid(experiment_name)) ? console.log("experiment name is not valid") : console.log("experiment name is valid");

}
