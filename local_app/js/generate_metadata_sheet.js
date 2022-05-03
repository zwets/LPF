const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');
var mkdirp = require('mkdirp');

function execute_command_as_subprocess(cmd, start_msg, end_msg, fail_msg) {
    console.log(cmd);

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

function create_metadata_table_fast5(){

    document.getElementById('metadata-table-div').innerHTML = "";
    //document.getElementById('analyse-multiple-index-file-section').innerHTML = "";

    var input = document.getElementById('multiple-input-type').value;
    var input_number = parseInt(input);

    var children = "";
    for (var i = 0; i < input_number; ++i) {
        if (i >= 9) {
            children +=  (i+1).toString() + ',';
        } else {
            children +=  "0" + (i+1).toString() + ',';
        }
     }
    var parallel_input = children.slice(0, -1);
    var input_array = parallel_input.split(",");


    append_table = generate_table_fast5(input_array)

    document.getElementById('metadata-table-div').appendChild(append_table);

    var create_button = document.createElement('button');
    create_button.classList.add('button-7');

    create_button.type = "button";
    create_button.id = "generate-metadata-sheet";
    create_button.onclick = function() {
      var experiment_name = document.getElementById('experiment-name').value;
      var input = document.getElementById('multiple-input-type').value;
      var input_number = parseInt(input);

      var csv_string = "";
      var rows = document.getElementById("metadata_csv_table").rows;
      var header_row = rows[0];

      for (var i = 0; i < header_row.cells.length; i++) {
          csv_string = csv_string.concat(`${header_row.cells[i].innerHTML},`);
        }
      csv_string = csv_string.concat(`file_location,`);
      csv_string = csv_string.concat(`ont_type\n`);

      var bc_folder = document.getElementById('barcode-folder');
      var bc_folder_path = bc_folder.files.item(0).path;
      var path_list = bc_folder_path.split("/");
      var path_slice= path_list.slice(1, -1);
      var bc_final_path = "/" + path_slice.join("/") + "/";
      for (var i = 0; i < rows.length; i++) {
          if (i>0) {
            for (var t = 0; t < rows[i].cells.length; t++) {
              csv_string = csv_string.concat(`${rows[i].cells[t].value},`);
              }
            csv_string = csv_string.concat(`${bc_final_path},fast5\n`);
          }
        }

      var current_moss_system = require('/opt/moss_db/config.json')["current_working_db"];
      var output_csv_file = `/opt/moss_db/${current_moss_system}/metadata_csv/${experiment_name}.csv`;
      //Here insert validation function for ENA compatability
      if (fs.existsSync(output_csv_file)) {
          // path exists
          alert("A file with this name already exists, please choose another one than: ", output_csv_file);
            }
        else {

          fs.writeFile(output_csv_file, csv_string, err => {
              if (err) {
                console.error(err)
                return
              }
              alert(`The metadata csv file has been created and is stored at ${output_csv_file}`);
            })

        }
       }
    create_button.innerHTML = "Create metadata sheet and begin automated basecalling";
    var mybr = document.createElement('br');
    document.getElementById('metadata-table-div').appendChild(mybr);
    document.getElementById('metadata-table-div').appendChild(create_button);

}


function create_metadata_table_fastq(){

    document.getElementById('metadata-table-div').innerHTML = "";

    var input = document.getElementById('multiple-input-type').value;
    var input_number = parseInt(input);


    append_table = generate_table_fastq(input_number)

    document.getElementById('metadata-table-div').appendChild(append_table);

    var create_button = document.createElement('button');
    create_button.classList.add('button-7');

    create_button.type = "button";
    create_button.id = "generate-metadata-sheet";
    create_button.onclick = function() {
      var experiment_name = document.getElementById('experiment-name').value;
      var input = document.getElementById('multiple-input-type').value;
      var input_number = parseInt(input);

      var csv_string = "";
      var rows = document.getElementById("metadata_csv_table").rows;
      var header_row = rows[0];

      for (var i = 0; i < header_row.cells.length; i++) {
          csv_string = csv_string.concat(`${header_row.cells[i].innerHTML},`);
        }
      csv_string = csv_string.concat(`file_location,`);
      csv_string = csv_string.concat(`ont_type\n`);

      var bc_folder = document.getElementById('fastq-folder');
      var bc_folder_path = bc_folder.files.item(0).path;
      var path_list = bc_folder_path.split("/");
      var path_slice= path_list.slice(1, -1);
      var bc_final_path = "/" + path_slice.join("/") + "/";
      var barcode_list = [];

      for (var i = 0; i < rows.length; i++) {
            for (var t = 0; t < rows[i].cells.length; t++) {
            console.log(document.getElementById(`input${[i]}${[t]}`.value);
              if (t == 0) {
                barcode_list.push(rows[i].cells[t].value);
              }
              csv_string = csv_string.concat(`${rows[i].cells[t].value},`);
              }
            csv_string = csv_string.concat(`${bc_final_path},fastq\n`);

        }
      console.log(barcode_list);
      var current_moss_system = require('/opt/moss_db/config.json')["current_working_db"];
      var output_csv_file = `/opt/moss_db/${current_moss_system}/metadata_csv/${experiment_name}.csv`;
      //Here insert validation function for ENA compatability
      if (fs.existsSync(output_csv_file)) {
          // path exists
          alert("A file with this name already exists, please choose another one than: ", output_csv_file);
        } else {
          //check barcodes

          fs.writeFile(output_csv_file, csv_string, err => {
              if (err) {
                console.error(err)
                return
              }
              alert(`The metadata csv file has been created and is stored at ${output_csv_file}`);
              //file written successfully
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

function generate_table_fastq(input_number) {

    var table = document.createElement('table');
    table.id = "metadata_csv_table";
    table.classList.add('table');

    var bc_folder = document.getElementById('fastq-folder');

    var headRow = document.createElement('tr');
    headRow.id = "thead_tr";
    var columnNames = ["barcode number"];

    const jsonData= require('/opt/moss/datafiles/ena_list.json');
    const ena_keys = Object.keys(jsonData);
    columnNames.push.apply(columnNames, ena_keys)

    for (var i = 0; i < columnNames.length; i++) {
      var th = document.createElement('th');
      th.appendChild(document.createTextNode(columnNames[i].replace("_", " ")));
      headRow.appendChild(th);
    }

    table.appendChild(headRow);

    for (var i = 0; i < input_number; i++) {
      var tr = document.createElement('tr');
      tr.id = "tbody_tr_" + (i).toString();
      var sample_name = bc_folder.files.item(i).path.split("/").slice(-1);

      for (var j = 0; j < columnNames.length; j++) {
        var identifier = jsonData[columnNames[j]];
        var td = document.createElement('td');
        td.style.textAlign = "center";
        td.id = `outer${i}${j}`;
        if (j > 1) {
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
        else if (j == 1) {
            td.defaultValue = "";
            var label = document.createElement('label');
            label.id = `input${i}${j}`;
            label.innerHTML = sample_name;
            label.value = sample_name;
            td.appendChild(label);
            tr.appendChild(td);
            continue;
        }
        else {
            td.defaultValue = "";
            td.classList.add("select");
            var input = document.createElement('select');
            input.id = `input${i}${j}`;
            var object_options = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
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
        //td.appendChild(document.createTextNode(new_input_array[i]));
        tr.appendChild(td);
      }


      table.appendChild(tr);
    }

    //table.appendChild(thead);
    //table.appendChild(tbody);
    return table
}

function generate_table_fast5(input_array) {

    var new_input_array = input_array.sort();

    var array_len = new_input_array.length;

    var table = document.createElement('table');
    table.id = "metadata_csv_table";
    table.classList.add('table');

    var headRow = document.createElement('tr');
    headRow.id = "thead_tr";
    var columnNames = ["barcode number"];

    const jsonData= require('/opt/moss/datafiles/ena_list.json');
    const ena_keys = Object.keys(jsonData);
    columnNames.push.apply(columnNames, ena_keys)

    for (var i = 0; i < columnNames.length; i++) {
      var th = document.createElement('th');
      th.appendChild(document.createTextNode(columnNames[i].replace("_", " ")));
      headRow.appendChild(th);
    }

    table.appendChild(headRow);

    //var tbody = document.createElement('tbody');
    //tbody.id = "tbody";

    for (var i = 0; i < array_len; i++) {
      var tr = document.createElement('tr');
      tr.id = "tbody_tr_" + (i).toString();

      for (var j = 0; j < columnNames.length; j++) {
        var identifier = jsonData[columnNames[j]];
        var td = document.createElement('td');
        td.style.textAlign = "center";
        td.id = `outer${i}${j}`;
        if (j >= 1) {
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
                td.appendChild(input);
                tr.appendChild(td);
                continue;
            }

        }
        td.appendChild(document.createTextNode(new_input_array[i]));
        tr.appendChild(td);
      }


      table.appendChild(tr);
    }

    //table.appendChild(thead);
    //table.appendChild(tbody);
    return table
}




function find_model_from_input(flowcell, kit, db_dir, algorithm){
    var model = "";
    var database_system = require('/opt/moss_db/config.json').current_working_db;
    const data = require("/opt/moss_db/" + database_system +"/static_files/workflow.json");
    for (var i = 0; i < data.length; i++) {
                if (data[i].flowcell == flowcell) {
                    if (data[i].kit == kit) {
                        model = data[i].barcoding_config_name;
                        model = model.concat(algorithm);
                        return model;
                        //document.getElementById('running_model').innerHTML = model;
                    };
                };
            }
}


function fetch_guppy_data(){
    var db_dir = document.getElementById('current-config').innerHTML;
    var database_system = require('/opt/moss_db/config.json').current_working_db;
    readTextFile("/opt/moss_db/" + database_system +"/static_files/workflow.json", function(text){
        var data = JSON.parse(text);
        document.getElementById('workflowjson').innerHTML = data;

        var items = data;

        var result_flowcell = [];
        var result_kit = [];
        var result_barcoding_config_name = [];
        var result_model_version = [];

        for (var item, i = 0; item = items[i++];) {
          var flowcell = item.flowcell;
          var kit = item.kit;
          var barcoding_config_name = item.barcoding_config_name;
          var model_version = item.model_version;
          result_flowcell.push(flowcell);
          result_kit.push(kit);
          result_barcoding_config_name.push(barcoding_config_name);
          result_model_version.push(model_version);
        }

        const unique_flowcell = [...new Set(result_flowcell)];
        const unique_kit = [...new Set(result_kit)];
        const unique_barcoding_config_name = [...new Set(result_barcoding_config_name)];
        const unique_model_version = [...new Set(result_model_version)];

        var select = document.getElementById("flow-cell");
        //var unames = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"];
        for (var i = 0; i < unique_flowcell.length; i++) {
            var opt = unique_flowcell[i];
            var el = document.createElement("option");
            el.textContent = opt;
            el.value = opt;
            select.appendChild(el);
          }

        var select = document.getElementById("kit");
        //var unames = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"];
        for (var i = 0; i < unique_kit.length; i++) {
            var opt = unique_kit[i];
            var el = document.createElement("option");
            el.textContent = opt;
            el.value = opt;
            select.appendChild(el);
          }

        var select = document.getElementById("barcoding_config_name");
        for (var i = 0; i < unique_barcoding_config_name.length; i++) {
            var opt = unique_barcoding_config_name[i];
            var el = document.createElement("option");
            el.textContent = opt;
            el.value = opt;
            select.appendChild(el);
          }

        var select = document.getElementById("model_version");
        for (var i = 0; i < unique_model_version.length; i++) {
            var opt = unique_model_version[i];
            var el = document.createElement("option");
            el.textContent = opt;
            el.value = opt;
            select.appendChild(el);
          }

    });


    readTextFile("/opt/moss_db/" + database_system +"/static_files/barcodes.json", function(text){
        var data = JSON.parse(text);
        var items = data;

        var result_barcode = [];

        for (var item, i = 0; item = items[i++];) {
          var barcode = item.barcode;
          result_barcode.push(barcode);
        }

        const unique_barcode = [...new Set(result_barcode)];

        var select = document.getElementById("demux");
        var opt = "No multiplexing";
        var el = document.createElement("option");
        el.textContent = opt;
        el.value = opt;
        select.appendChild(el);
        //var unames = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"];
        for (var i = 0; i < unique_barcode.length; i++) {
            var opt = unique_barcode[i];
            var el = document.createElement("option");
            el.textContent = opt;
            el.value = opt;
            select.appendChild(el);
          }

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