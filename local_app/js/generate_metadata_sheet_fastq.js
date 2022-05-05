const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');
var mkdirp = require('mkdirp');
var path = require("path");

function execute_command_as_subprocess(cmd, start_msg, end_msg, fail_msg) {

    alert(start_msg);

    var create_button = document.createElement('button');
    create_button.classList.add('button-7');
    create_button.type = "button";
    create_button.id = "go-to-analyses-button";
    create_button.innerHTML = "Proceed to basecalling overview";
    create_button.onclick = function() {
      location.href='./basecalling.html';
    }
    create_button.style.width = "400px";
    create_button.style.height = "150px";
    create_button.style.fontSize = "large"

    document.getElementById('metadata-table-div').appendChild(document.createElement('br'));
    document.getElementById('metadata-table-div').appendChild(document.createElement('br'));

    document.getElementById('metadata-table-div').appendChild(create_button);

    exec(cmd, (error, stdout, stderr) => {

        if (error) {
            alert(`${error}`);
            alert(fail_msg);
          console.error(`exec error: ${error}`);
          return;
        } else {
            alert(end_msg);
        }

      });

}

function hasDuplicates(array) {
    return (new Set(array)).size !== array.length;
}

function create_metadata_table_fastq(){

    document.getElementById('metadata-table-div').innerHTML = "";
    var file_list_obj = document.getElementById('input').files;
    var file_number = Object.keys(file_list_obj).length;

    append_table = generate_table_fastq(file_number)

    document.getElementById('metadata-table-div').appendChild(append_table);

    var create_button = document.createElement('button');
    create_button.classList.add('button-7');

    create_button.type = "button";
    create_button.id = "generate-metadata-sheet";
    create_button.onclick = function() {
      var experiment_name = document.getElementById('experiment-name').value;
      var file_list_obj = document.getElementById('input').files;
      var file_number = Object.keys(file_list_obj).length;

      var csv_string = "";
      var rows = document.getElementById("metadata_csv_table").rows;
      var header_row = rows[0];

      for (var i = 0; i < header_row.cells.length; i++) {
          csv_string = csv_string.concat(`${header_row.cells[i].innerHTML},`);
        }
      csv_string = csv_string.concat(`file_location,`);
      csv_string = csv_string.concat(`ont_type\n`);
      for (var i = 0; i < rows.length-1; i++) {
            for (var t = 0; t < rows[i].cells.length; t++) {
            var table_item = document.getElementById(`input${[i]}${[t]}`).value;
              if (t == 0) {
                csv_string = csv_string.concat(`${table_item},`);
                }
              else if (t == 1) {
                csv_string = csv_string.concat(`${table_item[0]},`);
              }
              else {
                csv_string = csv_string.concat(`${table_item},`);
              }
            }
            csv_string = csv_string.concat(`${file_list_obj[i].path},fastq\n`);

        }
      var current_moss_system = require('/opt/moss_db/config.json')["current_working_db"];
      var output_csv_file = `/opt/moss_db/${current_moss_system}/metadata_csv/${experiment_name}.csv`;
      //Here insert validation function for ENA compatability
      if (fs.existsSync(output_csv_file)) {
          // path exists
          alert("A file with this name already exists, please choose another one than: ", output_csv_file);
        } else {
            fs.writeFile(output_csv_file, csv_string, err => {
                  if (err) {
                    console.error(err)
                    return
                  }
                  alert(`The metadata csv file has been created and is stored at ${output_csv_file}`);
                  var create_button = document.createElement('button');
                  create_button.classList.add('button-7');
                  create_button.type = "button";
                  create_button.id = "go-to-analyses-button";
                  create_button.innerHTML = "Proceed to analyses";
                  create_button.onclick = function() {
                    location.href='./analyse.html';
                  }
                  create_button.style.width = "400px";
                  create_button.style.height = "150px";
                  create_button.style.fontSize = "large"

                  document.getElementById('metadata-table-div').appendChild(document.createElement('br'));
                  document.getElementById('metadata-table-div').appendChild(document.createElement('br'));

                  document.getElementById('metadata-table-div').appendChild(create_button);
                  //Make go to analyses shortcut
                })

            }
          }
    create_button.innerHTML = "Create metadata sheet for sequencing and analysis";
    var mybr = document.createElement('br');
    document.getElementById('metadata-table-div').appendChild(mybr);
    document.getElementById('metadata-table-div').appendChild(create_button);

}

function create_csv_from_obj(obj, experiment_name) {
    //check if experiment_name taken
    //if not {
    //  print obj to csv in /opt/moss_db/{current_dir}/metadata_csv/{experiment_name}.csv
}

function generate_table_fastq(file_number) {

    var file_list_obj = document.getElementById('input').files;


    var table = document.createElement('table');
    table.id = "metadata_csv_table";
    table.classList.add('table');

    var headRow = document.createElement('tr');
    headRow.id = "thead_tr";
    var columnNames = [];

    const jsonData= require('/opt/moss/datafiles/ena_list.json');
    const ena_keys = Object.keys(jsonData);
    columnNames.push.apply(columnNames, ena_keys)

    for (var i = 0; i < columnNames.length; i++) {
      var th = document.createElement('th');
      th.appendChild(document.createTextNode(columnNames[i].replace("_", " ")));
      headRow.appendChild(th);
    }

    table.appendChild(headRow);

    for (var i = 0; i < file_number; i++) {
      var tr = document.createElement('tr');
      tr.id = "tbody_tr_" + (i).toString();
      var sample_name = file_list_obj[i].path.split("/").slice(-1);

      for (var j = 0; j < columnNames.length; j++) {
        var identifier = jsonData[columnNames[j]];
        var td = document.createElement('td');
        td.style.textAlign = "center";
        td.id = `outer${i}${j}`;
        if (j > 0) {
            if (identifier=="free_text") {
                td.defaultValue = "";
                td.classList.add("input");
                var input = document.createElement('input');
                input.id = `input${i}${j}`;
                td.appendChild(input);
                tr.appendChild(td);
                continue;
            } else if (typeof identifier === "object") {
                td.defaultValue = "";
                td.classList.add("select");
                var input = document.createElement('select');
                input.id = `input${i}${j}`;
                var object_options = Object.values(identifier);
                for (var t = 0; t < object_options.length; t++) {
                    var option = document.createElement("option");
                    option.value = object_options[t];
                    option.text = object_options[t];
                    input.add(option);
                }
                input.defaultValue = object_options[0];
                td.appendChild(input);
                tr.appendChild(td);
                continue;
                }
            }
        else if (j == 0) {
            td.defaultValue = "";
            var label = document.createElement('label');
            label.id = `input${i}${j}`;
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

    //table.appendChild(thead);
    //table.appendChild(tbody);
    return table
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