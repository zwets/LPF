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


function check(){
    console.log("check")
}

function generate_table(sequence_type, input_array) {

    if (sequence_type == 'pe_illumina') {
        var sorted_input_array = input_array.sort();
        var new_input_array = [];
        for (var i=0; i < sorted_input_array.length; i++) {
            if (i % 2 == 0) {
                new_input_array.push(`${sorted_input_array[i]} ${sorted_input_array[i+1]}`)

            }
        }
    } else {
        var new_input_array = input_array.sort();
    }

    var array_len = new_input_array.length;

    var table = document.createElement('table');
    table.classList.add('table');

    var thead = document.createElement('thead');
    var headRow = document.createElement('tr');
    var columnNames = ["Sample", "SeqType", "Use current IP location", "City", "Country"];

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


        //td.style.align-items = center;
        //td.style.border = "1px solid #000";
        //td.style.borderLeft = "1px solid #000"
        //td.style.borderRight = "1px solid #000"

        if (j >= 2) {
            if (j == 2) {
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
        if (j == 1) {
            td.appendChild(document.createTextNode(sequence_type));
            tr.appendChild(td);
        } else {
            td.appendChild(document.createTextNode(new_input_array[i]));
            tr.appendChild(td);
            }
      }


      tbody.appendChild(tr);
    }

    table.appendChild(thead);
    table.appendChild(tbody);
    return table
}


function create_metadata_table(){
    document.getElementById('metadata-table-div').innerHTML = "";
    //document.getElementById('analyse-multiple-index-file-section').innerHTML = "";

    var input = document.getElementById('multiple-input-field');
    var sequence_type = document.getElementById("multiple-input-type").value;

    var children = "";
    for (var i = 0; i < input.files.length; ++i) {
        children +=  input.files.item(i).path + ',';
     }
    var parallel_input = children.slice(0, -1);
    var input_array = parallel_input.split(",");


    append_table = generate_table(sequence_type, input_array)

    document.getElementById('metadata-table-div').appendChild(append_table);

    var create_button = document.createElement('button');

    create_button.type = "button";
    create_button.id = "generate-multiple-index-button";
    create_button.style.width = '225px'; // setting the width to 200px
    create_button.style.height = '20px'; // setting the height to 200px
    create_button.innerHTML = "Create multiple analysis index file"
    create_button.style.margin='0px 2px';



    document.getElementById('parameter-section').style.display = "block";
    document.getElementById('parallel-section').style.display = "none";



}


function geotooglefunc(){
    var checkstatus = this.checked;
}

function displayContents(contents) {
    var element = document.getElementById('file-content');
    element.textContent = contents;
    document.getElementById('moss-arguments').style.display = "block";
}

function singleInputFunction() {
    document.getElementById('single-input').style.display = "block";
    document.getElementById('multiple-input').style.display = "None";
    document.getElementById('parameter-section').style.display = "block";
}
function multipleInputFunction() {
    document.getElementById('multiple-input').style.display = "block";
    document.getElementById('single-input').style.display = "None";
    document.getElementById('parameter-section').style.display = "None";
    document.getElementById('analyse-multiple-index-file-section').style.display = "none";
    document.getElementById('generate-multiple-index-file-section').style.display = "none";
}

function submitMultiAnalysis() {

    var input = document.getElementById('multiple-input-field');
    var children = "";
        for (var i = 0; i < input.files.length; ++i) {
            children +=  input.files.item(i).path + ',';
         }
    var parallel_input = children.slice(0, -1);
    var input_array = parallel_input.split(",");


    var sequence_type = document.getElementById("multiple-input-type").value;
    var db_dir = document.getElementById('current-config').innerHTML;
    var exepath = document.getElementById('current-exepath').innerHTML;
    var srcpath = exepath + "src/";
    var threads = document.getElementById('threads').value;
    var jobs = document.getElementById('parallel-jobs').value;

    if (sequence_type == 'pe_illumina' && input_array.length%2 != 0) {
        alert("An odd number of sequences provided. For Illumina paired end analyses the number of sequences should be even!");
    } else {
        cmd_string = "";
        var sorted_input_array = input_array.sort();
        if (sequence_type == 'pe_illumina') {

            for (var i = 0; i < (sorted_input_array.length/2); ++i) {
                moss_string = `python3 ${srcpath}moss.py -seqType ${sequence_type} -thread ${threads} -db_dir ${db_dir} -exepath ${exepath}`;
                var checkstatus = document.getElementById(`input${i}2`).checked;
                if (checkstatus) {
                    moss_string = moss_string.concat(` -coordinates`);
                }

                var city_location = document.getElementById(`input${i}3`).value;
                var country_location = document.getElementById(`input${i}4`).value;
                var location = city_location + "," + country_location;

                if (location != ","){
                    moss_string = moss_string.concat(` -location ${location}`);
                }

                var pe_input = document.getElementById(`outer${i}0`).innerHTML;


                moss_string = moss_string.concat(` -i ${pe_input};`);

                cmd_string = cmd_string.concat(`${moss_string}`);

            }
        } else {
            for (var i = 0; i < (sorted_input_array.length); ++i) {
                moss_string = `python3 ${srcpath}moss.py -seqType ${sequence_type} -thread ${threads} -db_dir ${db_dir} -exepath ${exepath}`;
                var checkstatus = document.getElementById(`input${i}2`).checked;
                if (checkstatus) {
                    moss_string = moss_string.concat(` -coordinates`);
                }

                var city_location = document.getElementById(`input${i}3`).value;
                var country_location = document.getElementById(`input${i}4`).value;
                var location = city_location + "," + country_location;

                if (location != ","){
                    moss_string = moss_string.concat(` -location ${location}`);
                }

                var se_input = document.getElementById(`outer${i}0`).innerHTML;


                moss_string = moss_string.concat(` -i ${se_input};`);

                cmd_string = cmd_string.concat(`${moss_string}`);

            }

        }
    }
    var final_moss_string = cmd_string.slice(0, -1);

    parallel_wrapper_string = `python3 ${srcpath}moss_parallel_wrapper.py -i "${final_moss_string}" -jobs 1`;

    execute_command_as_subprocess(parallel_wrapper_string, srcpath, db_dir);


}


