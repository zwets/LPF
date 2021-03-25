const { _colorStringFilter } = require("gsap/gsap-core");

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

