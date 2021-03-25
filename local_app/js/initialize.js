const { exec } = require('child_process');


function getfolder(id) {
    var trypath = document.getElementById(id).files[0].path;
    var Folder = trypath.split("/");
    var returnstring = "";
    for (var i = 0; i < Object.keys(Folder).length - 1; i++ ) returnstring = returnstring + Folder[i] + "/";
    return returnstring;
  }

function submitInitilization() {
  var init_path = document.getElementById("init-path").value;
  var config_name = document.getElementById("config-name").value;
  var exe_path = getfolder("exe-path");


  var input_fasta = document.getElementById("input-fasta").value;
  if (input_fasta == "") {
    input_fasta = "";
  } else {
    var input_fasta = getfolder("input-fasta");
  }

  var kmaindex_path = document.getElementById("kmaindex-path").value;
  if (kmaindex_path == "") {
    kmaindex_path = "";
  } else {
    var kmaindex_path = getfolder("kmaindex-path");
  }

  var execstring = `python3 ${exe_path}prtt_init.py -db_dir ${init_path} -exepath ${exe_path} -configname ${config_name}`




  if (input_fasta != ""){
    execstring = execstring.concat(` -input_path_fasta ${input_fasta}`);
    }

  if (kmaindex_path != ""){
    execstring = execstring.concat(` -kmaindex_db_path ${kmaindex_path}`);
    }

  console.log(execstring);


  console.log("job submitted");

  alert("job submitted, you will be redirected to Home.");

  location.href = "./index.html";

  //Auto initialization of config!
  //Loader whilst initializing perhaps?

  exec(execstring, (error, stdout, stderr) => {



    if (error) {
      //If error, change accepted ui to failure, which attached message.
      console.error(`exec error: ${error}`);
      alert(`exec error: ${error}`);
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





      }); 

    }


