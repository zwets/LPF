const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');
var mkdirp = require('mkdirp');


function create_metadata_table(){
    document.getElementById('metadata-table-div').innerHTML = "";
    //document.getElementById('analyse-multiple-index-file-section').innerHTML = "";

    var input = document.getElementById('multiple-input-type').value;
    var input_number = parseInt(input);

    var children = "";
    for (var i = 0; i < input_number; ++i) {
        children +=  "test" + ',';
     }
    var parallel_input = children.slice(0, -1);
    var input_array = parallel_input.split(",");


    append_table = generate_table(input_array)

    document.getElementById('metadata-table-div').appendChild(append_table);

    var create_button = document.createElement('button');

    create_button.type = "button";
    create_button.id = "generate-multiple-index-button";
    create_button.style.width = '225px'; // setting the width to 200px
    create_button.style.height = '20px'; // setting the height to 200px
    create_button.innerHTML = "Create multiple analysis index file"
    create_button.style.margin='0px 2px';



    document.getElementById('parameter-section').style.display = "block";
    document.getElementById('parallel-section').style.display = "block";



}


function generate_table(input_array) {

    console.log(input_array);

    var new_input_array = input_array.sort();

    var array_len = new_input_array.length;

    var table = document.createElement('table');
    table.classList.add('table');

    var thead = document.createElement('thead');
    var headRow = document.createElement('tr');
    var columnNames = ["Barcode number"];

    for (var i = 0; i < 5; i++) {
      var th = document.createElement('th');
      //th.style.borderLeft = "1px solid #000"
      //th.style.borderRight = "1px solid #000"
      th.appendChild(document.createTextNode(columnNames[i]));
      headRow.appendChild(th);
    }

    thead.appendChild(headRow);

    var tbody = document.createElement('tbody');

    for (var i = 0; i < array_len; i++) {
      var tr = document.createElement('tr');

      for (var j = 0; j < 5; j++) {
        var td = document.createElement('td');
        td.style.textAlign = "center";
        td.id = `outer${i}${j}`;

        if (j >= 1) {
            if (j == 1) {
                td.classList.add("input");
                var input = document.createElement('input');
                input.type = "checkbox";
                input.id = `input${i}${j}`;
                td.appendChild(input);
                tr.appendChild(td);
                continue;
              } else {
                td.defaultValue = "";
                td.classList.add("input");
                var input = document.createElement('input');
                input.id = `input${i}${j}`;
                td.appendChild(input);
                tr.appendChild(td);
                continue;
              }

        }
        td.appendChild(document.createTextNode(new_input_array[i]));
        tr.appendChild(td);
      }


      tbody.appendChild(tr);
    }

    table.appendChild(thead);
    table.appendChild(tbody);
    return table
}




function find_model_from_input(flowcell, kit, db_dir, algorithm){
    var model = "";
    const data = require("/opt/moss_db/" + "test1" +"/static_files/workflow.json");
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

    readTextFile("/opt/moss_db/" + "test1" +"/static_files/workflow.json", function(text){
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




    readTextFile("/opt/moss_db/" + "test1" +"/static_files/barcodes.json", function(text){
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