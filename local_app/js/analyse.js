const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');

storage.get('currentConfig', function(error, data) {
  if (error) throw error;

  var element = document.getElementById('current-config');
  element.textContent = data.dbdir;
  var element = document.getElementById('current-exepath');
  element.textContent = data.exepath;

});

function check(){
    console.log("check")
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
    document.getElementById('parameter-section').style.display = "block";
}



function submitAnalysis() {
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
    let output_name = document.getElementById("output-name").value;

    var obj = new Object();
    obj.nanopore_input = nanopore_input;
    obj.illumina_input_forward  = illumina_input_forward;
    obj.illumina_input_reverse = illumina_input_reverse;
    obj.masking_scheme = "";
    obj.prune_distance = "10";
    obj.base_calling = "0.7";
    obj.threads = threads;
    obj.output_name = output_name;
    obj.dbdir = document.getElementById('current-config').innerHTML;
    obj.exepath = document.getElementById('current-exepath').innerHTML;
    obj.srcpath = obj.exepath + "src/";

    var combinedilluminacheck = obj.illumina_input_forward + obj.illumina_input_reverse;

    if (combinedilluminacheck != "") {
        combinedillumina = obj.illumina_input_forward + " " + obj.illumina_input_reverse;
        moss_string = `python3 ${obj.srcpath}moss.py -i_illumina ${combinedillumina} -prune_distance ${obj.prune_distance} -bc ${obj.base_calling} -thread ${obj.threads} -db_dir ${obj.dbdir} -o ${obj.output_name} -exepath ${obj.exepath}`;
    } else if (nanopore_input != "") {
        combinedillumina = combinedilluminacheck;
        moss_string = `python3 ${obj.srcpath}moss.py -i_nanopore ${obj.nanopore_input} -prune_distance ${obj.prune_distance} -bc ${obj.base_calling} -thread ${obj.threads} -db_dir ${obj.dbdir} -o ${obj.output_name} -exepath ${obj.exepath}`;
    } else if (document.getElementById('multiple-input-field').value != "") {
        var input = document.getElementById('multiple-input-field');
        var children = "";
        for (var i = 0; i < input.files.length; ++i) {
            children +=  input.files.item(i).path + ',';
         }
        var parallel_input = children.slice(0, -1);
        var input_type = document.getElementById("input-type").value;
        var parallel_jobs = document.getElementById("parallel-jobs").value;
        moss_string = `python3 ${obj.srcpath}moss_parallel_wrapper.py -input_type ${input_type} -prune_distance ${obj.prune_distance} -bc ${obj.base_calling} -thread ${obj.threads} -db_dir ${obj.dbdir} -o ${obj.output_name} -exepath ${obj.exepath} -parallel_input ${parallel_input} -jobs ${parallel_jobs}`;
    }

    if (obj.masking_scheme != ""){
        moss_string = moss_string.concat(`-masking_scheme ${obj.masking_scheme}`);
    }

    console.log(moss_string);

    console.log("job submitted");

    //Her, skift UI til accepteret job

    let output_path = obj.dbdir + "multiSampleAnalysisReports/" + obj.output_name + "/"

    alert("job submitted.");



    exec(moss_string, (error, stdout, stderr) => {

        if (error) {
          //If error, change accepted ui to failure, which attached message.
          console.error(`exec error: ${error}`);
          return;
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);
        fs.writeFile(output_path + 'stdout', stdout, (err) => { 
      
            // In case of a error throw err. 
            if (err) throw err; 
        }) 
        fs.writeFile(output_path + 'stderr', stderr, (err) => { 
      
            // In case of a error throw err. 
            if (err) throw err; 
        }) 

        outbreakfinderstring = `python3 ${obj.srcpath}outbreak_finder.py -db_dir ${obj.dbdir}`
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

