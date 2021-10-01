const { _colorStringFilter } = require("gsap/gsap-core");

storage.get('currentConfig', function(error, data) {
  if (error) throw error;

  var element = document.getElementById('current-config');
  element.textContent = data.db_dir;
  var exepath = data.exepath;
});

function readSingleFile(e) {
    var file = e.target.files[0];
    if (!file) {
        return;
    }
    var reader = new FileReader();
    reader.onload = function(e) {
        var contents = e.target.result;
        displayContents(contents);
        return contents;
    };
    reader.readAsText(file);
}

function displayContents(contents) {
    var element = document.getElementById('file-content');
    element.textContent = contents;
}




function sql_data_query_table(data_obj, data) {
        var divShowData = document.getElementById('showData');
        divShowData.innerHTML = "";
        if (data_obj.length == 0) {
            var textmsg = document.createElement('p');
            textmsg.innerHTML = `No results found`;
            document.getElementById('search-area').append(textmsg);
        }

        var col = [];

		for (var i = 0; i < data_obj.length; i++) {
                for (var key in data_obj[i]) {
                    if (col.indexOf(key) === -1) {
                        col.push(key);
                    }
                }
            }
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
            img.id = data_obj[i].entryid;
            img.name = data_obj[i].entryid;
            img.src = data.exepath + "local_app/images/report-icon.png";
            img.setAttribute('height', '17pt');
            img.innerHTML = data_obj[i].entryid;
            img.onclick = function() {openPDF(this.id, data)};
            //el.addEventListener("click", function(){
            //    openPDF(Object.keys(myjson)[i]));
            //});
            tabCell.appendChild(img);
        }

        divShowData.appendChild(table);
    }

function showMostRecentIsolates() {
    document.getElementById('button-panel').innerHTML = "";
    document.getElementById('search-area').innerHTML = "";
    let sql = `SELECT * FROM isolatetable`;
    let db_dir = document.getElementById('current-config').innerHTML
    const db = require('better-sqlite3')(db_dir + 'moss.db');
    const data_obj = db.prepare(sql).all();
    if (data_obj.length > 50) {
        var size = 50;
        const sliceddata_obj = data_obj.slice(0, size);
        storage.get('currentConfig', function(error, data) {
          if (error) throw error;

          most_recent_isolates_table(sliceddata_obj, data);
        });
    } else {
        const sliceddata_obj = data_obj;
        storage.get('currentConfig', function(error, data) {
          if (error) throw error;

          most_recent_isolates_table(sliceddata_obj, data);
        });
    };
 }


function most_recent_isolates_table(data_obj, data) {
        var divShowData = document.getElementById('showData');
        divShowData.innerHTML = "";
        document.getElementById('search-area').innerHTML = "";


		var myObject = [];

        var col = [];
        col.push('Name');
        col.push('Collection_date');

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
            tabCell.innerHTML = data_obj[i].collection_date;

            var tabCell = tr.insertCell(-1);
            var img = document.createElement('img');
            img.id = data_obj[i].entryid;
            img.name = data_obj[i].isolatename;
            img.src = data.exepath + "local_app/images/report-icon.png";
            img.setAttribute('height', '17pt');
            img.innerHTML = data_obj[i].entryid;
            img.onclick = function() {openPDF(this.id, data)};
            //el.addEventListener("click", function(){
            //    openPDF(Object.keys(myjson)[i]));
            //});
            tabCell.appendChild(img);

        }
        divShowData.appendChild(table);

    }

