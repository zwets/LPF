const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');

function getfolder(id) {
    var trypath = document.getElementById(id).files[0].path;
    var Folder = trypath.split("/");
    var returnstring = "";
    for (var i = 0; i < Object.keys(Folder).length - 1; i++ ) returnstring = returnstring + Folder[i] + "/";
    return returnstring;
  }


function submitinit() {
  var init_path = document.getElementById("init-path").value;
  var config_name = document.getElementById("config-name").value;
  var exepath = getfolder("exe-path");

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

  var execstring = `python3 ${exepath}src/moss_init.py -db_dir ${init_path} -exepath ${exepath} -configname ${config_name}`
  console.log(execstring);



  if (input_fasta != ""){
    execstring = execstring.concat(` -input_path_fasta ${input_fasta}`);
    }

  if (kmaindex_path != ""){
    execstring = execstring.concat(` -kmaindex_db_path ${kmaindex_path}`);
    }

  console.log(execstring);


  //console.log("job submitted");

  //alert("job submitted.");

  //location.href = "./index.html";

  //Auto initialization of config!
  //Loader whilst initializing perhaps?
  var loader = document.getElementById('loader');
  loader.style.display = 'block';
  document.getElementById('loadermessage').innerHTML = "Setting up database system. Depending on the database size, this might take some time (>20 min).";

  exec(execstring, (error, stdout, stderr) => {



    if (error) {
      //If error, change accepted ui to failure, which attached message.
      console.error(`exec error: ${error}`);
      alert(`exec error: ${error}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);

    //Automatic change of correct system config to
    console.log(exepath)
    console.log(init_path)
    storage.set('currentConfig', { exepath: exepath, dbdir: init_path }, function(error) {
            if (error) throw error;
        });
    alert("Your database has been set up!");

    loader.style.display = 'none';
    document.getElementById('loadermessage').innerHTML = "Your database system has been set up.";



      });


  }


