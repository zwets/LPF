const { exec } = require('child_process');
const fs = require('fs');
const storage = require('electron-json-storage');

storage.get('currentConfig', function(error, data) {
  if (error) throw error;

  var element = document.getElementById('current-config');
  element.textContent = data.db_dir;
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
        col.push('sample_name');
        col.push('analysistimestamp');
        col.push('specie');
        col.push('amrgenes');
        col.push('risklevel');
        col.push('warning');
        col.push('entry_id');

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
            img.sample_name = data_obj[i].sample_name;
            img.analysistimestamp = data_obj[i].analysistimestamp;
            img.specie = data_obj[i].specie;
            img.amrgenes = data_obj[i].amrgenes;
            img.risklevel = data_obj[i].risklevel;
            img.warning = data_obj[i].warning;
            img.entry_id = data_obj[i].entry_id;
            img.setAttribute('height', '17pt');
            img.innerHTML = data_obj[i].entry_id;
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
        col.push('entry_id');
        col.push('sample_name');
        col.push('analysistimestamp');
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
            tabCell.innerHTML = data_obj[i].sample_name;
            var tabCell = tr.insertCell(-1);
            tabCell.innerHTML = data_obj[i].analysistimestamp;

            var tabCell = tr.insertCell(-1);
            var img = document.createElement('img');
            img.entry_id = data_obj[i].entry_id;
            img.sample_name = data_obj[i].sample_name;
            img.analysistimestamp = data_obj[i].analysistimestamp;
            img.risklevel = data_obj[i].risklevel;
            img.setAttribute('height', '17pt');
            img.innerHTML = data_obj[i].entry_id;
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
            k+= '<td>' + obj[i].sample_name + '</td>';
            k+= '<td>' + obj[i].analysistimestamp + '</td>';
            k+= '</tr>';
        }

        /* We add the table row to the table body */
        k+='</tbody>';
        document.getElementById('showData').innerHTML = k;
}

function search_db_query(sql) {
    let db_dir = document.getElementById('current-config').innerHTML
    const db = require('better-sqlite3')(db_dir + 'moss.db');
    const data_obj = db.prepare(sql).all();
    return data_obj
}

function outbreakClustersCollapsible() {
    document.getElementById("AMRtab").style.display = "none";
    document.getElementById("cluster-exploration-section").style.display = "block";
    let db_dir = document.getElementById('current-config').innerHTML
    //var configobj = JSON.parse(configfilecontent);

    readTextFile(db_dir + "static_files/outbreakfinder.json", function(text){
        var data = JSON.parse(text);
        var datalist = [[],[]];

        let objlenght = Object.keys(data).length;
        for (i = 0; i < objlenght; i++) {
            datalist[0].push(Object.keys(data)[i]);
            datalist[1].push(Object.values(data)[i]);
        }
        document.getElementById('showData').innerHTML = "";



        document.getElementById('showData').appendChild(makeUL(datalist, db_dir));


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



function makeUL(array, db_dir) {
    // Create the list element:
    var list = document.createElement('div');
    for (var i = 0; i < array[0].length; i++) {
        // Create the list item:
        var item = document.createElement("button");
        item.className = "collapsible";
        item.type = "button";
        item.id = array[0][i];
        isolatelenght = array[1][i].split(", ").length;
        item.innerHTML = array[0][i] + ` (isolates: ${isolatelenght})`;
        item.onclick = function() {collapseFunction(this.id)};
        list.appendChild(item);
        var isolatediv = document.createElement('div');
        isolatediv.className = "collapsible-content";
        isolatediv.id = array[0][i] + "child";
        var textmsg = document.createElement('p');
        textmsg.innerHTML = "The following isolates were associated with this reference:";
        isolatediv.appendChild(textmsg);
        var isolatetext = document.createElement('p');
        isolatetext.innerHTML = `${array[1][i]}`;
        isolatediv.appendChild(isolatetext);
        if (isolatelenght > 0) {
            var matrixbutton = document.createElement("button");
            matrixbutton.type = "button";
            accessionID = array[0][i].split(" ")[0];
            matrixbutton.id = accessionID;
            matrixbutton.innerHTML = `Fetch distancematrix for ${accessionID}`;
            var distancematrixstring = document.createElement('p');
            distancematrixstring.id = array[0][i].split(" ")[0] + "matrixid";
            distancematrixstring.style = "white-space: pre-line";
            matrixbutton.onclick = function() {fetchDistanceMatrix(this.id, db_dir, isolatediv)};
            isolatediv.appendChild(document.createElement("br"));
            isolatediv.appendChild(matrixbutton);
            isolatediv.appendChild(document.createElement("br"));
            isolatediv.appendChild(distancematrixstring);

            var figtreebutton = document.createElement("button");
            figtreebutton.type = "button";
            treeaccessionID = array[0][i].split(" ")[0]  + "fb";
            figtreebutton.id = treeaccessionID;
            figtreebutton.innerHTML = `Fetch phylogenetic tree for ${accessionID}`;
            figtreebutton.onclick = function() {insertPicture(this.id, db_dir)};

            var treeimage = document.createElement("figtree");
            treeimage.id = "figtree" + treeaccessionID;

            isolatediv.appendChild(document.createElement("br"));
            isolatediv.appendChild(figtreebutton);
            isolatediv.appendChild(document.createElement("br"));
            isolatediv.appendChild(treeimage);

        }
        list.appendChild(isolatediv);
    }
    return list;
}


function collapseFunction(id) {

    var content = document.getElementById(id + "child");
    if (content.style.display === "block") {
        content.style.display = "none";
    } else {
        content.style.display = "block";
    }
}

function fetchDistanceMatrix(id, db_dir, isolatediv) {

    readTextFileUpdateDiv(db_dir + `datafiles/distancematrices/${id}/distance_matrix_${id}`, isolatediv, function(text){
        document.getElementById(id + "matrixid").innerHTML = text;
    })
    ;

}

function readTextFileUpdateDiv(file, div, callback) {
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

function insertPicture(id, db_dir) {
    document.getElementById("figtree"+ id).innerHTML = `<img src ="${db_dir}datafiles/distancematrices/${id.slice(0,-2)}/tree.png" width="500" height="500">`;
    //document.getElementById("figtree").style.width = "50px";
    //document.getElementById("figtree").style.height = "50px";
}
