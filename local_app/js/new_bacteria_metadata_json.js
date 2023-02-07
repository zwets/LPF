const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');
const mkdirp = require('mkdirp');
const path = require("path");
const Dialogs = require("dialogs");

function execute_command_as_subprocess(cmd, print_msg) {
    console.log(cmd);

    console.log("Analysis has been submitted");

    alert("Analysis has been submitted. Go to the Results section is the left menu to see progress and final results.");

    exec(cmd, (error, stdout, stderr) => {

        if (error) {
            alert(`exec error: ${error}`);
            document.getElementById('analysis-msg').innerHTML = `Analysis has failed: ${error}`;
          console.error(`exec error: ${error}`);
          return;
        } else {
            alert("Analysis has been completed.");
            document.getElementById('analysis-msg').innerHTML = `Analysis has been completed`;
        }

        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);



      });

}

function hasDuplicates(array) {
    return (new Set(array)).size !== array.length;
}

function isExperimentNameValid(experiment_name) {
    const ext = experiment_name.split('.');
    if (ext.length > 1) {
       window.alert("please enter the sequencing experiment name without .json extension");
       return false;
    } else {
       return true;
    }
}

exports.isExperimentNameValid = isExperimentNameValid

function create_meta_data_table_fastq(){
    const experiment_name = document.getElementById('experiment-name').value;

    !(window.isExperimentNameValid(experiment_name) {
        alert("please enter the sequencing experiment name without .json extension");
        return;
    }
}

function input_prompt_costum_city(rowNumber, columnNumber) {
    var Dialogs = require('dialogs')
    var dialogs = Dialogs()
    dialogs.prompt('Please enter a custom city name', function (custom_city) {
        console.log(custom_city)
        })
}

function getCities(rowNumber, columnNumber) {
    let country = document.getElementById(`input${[rowNumber]}${[columnNumber]}`).value;
    let rows = document.getElementById("metadata_csv_table").rows;
    let header_row = rows[0];
    if (header_row.cells[columnNumber].innerHTML == "country") {
       const countryValue = document.getElementById(`input${[rowNumber]}${[columnNumber]}`).value
       const countryData= require('/opt/LPF/datafiles/cities_and_countries.json');
       while (document.getElementById(`input${[rowNumber]}${[columnNumber-1]}`).hasChildNodes()) {
           document.getElementById(`input${[rowNumber]}${[columnNumber-1]}`).removeChild(document.getElementById(`input${[rowNumber]}${[columnNumber-1]}`).firstChild);
       }
       const none_option = document.createElement("option");
       none_option.value = "Unspecified city";
       none_option.text = "Unspecified city";
       document.getElementById(`input${[rowNumber]}${[columnNumber-1]}`).add(none_option);
       const custom_option = document.createElement("option");
       custom_option.value = "custom city";
       custom_option.text = "custom city";
       custom_option.onclick = input_prompt_costum_city(rowNumber, columnNumber);

       document.getElementById(`input${[rowNumber]}${[columnNumber-1]}`).add(custom_option);
       for (let city in countryData[countryValue]) {
           const cityName = countryData[countryValue][city]
           const option = document.createElement("option");
           option.value = cityName;
           option.text = cityName;
           document.getElementById(`input${[rowNumber]}${[columnNumber-1]}`).add(option);
       }
       document.getElementById(`input${[rowNumber]}${[columnNumber-1]}`).defaultValue = "Unspecified city";
   }
}


/*
function getCustomValue() {
    let rows = document.getElementById("metadata_csv_table").rows;
    let header_row = rows[0];

    for (let i = 0; i < rows.length-1; i++) {
        for (let t = 0; t < rows[i].cells.length; t++) {
            if (header_row.cells[t].innerHTML == "city") {
                const cityValue = document.getElementById(`input${[i]}${[t]}`).value
                if (cityValue == "custom city") {
                    const Dialogs = require('dialogs')
                    const dialogs = Dialogs()
                    dialogs.prompt('Give the city name', ok => {
                        const custom_option = document.createElement("option");
                        custom_option.value = ok;
                        custom_option.text = ok;
                        document.getElementById(`input${[i]}${[t]}`).add(custom_option);
                        document.getElementById(`input${[i]}${[t]}`).value = custom_option.value;
                    })
                }
            }

            if (header_row.cells[t].innerHTML == "country") {
                const countryValue = document.getElementById(`input${[i]}${[t]}`).value
                const countryData = require('/opt/LPF/datafiles/cities_and_countries.json');
                while (document.getElementById(`input${[i]}${[t - 1]}`).hasChildNodes()) {
                    document.getElementById(`input${[i]}${[t - 1]}`).removeChild(document.getElementById(`input${[i]}${[t - 1]}`).firstChild);
                }
                const none_option = document.createElement("option");
                none_option.value = "Unspecified city";
                none_option.text = "Unspecified city";
                document.getElementById(`input${[i]}${[t - 1]}`).add(none_option);
                for (let city in countryData[countryValue]) {
                    const cityName = countryData[countryValue][city]
                    const option = document.createElement("option");
                    option.value = cityName;
                    option.text = cityName;
                    document.getElementById(`input${[i]}${[t - 1]}`).add(option);
                }
                document.getElementById(`input${[i]}${[t - 1]}`).defaultValue = "Unspecified city";
            }
        }
    }
}
*/

function generate_table_fastq(file_number) {

    const file_list_obj = document.getElementById('input').files;


    const table = document.createElement('table');
    table.id = "metadata_csv_table";
    table.classList.add('table');

    const headRow = document.createElement('tr');
    headRow.id = "thead_tr";
    let columnNames = [];

    const jsonData= require('/opt/LPF/datafiles/ena_list.json');
    const ena_keys = Object.keys(jsonData);
    columnNames.push.apply(columnNames, ena_keys)

    for (let i = 0; i < columnNames.length; i++) {
      let th = document.createElement('th');
      th.appendChild(document.createTextNode(columnNames[i]));
      headRow.appendChild(th);
    }

    table.appendChild(headRow);

    for (let i = 0; i < file_number; i++) {
      let tr = document.createElement('tr');
      tr.id = "tbody_tr_" + (i).toString();
      let sample_name = file_list_obj[i].path.split("/").slice(-1);

      for (let j = 0; j < columnNames.length; j++) {
        let identifier = jsonData[columnNames[j]];
        let td = document.createElement('td');
        td.style.textAlign = "center";
        td.id = `outer${i}${j}`;
        if (j > 0) {
            if (identifier=="free_text") {
                td.defaultValue = "";
                td.classList.add("input");
                const input = document.createElement('input');
                input.id = `input${i}${j}`;
                td.appendChild(input);
                tr.appendChild(td);
                if (columnNames[j] =="collection_date") {
                    input.placeholder = "YYYY-MM-DD";
                    }
                continue;

            } else if (typeof identifier === "object") {
                td.defaultValue = "";
                td.classList.add("select");
                const input = document.createElement('select');
                input.id = `input${i}${j}`;
                let object_options = [];
                if (columnNames[j] =="country") {
                    const countryData= require('/opt/LPF/datafiles/cities_and_countries.json');
                    const countries = Object.keys(countryData);
                    const countryNames = ["Unspecified country"];
                    countryNames.push.apply(countryNames, countries);
                    object_options = countryNames;
                    input.onclick = function(){window.getCities(i, j)};
                }
		        else if (columnNames[j] == "city") {
                    object_options = Object.values(identifier);
                    input.onclick = function(){window.getCustomValue()};
                }
                else {
                    object_options = Object.values(identifier);
                    }
            for (let t = 0; t < object_options.length; t++) {
                let option = document.createElement("option");
                option.value = object_options[t];
                option.text = object_options[t];
                input.add(option);
                }
            input.defaultValue = object_options[0];
            td.appendChild(input);
            tr.appendChild(td);
            continue;
            }
        } else if (j == 0) {
            td.defaultValue = "";
            const label = document.createElement('label');
            label.id = `input${i}${j}`;
            label.innerHTML = sample_name;
            label.value = sample_name;
            td.appendChild(label);
            tr.appendChild(td);
            continue;
        }
        tr.appendChild(td);
      }

      table.appendChild(tr);
    }
    return table
}

//code to check numerical in input field (patient_age)
function allNumeric(inputText, propertyName, errors) {
   if (inputText != "") {
       let numeric = new RegExp (/^\d{1,3}$/);
        if (!numeric.test(inputText)) {
     	 const message = String(propertyName+" should contain only numbers upto three digits");
      	    errors = errors.concat("\n").concat(message);
            window.alert(message);
  	      }
      }
   return errors;
}

exports.allNumeric = allNumeric


// function to validate the data input
function validateData(jsonFinal) {
   let errors = "";
   errors = window.allNumeric(jsonFinal.patient_age, "patient age", errors);
   if(jsonFinal.country === "" || jsonFinal.country == "Unspecified country") {
     window.alert("Please select country");
     errors = errors.concat("\n").concat("Please select country");
   }
   const dateReg = /^\d{4}-\d{2}-\d{2}$/;
   const dateError = "Collection Date should be in YYYY-MM-DD format"
   if(!dateReg.test(jsonFinal.collection_date)) {
      window.alert(dateError);
      errors = errors.concat("\n").concat(dateError);
      return errors;
   }
   const collDate = new Date(jsonFinal.collection_date);
   let timeS = collDate.getTime();
   if(jsonFinal.city === "undefined") {
     window.alert("Please enter or select the city");
     errors = errors.concat("\n").concat("Please enter or select the city name");
     return errors;
   }
   if(jsonFinal.city === "" || jsonFinal.city == "Unspecified city") {
     window.alert("Please select city");
     errors = errors.concat("\n").concat("Please select city");
     return errors;
   }
   if (typeof timeS !== 'number' || Number.isNaN(timeS)) {
      window.alert(dateError);
      errors = errors.concat("\n").concat(dateError);
   }
   return errors;
}

exports.validateData = validateData


//code to check numerical in input field (patient_age)
function allNumeric(inputText, propertyName, errors) {
   if (inputText != "") {
       let numeric = new RegExp (/^\d{1,3}$/);
        if (!numeric.test(inputText)) {
     	 const message = String(propertyName+" should contain only numbers upto three digits");
      	    errors = errors.concat("\n").concat(message);
            window.alert(message);
  	      }
      }
   return errors;
}

exports.allNumeric = allNumeric


// function to validate the data input
function validateData(jsonFinal) {
   let errors = "";
   errors = window.allNumeric(jsonFinal.patient_age, "patient age", errors);
   if(jsonFinal.country === "" || jsonFinal.country == "Unspecified country") {
     window.alert("Please select country");
     errors = errors.concat("\n").concat("Please select country");
   }
   const dateReg = /^\d{4}-\d{2}-\d{2}$/;
   const dateError = "Collection Date should be in YYYY-MM-DD format"
   if(!dateReg.test(jsonFinal.collection_date)) {
      window.alert(dateError);
      errors = errors.concat("\n").concat(dateError);
      return errors;
   }
   const collDate = new Date(jsonFinal.collection_date);
   let timeS = collDate.getTime();
   if(jsonFinal.city === "undefined") {
     window.alert("Please enter or select the city");
     errors = errors.concat("\n").concat("Please enter or select the city name");
     return errors;
   }
   if(jsonFinal.city === "" || jsonFinal.city == "Unspecified city") {
     window.alert("Please select city");
     errors = errors.concat("\n").concat("Please select city");
     return errors;
   }
   if (typeof timeS !== 'number' || Number.isNaN(timeS)) {
      window.alert(dateError);
      errors = errors.concat("\n").concat(dateError);
   }
   return errors;
}

exports.validateData = validateData
