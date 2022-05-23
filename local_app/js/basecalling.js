const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');
var mkdirp = require('mkdirp');

function fetch_guppy_data(){

    var current_moss_system = require('/opt/moss_db/config.json')["current_working_db"] + "/";

    readTextFile("/opt/moss_db/" + current_moss_system + "static_files/workflow.json", function(text){
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




    readTextFile("/opt/moss_db/" + current_moss_system + "static_files/barcodes.json", function(text){
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

function find_model_from_input(flowcell, kit, algorithm){
    var model = "";
    const data = require("/opt/moss_db/" + current_moss_system + "static_files/workflow.json");
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

function start_base_calling(){

    var flowcell = document.getElementById('flow-cell').value;
    var kit = document.getElementById('kit').value;
    var barcoding_config_name = document.getElementById('barcoding_config_name').value;
    var barcodes = document.getElementById('demux').value;
    var model_version = document.getElementById('model_version').value;
    var algorithm = document.getElementById('algorithm').value;
    var input = document.getElementById('fast5-input-field');
    var output_name = document.getElementById('output-field').value;

    var single_path = input.files.item(0).path;
    var path_list = single_path.split("/");
    var path_slice= path_list.slice(1, -1);
    var input_path = "/" + path_slice.join("/") + "/";



    var check_basecall_name = false;
    if (fs.existsSync("/opt/moss_data/fast5/" + output_name)) {
        alert("A experiment name has already been used. Please choose another one.");
    } else {
        check_basecall_name = true;
    }

    if (check_basecall_name) {
        cmd = `conda run -n base python3 /opt/moss/src/run_guppy.py -i ${input_path} -n ${output_name}`

        var model = find_model_from_input(flowcell, kit, algorithm);
        cmd = cmd.concat(` -c ${model}`)
        console.log(cmd);

        //if (fs.existsSync(output_name)) {
        var loader = document.getElementById('loader');
        loader.style.display = 'block';
        document.getElementById('loadermessage').innerHTML = "Basecalling is running";

        console.log("Base calling has begun.");


        if (algorithm == "_sup.cfg") {
            cmd = cmd.concat(` -chunks 75`)
        }

        if (barcodes != "No multiplexing") {
            cmd = cmd.concat(` -bk \"${barcodes}\"`)
            }

        console.log(cmd)
        exec(cmd, (error, stdout, stderr) => {

            if (error) {
                alert(`exec error: ${error}`);
                document.getElementById('loadermessage').innerHTML = `Basecalling has failed: ${error}`;
                loader.style.display = 'none';
              console.error(`exec error: ${error}`);
              return;
            } else {
                alert("Base calling has completed.");
                document.getElementById('loadermessage').innerHTML = `Basecalling has been completed: ${stdout}`;
                loader.style.display = 'none';
            }


        });

        //} else {
        //    alert("The given output directory does not exist");
        //}

    }
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