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

function select_flow_cell(flow_cell, data_json){
    console.log
}

function select_output(){
    console.log
}

function start_base_calling(){
    var db_dir = document.getElementById('current-config').innerHTML;
    var exepath = document.getElementById('current-exepath').innerHTML;
    var fast5 = document.getElementById('fast5-input-field');
    var output = document.getElementById('output-field');
    var flowcell = document.getElementById('flow-cell');
    var kit = document.getElementById('flow-cell');

    readTextFile(db_dir + "analyticalFiles/workflow.json", function(text){
        var data = JSON.parse(text);
        console.log(data);

        var lookup = {};
        var items = data;

        var result = [];

        for (var item, i = 0; item = items[i++];) {
          var flowcell = item.flowcell;


          if (!(name in lookup)) {
            lookup[flowcell] = 1;
            result.push(flowcell);
          }
        }


        console.log(result);







    });




    /*

    var sequence_type = document.getElementById("multiple-input-type").value;
    var csv_name = document.getElementById("metadata_sheet_name").value;
    var children = "";
    for (var i = 0; i < input.files.length; ++i) {
        children +=  input.files.item(i).path + ',';
     }
    var parallel_input = children.slice(0, -1);
    var input_array = parallel_input.split(",");

    var cmd_msg = `python3 ${exepath}src/create_metadata_csv.py -i ${parallel_input} -input_type ${sequence_type} -db_dir ${db_dir} -exepath ${exepath} -name ${csv_name}`;
    console.log(cmd_msg);
    var print_msg = `Your metadata sheet has been created at: ${db_dir}analyticalFiles/metadata_csv/${csv_name}.csv. <br>You may open it in excel or another program of your own choosing and fill in the metadata. <b>Remember to save it as a csv file afterwards.</b> <br>Once the metadata has been filled in, the sheet is ready to be submitted for analysis. <br>It is recommended to fill in as many of the data collumns as possible, but none are required. <br>Additional metadata can be added later, and the given metadata also be changed after the analysis`;

    execute_command_as_subprocess(cmd_msg, print_msg);



    //All in python script:
        //load files
        //Copy template to db_dir/analyticalFiles/tmp_metadata_csv/chosen_name
        //Insert files into csv and safe file
    //Msg or open button, whichever is easiest
    */

}

function execute_command_as_subprocess(cmd, print_msg) {
    console.log(cmd);

    console.log("Metadata Sheet Creation has begun.");

    alert("Metadata Sheet Creation has begun.");



    exec(cmd, (error, stdout, stderr) => {

        if (error) {
            alert(`exec error: ${error}`);
          console.error(`exec error: ${error}`);
          return;
        } else {
            alert("Metadata Sheet Creation has been completed.");
            document.getElementById('metadata-sheet-msg').innerHTML = print_msg;
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);



      });

}

function readTextFile(file, callback) {
    var rawFile = new XMLHttpRequest();
    rawFile.overrideMimeType("application/json");
    rawFile.open("GET", file, true);
    rawFile.onreadystatechange = function() {
        if (rawFile.readyState === 4 && rawFile.status == "200") {
            callback(rawFile.responseText);
        }
    }
    rawFile.send(null);
}