function submitSingleAnalysis() {

    var input = document.getElementById('single-input-field');
    var children = "";
        for (var i = 0; i < input.files.length; ++i) {
            children +=  input.files.item(i).path + ',';
         }
    var parallel_input = children.slice(0, -1);
    var input_array = parallel_input.split(",");


    var sequence_type = document.getElementById("single-input-type").value;
    var db_dir = document.getElementById('current-config').innerHTML;
    var exepath = document.getElementById('current-exepath').innerHTML;
    var srcpath = exepath + "src/";

    if (sequence_type == 'pe_illumina' && input_array.length != 2) {
        alert("A number other than 2 sequences were provided for paired end illumina analyses.");
    } else if ((sequence_type == 'se_illumina' || sequence_type == "nanopore") && input_array.length != 1) {
        console.log(input_array);
        console.log(input_array.length);
        alert("More than one file was given. For multiple file analyses, use the multiple analyses function, not the single analyses function.");
    } else {
                moss_string = `python3 ${srcpath}moss.py -seqType ${sequence_type} -thread 2 -db_dir ${db_dir} -exepath ${exepath}`;
                if (sequence_type == "pe_illumina") {
                    moss_string = moss_string.concat(` -i ${input_array[0]} ${input_array[1]}`);
                } else {
                    moss_string = moss_string.concat(` -i ${input_array[0]}`);
                }

                var checkstatus = document.getElementById('geotoggle').checked;

                if (checkstatus) {
                    moss_string = moss_string.concat(` -coordinates`);
                }

                var city_location = document.getElementById('City').value;
                var country_location = document.getElementById('Country').value;
                var location = city_location + "," + country_location;

                if (location != ","){
                    moss_string = moss_string.concat(` -location ${location}`);
                    }


                parallel_wrapper_string = `python3 ${srcpath}moss_parallel_wrapper.py -i "${moss_string}"`;


                execute_command_as_subprocess(parallel_wrapper_string, srcpath, db_dir);
    }

}

function execute_command_as_subprocess(cmd, srcpath, db_dir) {
    console.log(cmd);

    console.log("job submitted");

    alert("job submitted.");



    exec(cmd, (error, stdout, stderr) => {

        if (error) {
          console.error(`exec error: ${error}`);
          return;
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);

        outbreakfinderstring = `python3 ${srcpath}outbreak_finder.py -db_dir ${db_dir}`
        console.log(outbreakfinderstring);


        exec(outbreakfinderstring, (error, stdout, stderr) => {

            if (error) {
              //If error, change accepted ui to failure, which attached message.
              console.error(`exec error: ${error}`);
              return;
            }

            console.log(`stdout: ${stdout}`);
            console.error(`stderr: ${stderr}`);

            alert("Analysis complete!");



          });



      });
}

