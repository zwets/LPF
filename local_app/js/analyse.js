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



function submitSingleAnalysis() {
    var input = document.getElementById('csv_file');
    var children = "";
        for (var i = 0; i < input.files.length; ++i) {
            children +=  input.files.item(i).path + ',';
         }
    var parallel_input = children.slice(0, -1);
    var input_array = parallel_input.split(",");
    var csv_path = input_array[0];

    var cmd_msg = `conda run -n base python3 ${exepath}src/moss_parallel_wrapper.py -i ${input_array[0]} -input_type ${sequence_type} -db_dir ${db_dir} -exepath ${exepath} -threads ${threads} -jobs ${jobs}`;

    execute_command_as_subprocess(cmd_msg);

}


function execute_command_as_subprocess(cmd, print_msg) {
    console.log(cmd);

    console.log("Analysis has been submitted");

    alert("Analysis has been submitted");

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

