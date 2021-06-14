const { exec } = require('child_process');
const fs = require('fs');
const storage = require('electron-json-storage');

storage.get('currentConfig', function(error, data) {
  if (error) throw error;

  var element = document.getElementById('current-config');
  element.textContent = data.dbdir;
  var exe_path = data.exepath;
});


var configfile = "None";
document.getElementById("configfile").innerHTML = configfile;

function readSingleFile(e) {
    var file = e.target.files[0];
    if (!file) {
        return;
    }
    var reader = new FileReader();
    reader.onload = function(e) {
        var contents = e.target.result;
        displayContents(contents);
    };
    reader.readAsText(file);
}

function showFinishedAnalyses() {
    storage.get('currentConfig', function(error, data) {
      if (error) throw error;

      tableFromJson('finishedAnalyses.json', data);
    });
}

function showRunningAnalyses() {
    storage.get('currentConfig', function(error, data) {
          if (error) throw error;

          tableFromJson('runningAnalyses.json', 'none');
    });
}

function openPDF(id, data, myjson){
  console.log(data.dbdir + "analysis/" + document.getElementById(id).name + "/" + id + "_report.pdf");
  window.open(data.dbdir + "analysis/" + document.getElementById(id).name + "/" + id + "_report.pdf");
  //return false;
}


function tableFromJson(name, data) {
		// the json data. (you can change the values for output.)
		dbdir = document.getElementById('current-config').innerHTML;
		const myjson = require(dbdir + "/analyticalFiles/" + name);
		var myObjectlist = Object.values(myjson)

		var myObject = [];

		var arrayLength = myObjectlist.length;

		for (var i = 0; i < arrayLength; i++) {
                    const obj = JSON.parse(myObjectlist[i]);
                    myObject.push(obj);
                    //Do something
                }


		//var myObject = JSON.parse(myObject);

        //console.log(myObject);

        // Extract value from table header.
        // ('Book ID', 'Book Name', 'Category' and 'Price')
        var col = [];
        for (var i = 0; i < myObject.length; i++) {
            for (var key in myObject[i]) {
                if (col.indexOf(key) === -1) {
                    col.push(key);
                }
            }
        }

        // Create a table.
        var table = document.createElement("table");

        // Create table header row using the extracted headers above.
        var tr = table.insertRow(-1);                   // table row.

        for (var i = 0; i < col.length; i++) {
            var th = document.createElement("th");      // table header.
            th.innerHTML = col[i];
            tr.appendChild(th);
        }

        // add json data to the table as rows.
        for (var i = 0; i < myObject.length; i++) {

            tr = table.insertRow(-1);

            for (var j = 0; j < col.length; j++) {
                var tabCell = tr.insertCell(-1);
                tabCell.innerHTML = myObject[i][col[j]];
            }
            if (data != "none") {
                var tabCell = tr.insertCell(-1);
                var img = document.createElement('img');
                img.id = Object.keys(myjson)[i];
                img.name = myObject[i].name;
                img.src = data.exepath + "local_app/images/report-icon.png";
                img.setAttribute('height', '17pt');
                img.innerHTML = myObject[i].name;
                img.onclick = function() {openPDF(this.id, data, myjson)};
                //el.addEventListener("click", function(){
                //    openPDF(Object.keys(myjson)[i]));
                //});
                tabCell.appendChild(img);
            };


        }



        // Now, add the newly created table with json data, to a container.
        var divShowData = document.getElementById('showData');
        divShowData.innerHTML = "";
        divShowData.appendChild(table);

        /*
        if (data != "none") {
            for (var i = 0; i < myObject.length; i++) {
                //console.log(myObject[i].name);
                //console.log(myjson[Object.keys(myjson)[i]]);

                el = document.getElementById(Object.keys(myjson)[i]);
                el.addEventListener("click", function(){
                    openPDF(Object.keys(myjson)[i]));
                });

            }
        };*/
    }
