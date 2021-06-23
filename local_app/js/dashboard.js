const { _colorStringFilter } = require("gsap/gsap-core");
var mysql = require('mysql');



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

function makeUL(array) {
    // Create the list element:
    var list = document.createElement('ul');

    for (var i = 0; i < array.length; i++) {
        // Create the list item:
        var item = document.createElement('li');

        // Set its contents:
        item.appendChild(document.createTextNode(array[i]));

        // Add it to the list:
        list.appendChild(item);
    }

    // Finally, return the constructed list:
    return list;
}


function showMostRecentIsolates() {
  let dbdir = document.getElementById('current-config').innerHTML
  var con = mysql.createConnection({
    database: dbdir + "moss.db"
  });

  con.connect(function(err) {
    if (err) throw err;
    console.log("Connected!");
  });


}

function addSearchField() {
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
  search_button.onclick = function() {console.log("fetch results")};

  element.appendChild(search_button);


}

function singleSearchArea(string) {
    var element = document.getElementById('search-area');
    element.innerHTML = `Enter search query for ${string} :`;
    addSearchField();
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
    isolate_genus_species_button.innerHTML = "Genus/Specie"
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
    reference_genus_species_button.innerHTML = "Genus/Specie"
    reference_genus_species_button.style.margin='0px 2px';
    reference_genus_species_button.onclick = function() {singleSearchArea(reference_genus_species_button.innerHTML)};


    element.appendChild(reference_genus_species_button);

}


function outbreakClustersCollapsible() {
    let dbdir = document.getElementById('current-config').innerHTML
    //var configobj = JSON.parse(configfilecontent);

    readTextFile(dbdir + "analyticalFiles/outbreakfinder.json", function(text){
        var data = JSON.parse(text);
        var datalist = [[],[]];

        let objlenght = Object.keys(data).length;
        for (i = 0; i < objlenght; i++) {
            datalist[0].push(Object.keys(data)[i]);
            datalist[1].push(Object.values(data)[i]);
        }
        document.getElementById('showData').innerHTML = "";

        console.log(datalist);

        document.getElementById('showData').appendChild(makeUL(datalist, dbdir));
        
        
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

function makeUL(array, dbdir) {
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
            matrixbutton.onclick = function() {fetchDistanceMatrix(this.id, dbdir, isolatediv)};
            isolatediv.appendChild(document.createElement("br"));
            isolatediv.appendChild(matrixbutton);
            isolatediv.appendChild(document.createElement("br"));
            isolatediv.appendChild(distancematrixstring);

            var figtreebutton = document.createElement("button");
            figtreebutton.type = "button";
            treeaccessionID = array[0][i].split(" ")[0]  + "fb";
            figtreebutton.id = treeaccessionID;
            figtreebutton.innerHTML = `Fetch phylogenetic tree for ${accessionID}`;
            figtreebutton.onclick = function() {insertPicture(this.id, dbdir)};

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

function fetchDistanceMatrix(id, dbdir, isolatediv) {
    
    readTextFileUpdateDiv(dbdir + `datafiles/distancematrices/${id}/distance_matrix_${id}`, isolatediv, function(text){
        document.getElementById(id + "matrixid").innerHTML = text;
    })
    ;
    
}

function insertPicture(id, dbdir) {
    document.getElementById("figtree"+ id).innerHTML = `<img src ="${dbdir}datafiles/distancematrices/${id.slice(0,-2)}/tree.png" width="500" height="500">`;
    //document.getElementById("figtree").style.width = "50px";
    //document.getElementById("figtree").style.height = "50px";
}


function CreateTableFromJSON(JSON) {
    console.log(JSON);
    // EXTRACT VALUE FOR HTML HEADER. 
    // ('Book ID', 'Book Name', 'Category' and 'Price')
    var col = [];
    for (var i = 0; i < JSON.length; i++) {
        for (var key in JSON[i]) {
            console.log(key);
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
    console.log(table);

    // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
    var divContainer = document.getElementById("showData");
    divContainer.innerHTML = "";
    divContainer.appendChild(table);
}

