const { exec } = require('child_process');
const fs = require('fs')

function submitSingleAnalysis() {
    var input = document.getElementById('json_file').files[0].path;
    console.log(document.getElementById('json_file').files)
    console.log(document.getElementById('json_file').files[0].path)
    var config_json = require('/opt/moss_db/config.json');

    var cmd_msg = `conda run -n base python3 /opt/moss/src/moss_parallel_wrapper.py -json ${input}}`;
    console.log(cmd_msg);
    execute_command_as_subprocess(cmd_msg);

}

function execute_command_as_subprocess(cmd, print_msg) {
    console.log(cmd);

    console.log("Analysis has been submitted");

    alert("Analysis has been submitted. Go to Results section is the left menu to see process and final results.");

    var print_msg = `Analysis is running`;

    document.getElementById('analysis-msg').innerHTML = print_msg;

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

