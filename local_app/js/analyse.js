const { exec } = require('child_process');
const fs = require('fs')

function submitSingleAnalysis() {
    var input = document.getElementById('csv_file');
    console.log(input);
    var children = "";
        for (var i = 0; i < input.files.length; ++i) {
            children +=  input.files.item(i).path + ',';
         }
    var parallel_input = children.slice(0, -1);
    var input_array = parallel_input.split(",");
    var config_json = require('/opt/moss_db/config.json');
    console.log(input_array);

    var cmd_msg = `conda run -n base python3 /opt/moss/src/moss_parallel_wrapper.py -csv ${input_array[0]} -config_name ${config_json.current_working_db}`;
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