function openPDF(id, data){
  window.open(data.db_dir + "analysis/" + id + "/" + id + "_report.pdf");
  //return false;
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

function produce_query_table(string) {
    data_obj = search_function(string);
    if (data_obj.length > 50) {
        var textmsg = document.createElement('p');
        textmsg.innerHTML = `A total of ${data_obj.length} results were found, 50 most recent of them are displayed here:`;
        document.getElementById('search-area').append(textmsg);
        var size = 50;
        const sliceddata_obj = data_obj.slice(0, size);
        storage.get('currentConfig', function(error, data) {
              if (error) throw error;

              sql_data_query_table(sliceddata_obj, data);
            });
    } else {
        const sliceddata_obj = data_obj;
        storage.get('currentConfig', function(error, data) {
          if (error) throw error;

          sql_data_query_table(sliceddata_obj, data);
        });
    }
}

function search_db_query(sql) {
    let db_dir = document.getElementById('current-config').innerHTML
    const db = require('better-sqlite3')(db_dir + 'moss.db');
    const data_obj = db.prepare(sql).all();
    return data_obj
}

function search_function(string) {
    let query = document.getElementById('search_field').value;
    if (string == "Reference name") { //Not done
        let sql = `SELECT * FROM referencetable WHERE refname LIKE '%${query}%'`;
        var data_obj = search_db_query(sql);
        return data_obj
    } else if (string == "Reference Header ID") {
        let sql = `SELECT * FROM referencetable WHERE headerid LIKE '%${query}%'`;
        var data_obj = search_db_query(sql);
        return data_obj
    } else if (string == "Reference Specie") {
      let sql = `SELECT * FROM referencetable WHERE headerid LIKE '%${query}%'`;
      var data_obj = search_db_query(sql);
      return data_obj
    } else if (string == "Isolate Name") {
        let sql = `SELECT * FROM isolatetable WHERE isolatename LIKE '%${query}%'`;
        var data_obj = search_db_query(sql);
        return data_obj
    } else if (string == "Isolate Specie") {
        let sql = `SELECT * FROM isolatetable WHERE headerid LIKE '%${query}%'`;
        var data_obj = search_db_query(sql);
        return data_obj
    } else if (string == "Run ID") {
        return data_obj
    } else if (string == "Outbreak Number") {
        return data_obj
    } else if (string == "Sequence Type") {
        return data_obj
    } else if (string == "Resistance Genes") {
        let sql = `SELECT * FROM isolatetable WHERE amrgenes LIKE '%${query}%'`;
        var data_obj = search_db_query(sql);
        return data_obj
    } else if (string == "Plasmids") {
        let sql = `SELECT * FROM isolatetable WHERE plasmids LIKE '%${query}%'`;
        var data_obj = search_db_query(sql);
        return data_obj
    } else if (string == "Virulence Genes") {
         let sql = `SELECT * FROM isolatetable WHERE virulencegenes LIKE '%${query}%'`;
         var data_obj = search_db_query(sql);
         return data_obj
    } else {
        var data_obj = [];
        return data_obj
    }

}

function addSearchField(string) {
  var x = document.createElement("INPUT");
  x.setAttribute("type", "text");
  x.setAttribute("value", "");
  x.id = "search_field"
  x.style.margin='0px 5px';
  var element = document.getElementById('search-area');
  element.appendChild(x);

  var search_button = document.createElement("button");
  search_button.type = "button";
  search_button.id = "search_button";
  search_button.style.width = '115px'; // setting the width to 200px
  search_button.style.height = '23px'; // setting the height to 200px
  search_button.innerHTML = "Fetch results"
  search_button.onclick = function() {produce_query_table(string)};

  element.appendChild(search_button);


}

function singleSearchArea(string) {
    var divShowData = document.getElementById('showData');
    divShowData.innerHTML = "";
    document.getElementById('search-area').innerHTML = "";
    var element = document.getElementById('search-area');
    element.innerHTML = `Enter search query for ${string} :`;
    addSearchField(string);
}

function showIndividualIsolateOptions() {
    // Create the list element:
    document.getElementById('search-area').innerHTML = "";
    document.getElementById('showData').innerHTML = "";
    var element = document.getElementById('button-panel')
    element.innerHTML = "";
    var isolate_name_button = document.createElement("button");
    isolate_name_button.type = "button";
    isolate_name_button.id = "isolate_name_button";
    isolate_name_button.style.width = '125px'; // setting the width to 200px
    isolate_name_button.style.height = '23px'; // setting the height to 200px
    isolate_name_button.innerHTML = "Isolate Name"
    isolate_name_button.onclick = function() {singleSearchArea(isolate_name_button.innerHTML)};

    element.appendChild(isolate_name_button);

    var isolate_genus_species_button = document.createElement("button");
    isolate_genus_species_button.type = "button";
    isolate_genus_species_button.id = "isolate_genus_species_button";
    isolate_genus_species_button.style.width = '125px'; // setting the width to 200px
    isolate_genus_species_button.style.height = '23px'; // setting the height to 200px
    isolate_genus_species_button.innerHTML = "Isolate Specie"
    isolate_genus_species_button.style.margin='0px 2px';
    isolate_genus_species_button.onclick = function() {singleSearchArea(isolate_genus_species_button.innerHTML)};


    element.appendChild(isolate_genus_species_button);

    var run_id_button = document.createElement("button");
    run_id_button.type = "button";
    run_id_button.id = "run_id_button";
    run_id_button.style.width = '125px'; // setting the width to 200px
    run_id_button.style.height = '23px'; // setting the height to 200px
    run_id_button.innerHTML = "Run ID"
    run_id_button.style.margin='0px 2px';
    run_id_button.onclick = function() {singleSearchArea(run_id_button.innerHTML)};


    element.appendChild(run_id_button);

    var outbreak_number_button = document.createElement("button");
    outbreak_number_button.type = "button";
    outbreak_number_button.id = "outbreak_number_button";
    outbreak_number_button.style.width = '125px'; // setting the width to 200px
    outbreak_number_button.style.height = '23px'; // setting the height to 200px
    outbreak_number_button.innerHTML = "Outbreak Number"
    outbreak_number_button.style.margin='0px 2px';
    outbreak_number_button.onclick = function() {singleSearchArea(outbreak_number_button.innerHTML)};


    element.appendChild(outbreak_number_button);

    var sequence_type_button = document.createElement("button");
    sequence_type_button.type = "button";
    sequence_type_button.id = "sequence_type_button";
    sequence_type_button.style.width = '125px'; // setting the width to 200px
    sequence_type_button.style.height = '23px'; // setting the height to 200px
    sequence_type_button.innerHTML = "Sequence Type"
    sequence_type_button.style.margin='0px 2px';
    sequence_type_button.onclick = function() {singleSearchArea(sequence_type_button.innerHTML)};


    element.appendChild(sequence_type_button);

    var resistance_genes_button = document.createElement("button");
    resistance_genes_button.type = "button";
    resistance_genes_button.id = "resistance_genes_button";
    resistance_genes_button.style.width = '125px'; // setting the width to 200px
    resistance_genes_button.style.height = '23px'; // setting the height to 200px
    resistance_genes_button.innerHTML = "Resistance Genes"
    resistance_genes_button.style.margin='0px 2px';
    resistance_genes_button.onclick = function() {singleSearchArea(resistance_genes_button.innerHTML)};


    element.appendChild(resistance_genes_button);

    var plasmid_button = document.createElement("button");
    plasmid_button.type = "button";
    plasmid_button.id = "plasmid_button";
    plasmid_button.style.width = '125px'; // setting the width to 200px
    plasmid_button.style.height = '23px'; // setting the height to 200px
    plasmid_button.innerHTML = "Plasmids"
    plasmid_button.style.margin='0px 2px';
    plasmid_button.onclick = function() {singleSearchArea(plasmid_button.innerHTML)};


    element.appendChild(plasmid_button);

    var virulence_button = document.createElement("button");
    virulence_button.type = "button";
    virulence_button.id = "virulence_button";
    virulence_button.style.width = '125px'; // setting the width to 200px
    virulence_button.style.height = '23px'; // setting the height to 200px
    virulence_button.innerHTML = "Virulence Genes"
    virulence_button.style.margin='0px 2px';
    virulence_button.onclick = function() {singleSearchArea(virulence_button.innerHTML)};


    element.appendChild(virulence_button);

}

function showClusterReferenceOptions() {
    document.getElementById('search-area').innerHTML = "";
    document.getElementById('showData').innerHTML = "";
    // Create the list element:
    // Also needs to wipe existing Search-area, button-panel etc.
    var element = document.getElementById('button-panel')
    element.innerHTML = "";
    var reference_name_button = document.createElement("button");
    reference_name_button.type = "button";
    reference_name_button.id = "reference-name-button";
    reference_name_button.style.width = '125px'; // setting the width to 200px
    reference_name_button.style.height = '23px'; // setting the height to 200px
    reference_name_button.innerHTML = "Reference Name"
    reference_name_button.onclick = function() {singleSearchArea(reference_name_button.innerHTML)};


    element.appendChild(reference_name_button);

    var reference_genus_species_button = document.createElement("button");
    reference_genus_species_button.type = "button";
    reference_genus_species_button.id = "reference_genus_species_button";
    reference_genus_species_button.style.width = '125px'; // setting the width to 200px
    reference_genus_species_button.style.height = '23px'; // setting the height to 200px
    reference_genus_species_button.innerHTML = "Reference Specie"
    reference_genus_species_button.style.margin='0px 2px';
    reference_genus_species_button.onclick = function() {singleSearchArea(reference_genus_species_button.innerHTML)};

    element.appendChild(reference_genus_species_button);

    var reference_headerid_button = document.createElement("button");
    reference_headerid_button.type = "button";
    reference_headerid_button.id = "reference_headerid_button";
    reference_headerid_button.style.width = '145px'; // setting the width to 200px
    reference_headerid_button.style.height = '23px'; // setting the height to 200px
    reference_headerid_button.innerHTML = "Reference Header ID"
    reference_headerid_button.style.margin='0px 2px';
    reference_headerid_button.onclick = function() {singleSearchArea(reference_headerid_button.innerHTML)};

    element.appendChild(reference_headerid_button);

}
/*
function sqlResultsTable(sqlobj) {
    let db_dir = document.getElementById('current-config').innerHTML
    //var configobj = JSON.parse(configfilecontent);
    document.getElementById('showData').innerHTML = "";

    document.getElementById('showData').appendChild(makeUL(datalist, db_dir));

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
*/

function outbreakClustersCollapsible() {
    let db_dir = document.getElementById('current-config').innerHTML
    //var configobj = JSON.parse(configfilecontent);

    readTextFile(db_dir + "analyticalFiles/outbreakfinder.json", function(text){
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
//usage:

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

function insertPicture(id, db_dir) {
    document.getElementById("figtree"+ id).innerHTML = `<img src ="${db_dir}datafiles/distancematrices/${id.slice(0,-2)}/tree.png" width="500" height="500">`;
    //document.getElementById("figtree").style.width = "50px";
    //document.getElementById("figtree").style.height = "50px";
}


function CreateTableFromJSON(JSON) {
    // EXTRACT VALUE FOR HTML HEADER.
    // ('Book ID', 'Book Name', 'Category' and 'Price')
    var col = [];
    for (var i = 0; i < JSON.length; i++) {
        for (var key in JSON[i]) {
            if (col.indexOf(key) === -1) {
                col.push(key);
            }
        }
    }

    // CREATE DYNAMIC TABLE.
    var table = document.createElement("table");

    // CREATE HTML TABLE HEADER ROW USING THE EXTRACTED HEADERS ABOVE.

    var tr = table.insertRow(-1);                   // TABLE ROW.

    for (var i = 0; i < col.length; i++) {
        var th = document.createElement("th");      // TABLE HEADER.
        th.innerHTML = col[i];
        tr.appendChild(th);
    }

    // ADD JSON DATA TO THE TABLE AS ROWS.
    for (var i = 0; i < JSON.length; i++) {

        tr = table.insertRow(-1);

        for (var j = 0; j < col.length; j++) {
            var tabCell = tr.insertCell(-1);
            tabCell.innerHTML = JSON[i][col[j]];
        }
    }


    // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
    var divContainer = document.getElementById("showData");
    divContainer.innerHTML = "";
    divContainer.appendChild(table);
}

