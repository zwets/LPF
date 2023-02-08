const { exec } = require('child_process');
const fs = require('fs');

function showFinishedAnalyses() {
    let sql = `SELECT * FROM status_table`;
    document.getElementById('showData').innerHTML="" ;
    const db = require('better-sqlite3')('/opt/LPF_databases/LPF.db');
    const sql_data_obj = db.prepare(sql).all();
    console.log(sql_data_obj);

    tableFromObj(sql_data_obj);

}

function openPDF(id){
  console.log("/opt/LPF_analyses/" + id + "/" + id + ".pdf");
  window.open("/opt/LPF_analyses/" + id + "/" + id + ".pdf");
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
                var tabCell = tr.insertCell(-1);
                tabCell.innerHTML = sql_data_obj[i][col[j]];
            }
            if (sql_data_obj != "none") {
                var tabCell = tr.insertCell(-1);
                var img = document.createElement('img');
                img.id = sql_data_obj[i].entry_id;
                img.name = sql_data_obj[i].entry_id;
                img.src = "/opt/LPF/local_app/images/report-icon.png";
                img.setAttribute('height', '17pt');
                img.innerHTML = sql_data_obj[i].entry_id;
                img.onclick = function() {openPDF(this.id)};
                tabCell.appendChild(img);
            };


        }



        // Now, add the newly created table with json data, to a container.
        divShowData.appendChild(table);
    }
