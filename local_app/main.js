// Modules to control application life and create native browser window
const {app, BrowserWindow} = require('electron')
const path = require('path')
const fs = require('fs')
const storage = require('electron-json-storage');

/*
function reset_ipc_sql(cmd, srcpath, db_dir) {

    storage.get('currentConfig', function(error, data) {
      if (error) throw error;
      var srcpath = data.exepath + "src/";

      var cmd = `python3 ${srcpath}reset_ipc_sql.py -i "${data.db_dir}"`;

      exec(cmd, (error, stdout, stderr) => {

        if (error) {
          console.error(`exec error: ${error}`);
          return;
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);

        outbreakfinderstring = `python3 ${srcpath}outbreak_finder.py -db_dir ${db_dir}`
        console.log(outbreakfinderstring);


        exec(outbreakfinderstring, (error, stdout, stderr) => {

            if (error) {
              //If error, change accepted ui to failure, which attached message.
              console.error(`exec error: ${error}`);
              return;
            }

            console.log(`stdout: ${stdout}`);
            console.error(`stderr: ${stderr}`);

            alert("Analysis complete!");



          });



      });

    });



}
*/

function createWindow () {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1600,
    height: 1200,
    title: "My App",
    webPreferences: {
      nodeIntegration: true,
      enableRemoteModule: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  // reset semaphores in SQL db

  // and load the index.html of the app.
  mainWindow.loadFile('html/index.html')


  // Open the DevTools.
  // mainWindow.webContents.openDevTools()
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  createWindow()
  
  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})


// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.

