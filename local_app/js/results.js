const { exec } = require('child_process');
const fs = require('fs');
const Dialogs = require("dialogs");

var intervalId = window.setInterval(function(){
    showFinishedAnalyses();
  // call your function here
}, 2000);

function showFinishedAnalyses() {
    let sql = `SELECT * FROM status_table ORDER BY time_stamp DESC`;
    document.getElementById('showData').innerHTML="" ;
    const db = require('better-sqlite3')('/opt/LPF_databases/LPF.db');
    const sql_data_obj = db.prepare(sql).all();

    tableFromObj(sql_data_obj);

}

function openPDF(id){
  console.log("/opt/LPF_analyses/" + id + "/" + id + ".pdf");
  window.open("/opt/LPF_analyses/" + id + "/" + id + ".pdf");
  //return false;
}

function open_log_file(id){
    console.log("/opt/LPF_logs/" + id + ".log");
    window.open("/opt/LPF_logs/" + id + ".log");
    //return false;
}


function tableFromObj(sql_data_obj) {
        var divShowData = document.getElementById('showData');
        divShowData.innerHTML = "";

        // ('Book ID', 'Book Name', 'Category' and 'Price')
        var col = [];
        for (var i = 0; i < sql_data_obj.length; i++) {
            for (var key in sql_data_obj[i]) {
                if (col.indexOf(key) === -1) {
                    col.push(key);
                }
            }
        }

        col.push("PDF Report");
        col.push("Log File");
        col.push("Delete Entry");

        // Create a table.
        var table = document.createElement("table");
        table.innerHTML = "";

        // Create table header row using the extracted headers above.
        var tr = table.insertRow(-1);                   // table row.

        for (var i = 0; i < col.length; i++) {
            var th = document.createElement("th");      // table header.
            th.innerHTML = col[i];
            tr.appendChild(th);
        }

        // add json data to the table as rows.
        for (var i = 0; i < sql_data_obj.length; i++) {

            tr = table.insertRow(-1);

            for (var j = 0; j < col.length; j++) {
                if (col[j] == "PDF Report") {
                    var tabCell = tr.insertCell(-1);
                    tabCell.style.alignContent = "center";
                    var img = document.createElement('img');
                    img.style.alignContent = "center";
                    img.id = sql_data_obj[i].entry_id;
                    img.name = sql_data_obj[i].entry_id;
                    img.src = "/opt/LPF/local_app/images/report-icon.png";
                    img.setAttribute('height', '17pt');
                    img.innerHTML = sql_data_obj[i].entry_id;
                    img.onclick = function() {openPDF(this.id)};
                    tabCell.appendChild(img);
                }
                else if (col[j] == "Log File") {
                    var tabCell = tr.insertCell(-1);
                    tabCell.style.alignContent = "center";
                    var img = document.createElement('img');
                    img.style.alignContent = "center";
                    img.id = sql_data_obj[i].entry_id;
                    img.name = sql_data_obj[i].entry_id;
                    img.src = "/opt/LPF/local_app/images/log-icon.png";
                    img.setAttribute('height', '17pt');
                    img.innerHTML = sql_data_obj[i].entry_id;
                    img.onclick = function() {open_log_file(this.id)};
                    tabCell.appendChild(img);
                }
                else if (col[j] == "Delete Entry") {
                    var tabCell = tr.insertCell(-1);
                    tabCell.style.alignContent = "center";
                    var img = document.createElement('img');
                    img.style.alignContent = "center";
                    img.id = sql_data_obj[i].entry_id;
                    img.name = sql_data_obj[i].entry_id;
                    img.src = "/opt/LPF/local_app/images/icons8-cross-mark-button-96.png";
                    img.setAttribute('height', '17pt');
                    img.innerHTML = sql_data_obj[i].entry_id;
                    img.onclick = function() {delete_entry(this.id)};
                    tabCell.appendChild(img);
                }
                else {
                    var tabCell = tr.insertCell(-1);
                    tabCell.innerHTML = sql_data_obj[i][col[j]];
                }
            }
        }



        // Now, add the newly created table with json data, to a container.
        divShowData.appendChild(table);
    }

function delete_entry(id){
    const Dialogs = require('dialogs')
    const dialogs = Dialogs()
    dialogs.prompt('Write DELETE to delete the analysis entry:', result => {
        if (result == "DELETE") {
            console.log("Deleting entry");
            cmd = 'python3 /opt/LPF/scripts/removeFromDatabase.py -i ' + id;
            console.log(cmd);
            exec(cmd,
            function (error, stdout, stderr) {
                console.log('stdout: ' + stdout);
                console.log('stderr: ' + stderr);
                if (error !== null) {
                     console.log('exec error: ' + error);
                }
            });
       }
       else {
            console.log("Not deleting entry");
       }
       showFinishedAnalyses();
    })
}