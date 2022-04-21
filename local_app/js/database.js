const { _colorStringFilter } = require("gsap/gsap-core");

//const { ipcMain } = require('electron');
//const sqlite3 = require('sqlite3');

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

//db.serialize(function() {
//    db_dir = document.getElementById('current-config').innerHTML;
//    console.log(db_dir);
 //   const database = new sqlite3.Database(db_dir + 'PRTT.db', (err) => {
//        if (err) console.error('Database opening error: ', err);
 //   });
  //db.run("CREATE TABLE lorem (info TEXT)");

  //var stmt = db.prepare("INSERT INTO lorem VALUES (?)");
  //for (var i = 0; i < 10; i++) {
  //    stmt.run("Ipsum " + i);
  //}
  //stmt.finalize();

  //db.each("SELECT * FROM isolate_table AS id", function(err, row) {
  //    console.log(row.id);
  //});
  //db.close();
//});

function logdb() {
    db_dir = document.getElementById('current-config').innerHTML;
    var sqlite3 = require('sqlite3').verbose();
    //var db = new sqlite3.Database(db_dir + 'PRTT.db');

    console.log(db_dir + 'PRTT.db');

    let db = new sqlite3.Database(db_dir + 'PRTT.db', (err) => {
      if (err) {
        console.error(err.message);
      }
      console.log('Connected to the MOSS database.');
    });

    db.serialize(function() {

      db.each("SELECT entryid AS id FROM isolate_table", function(err, row) {
            console.log(row.id);
            console.log(row.id[0]);
        });
    });

    db.close();

}

