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

function isExperimentNameValid(experiment_name) {
    if (experiment_name.endsWith('.json')) {
        alert("Experiment name cannot end with .json");
        return false;
    }
    return true;
}
function create_meta_data_table_fastq(){
    const experiment_name = document.getElementById('experiment-name').value;

    if (!(isExperimentNameValid(experiment_name))) {
        return;
    }

    document.getElementById('metadata-table-div').innerHTML = "";
    const file_list_obj = document.getElementById('input').files;
    const file_number = Object.keys(file_list_obj).length;
    let append_table = generate_table_fastq(file_number)
    document.getElementById('metadata-table-div').appendChild(append_table);
}


function generate_table_fastq(file_number) {

    const file_list_obj = document.getElementById('input').files;

    const table = document.createElement('table');
    table.id = "metadata_csv_table";
    table.classList.add('table');

    const headRow = document.createElement('tr');
    headRow.id = "thead_tr";
    let columnNames = [];

    const jsonData= require('/opt/LPF/datafiles/ena_list.json');
    const ena_keys = Object.keys(jsonData);
    columnNames.push.apply(columnNames, ena_keys)

    // Add the header row.
    for (let i = 0; i < columnNames.length; i++) {
      let th = document.createElement('th');
      th.appendChild(document.createTextNode(columnNames[i]));
      headRow.appendChild(th);
    }
    table.appendChild(headRow);

    // Add the data rows.
    for (let i = 0; i < file_number; i++) {
      let tr = document.createElement('tr');
      tr.id = columnNames[i] + i;
      let sample_name = file_list_obj[i].path.split("/").slice(-1);

      for (let j = 0; j < columnNames.length; j++) {
        let identifier = jsonData[columnNames[j]];
        let td = document.createElement('td');
        td.style.textAlign = "center";
        td.id = `outer${i}${j}`;
        if (j > 0) {
            if (identifier=="free_text") {
                td.defaultValue = "";
                td.classList.add("input");
                const input = document.createElement('input');
                input.id = `${tr.id}${j}`;
                td.appendChild(input);
                tr.appendChild(td);
                if (columnNames[j] =="collection_date") {
                    input.placeholder = "YYYY-MM-DD";
                    }
                continue;

            } else if (typeof identifier === "object") {
                td.defaultValue = "";
                td.classList.add("select");
                const input = document.createElement('select');
                input.id = `${tr.id}${j}`;
                let object_options = [];
                if (columnNames[j] =="country") {
                    const countryData= require('/opt/LPF/datafiles/cities_and_countries.json');
                    const countries = Object.keys(countryData);
                    const countryNames = ["Unspecified country"];
                    countryNames.push.apply(countryNames, countries);
                    object_options = countryNames;
                    input.onclick = function(){window.getCities(i, j)};
                }
		        else if (columnNames[j] == "city") {
                    object_options = Object.values(identifier);
                    input.onclick = function(){window.getCustomValue()};
                }
                else {
                    object_options = Object.values(identifier);
                    }
            for (let t = 0; t < object_options.length; t++) {
                let option = document.createElement("option");
                option.value = object_options[t];
                option.text = object_options[t];
                input.add(option);
                }
            input.defaultValue = object_options[0];
            td.appendChild(input);
            tr.appendChild(td);
            continue;
            }
        } else if (j == 0) {
            td.defaultValue = "";
            const label = document.createElement('label');
            label.id = `${tr.id}${j}`;
            label.innerHTML = sample_name;
            label.value = sample_name;
            td.appendChild(label);
            tr.appendChild(td);
            continue;
        }
        tr.appendChild(td);
      }

      table.appendChild(tr);
    }
    return table
}