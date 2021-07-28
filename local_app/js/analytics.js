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


function displayClusterSection() {
    document.getElementById("AMRtab").style.display = "none";
    document.getElementById("cluster-exploration-section").style.display = "block";
}



function showAMRtabs() {
        document.getElementById("AMRtab").style.display = "block";
        document.getElementById("cluster-exploration-section").style.display = "none";
}

function showamrgenetab(evt, cityName, sql) {
      var i, tabcontent, tablinks;
      tabcontent = document.getElementsByClassName("tabcontent");
      for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
      }
      tablinks = document.getElementsByClassName("tablinks");
      for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
      }
      document.getElementById(cityName).style.display = "block";
      evt.currentTarget.className += " active";

      var data_obj = search_db_query(sql);

      storage.get('currentConfig', function(error, data) {
                    if (error) throw error;

                    sql_data_query_table(data_obj, data, cityName);
                  });

    }



function sql_data_query_table(data_obj, data, divid) {
        var divShowData = document.getElementById('showData' + divid);
        divShowData.innerHTML = "";
        if (data_obj.length == 0) {
            var textmsg = document.createElement('p');
            textmsg.innerHTML = `No results found`;
            document.getElementById('search-area').append(textmsg);
        }

        var col = [];
        col.push('isolatename');
        col.push('timestamp');
        col.push('specie');
        col.push('amrgenes');
        col.push('risklevel');
        col.push('warning');
        col.push('entryid');

        // Create a table.
        var table = document.createElement("table");
        table.innerHTML = "";

        // CREATE HTML TABLE HEADER ROW USING THE EXTRACTED HEADERS ABOVE.

        var tr = table.insertRow(-1);                   // TABLE ROW.

        for (var i = 0; i < col.length; i++) {
            var th = document.createElement("th");      // TABLE HEADER.
            th.innerHTML = col[i];
            tr.appendChild(th);
        }

        // ADD JSON DATA TO THE TABLE AS ROWS.
        for (var i = 0; i < data_obj.length; i++) {

            tr = table.insertRow(-1);

            for (var j = 0; j < col.length; j++) {
                var tabCell = tr.insertCell(-1);
                tabCell.innerHTML = data_obj[i][col[j]];
            }
            var tabCell = tr.insertCell(-1);
            var img = document.createElement('img');
            img.isolatename = data_obj[i].isolatename;
            img.timestamp = data_obj[i].timestamp;
            img.specie = data_obj[i].specie;
            img.amrgenes = data_obj[i].amrgenes;
            img.risklevel = data_obj[i].risklevel;
            img.warning = data_obj[i].warning;
            img.entryid = data_obj[i].entryid;
            img.setAttribute('height', '17pt');
            img.innerHTML = data_obj[i].entryid;
            tabCell.appendChild(img);
        }

        divShowData.appendChild(table);
    }



function most_recent_isolates_table(data_obj, data) {
        var divShowData = document.getElementById('showData');
        divShowData.innerHTML = "";
        document.getElementById('search-area').innerHTML = "";


		var myObject = [];

        var col = [];
        col.push('entryid');
        col.push('isolatename');
        col.push('timestamp');
        col.push('risklevel');

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
        for (var i = 0; i < data_obj.length; i++) {

            tr = table.insertRow(-1);

            var tabCell = tr.insertCell(-1);
            tabCell.innerHTML = data_obj[i].isolatename;
            var tabCell = tr.insertCell(-1);
            tabCell.innerHTML = data_obj[i].timestamp;

            var tabCell = tr.insertCell(-1);
            var img = document.createElement('img');
            img.entryid = data_obj[i].entryid;
            img.isolatename = data_obj[i].isolatename;
            img.timestamp = data_obj[i].timestamp;
            img.risklevel = data_obj[i].risklevel;
            img.setAttribute('height', '17pt');
            img.innerHTML = data_obj[i].entryid;
            tabCell.appendChild(img);

        }
        divShowData.appendChild(table);

    }


function make_table_from_obj(obj) {
    document.getElementById('showData').innerHTML = "";
    document.getElementById('search-area').innerHTML = "";
    var k = '<tbody>'
    for(i = 0;i < obj.length; i++){
            k+= '<tr>';
            k+= '<td>' + obj[i].isolatename + '</td>';
            k+= '<td>' + obj[i].timestamp + '</td>';
            k+= '</tr>';
        }

        /* We add the table row to the table body */
        k+='</tbody>';
        document.getElementById('showData').innerHTML = k;
}

function search_db_query(sql) {
    let dbdir = document.getElementById('current-config').innerHTML
    const db = require('better-sqlite3')(dbdir + 'moss.db');
    const data_obj = db.prepare(sql).all();
    return data_obj
}