function submitAnalysis() {
    var sequence_type = document.getElementById("input-type").value;


    let nanopore_input = document.getElementById("nanopore-input").value;
    if (nanopore_input == "") {
        nanopore_input = "";
    } else {
        nanopore_input = document.getElementById("nanopore-input").files[0].path;
    }

    illumina_input_forward = document.getElementById("illumina-input-forward").value;
    if (illumina_input_forward == "") {
        illumina_input_forward = "";
    } else {
        illumina_input_forward = document.getElementById("illumina-input-forward").files[0].path;
    }

    illumina_input_reverse = document.getElementById("illumina-input-reverse").value;
    if (illumina_input_reverse == "") {
        illumina_input_reverse = "";
    } else {
        illumina_input_reverse = document.getElementById("illumina-input-reverse").files[0].path;
    }
    /*
    masking_scheme = document.getElementById("masking-scheme").value;
    if (masking_scheme == "") {
        masking_scheme = "";
    } else {
        masking_scheme = document.getElementById("masking-scheme").files[0].path;
    }*/

    //let prune_distance = document.getElementById("prune-distance").value;
    //let base_calling = document.getElementById("base-calling").value;
    let threads = document.getElementById("threads").value;

    var obj = new Object();
    obj.nanopore_input = nanopore_input;
    obj.illumina_input_forward  = illumina_input_forward;
    obj.illumina_input_reverse = illumina_input_reverse;
    obj.masking_scheme = "";
    obj.prune_distance = "10";
    obj.base_calling = "0.7";
    obj.threads = threads;
    obj.db_dir = document.getElementById('current-config').innerHTML;
    obj.exepath = document.getElementById('current-exepath').innerHTML;
    obj.srcpath = obj.exepath + "src/";

    var combinedilluminacheck = obj.illumina_input_forward + obj.illumina_input_reverse;

    if (combinedilluminacheck != "") {
        combinedillumina = obj.illumina_input_forward + " " + obj.illumina_input_reverse;
        moss_string = `python3 ${obj.srcpath}moss.py -i_illumina ${combinedillumina} -prune_distance ${obj.prune_distance} -bc ${obj.base_calling} -thread ${obj.threads} -db_dir ${obj.db_dir} -exepath ${obj.exepath}`;
    } else if (nanopore_input != "") {
        combinedillumina = combinedilluminacheck;
        moss_string = `python3 ${obj.srcpath}moss.py -i_nanopore ${obj.nanopore_input} -prune_distance ${obj.prune_distance} -bc ${obj.base_calling} -thread ${obj.threads} -db_dir ${obj.db_dir} -exepath ${obj.exepath}`;
    } else if (document.getElementById('multiple-input-field').value != "") {
        var input = document.getElementById('multiple-input-field');
        var children = "";
        for (var i = 0; i < input.files.length; ++i) {
            children +=  input.files.item(i).path + ',';
         }
        var parallel_input = children.slice(0, -1);
        var input_type = document.getElementById("input-type").value;
        var parallel_jobs = document.getElementById("parallel-jobs").value;
        moss_string = `python3 ${obj.srcpath}moss_parallel_wrapper.py -input_type ${input_type} -prune_distance ${obj.prune_distance} -bc ${obj.base_calling} -thread ${obj.threads} -db_dir ${obj.db_dir} -exepath ${obj.exepath} -parallel_input ${parallel_input} -jobs 1 -mac`;
    }

    if (obj.masking_scheme != ""){
        moss_string = moss_string.concat(`-masking_scheme ${obj.masking_scheme}`);
    }

    var checkstatus = document.getElementById('geotoggle').checked;

    if (checkstatus) {
        moss_string = moss_string.concat(` -coordinates`);
    }

    var city_location = document.getElementById('City').value;
    var country_location = document.getElementById('Country').value;
    var location = city_location + "," + country_location;

    if (location != ","){
        moss_string = moss_string.concat(` -location ${location}`);
    }

    console.log(moss_string);

    console.log("job submitted");

    //Her, skift UI til accepteret job

    //let output_path = obj.db_dir + "multiSampleAnalysisReports/" + obj.output_name + "/"

    alert("job submitted.");



    exec(moss_string, (error, stdout, stderr) => {

        if (error) {
          //If error, change accepted ui to failure, which attached message.
          //GIVE PROMPT
          console.error(`exec error: ${error}`);
          return;
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);
        /*
        fs.writeFile(output_path + 'stdout', stdout, (err) => {

            // In case of a error throw err.
            if (err) throw err;
        })
        fs.writeFile(output_path + 'stderr', stderr, (err) => {

            // In case of a error throw err.
            if (err) throw err;
        })
        */
        outbreakfinderstring = `python3 ${obj.srcpath}outbreak_finder.py -db_dir ${obj.db_dir}`
        console.log(outbreakfinderstring);


        exec(outbreakfinderstring, (error, stdout, stderr) => {

            if (error) {
              //If error, change accepted ui to failure, which attached message.
              console.error(`exec error: ${error}`);
              return;
            }

            console.log(`stdout: ${stdout}`);
            console.error(`stderr: ${stderr}`);



          });



      });


      //Make a return checker for a succesfull start

    //Submit Job

}

