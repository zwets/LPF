const { exec } = require('child_process');
const fs = require('fs')
const storage = require('electron-json-storage');
const mkdirp = require('mkdirp');
const path = require("path");

function execute_command_as_subprocess(cmd, start_msg, end_msg, fail_msg) {

    alert(start_msg);

    const create_button = document.createElement('button');
    create_button.classList.add('button-7');
    create_button.type = "button";
    create_button.id = "go-to-analyses-button";
    create_button.innerHTML = "Proceed to basecalling overview";
    create_button.onclick = function() {
      location.href='./basecalling.html';
    }
    create_button.style.width = "400px";
    create_button.style.height = "150px";
    create_button.style.fontSize = "large"

    document.getElementById('metadata-table-div').appendChild(document.createElement('br'));
    document.getElementById('metadata-table-div').appendChild(document.createElement('br'));

    document.getElementById('metadata-table-div').appendChild(create_button);

    exec(cmd, (error) => {

        if (error) {
            alert(`${error}`);
            alert(fail_msg);
          console.error(`exec error: ${error}`);
        } else {
            alert(end_msg);
        }

      });

}

function hasDuplicates(array) {
    return (new Set(array)).size !== array.length;
}

function create_metadata_table_fastq(){
    document.getElementById('metadata-table-div').innerHTML = "";
    const file_list_obj = document.getElementById('input').files;
    const file_number = Object.keys(file_list_obj).length;

    let append_table = generate_table_fastq(file_number)

    document.getElementById('metadata-table-div').appendChild(append_table);

    const create_button = document.createElement('button');
    create_button.classList.add('button-7');

    create_button.type = "button";
    create_button.id = "generate-metadata-sheet";
    create_button.onclick = function() {
      const experiment_name = document.getElementById('experiment-name').value;
      const file_list_obj = document.getElementById('input').files;

      const obj_list = [];
      const rows = document.getElementById("metadata_csv_table").rows;
      const header_row = rows[0];

      for (let i = 0; i < rows.length-1; i++) {
            let new_obj = {};
            for (let t = 0; t < rows[i].cells.length; t++) {
                if (header_row.cells[t].innerHTML == 'input_file') {
                    new_obj[header_row.cells[t].innerHTML] = document.getElementById(`input${[i]}${[t]}`).value[0];
                } else {
                    new_obj[header_row.cells[t].innerHTML] = document.getElementById(`input${[i]}${[t]}`).value;
                }
            }
            new_obj['input_path'] = file_list_obj[i].path;
            new_obj['config_path'] = '/opt/moss_db/' + require('/opt/moss_db/config.json')["current_working_db"] + '/';
            var errorMessage = window.validateData(new_obj);
            if (errorMessage != "") {
                console.log(errorMessage);
                break;
              }
            obj_list.push(new_obj);

        }

      const final_obj = {'samples': obj_list}
      const current_moss_system = require('/opt/moss_db/config.json')["current_working_db"];
      const output_json_file = `/opt/moss_db/${current_moss_system}/metadata_json/${experiment_name}.json`;

      /*
      if (errorMessage != "") {
        console.log(errorMessage);
        return;
      }*/
      //Here insert validation function for ENA compatibility
      if (errorMessage == "") {
          if (fs.existsSync(output_json_file)) {
              // path exists
              alert("A file with this name already exists, please choose another one than: ", output_json_file);
            } else {
                fs.writeFile(output_json_file, JSON.stringify(final_obj), err => {
                      if (err) {
                        console.error(err)
                        return
                      }
                      alert(`The metadata json file has been created and is stored at ${output_json_file}`);
                      const create_button = document.createElement('button');
                      create_button.classList.add('button-7');
                      create_button.type = "button";
                      create_button.id = "go-to-analyses-button";
                      create_button.innerHTML = "Proceed to analyses";
                      create_button.onclick = function() {
                        location.href='./analyse.html';
                      }
                      create_button.style.width = "400px";
                      create_button.style.height = "150px";
                      create_button.style.fontSize = "large"

                      document.getElementById('metadata-table-div').appendChild(document.createElement('br'));
                      document.getElementById('metadata-table-div').appendChild(document.createElement('br'));

                      document.getElementById('metadata-table-div').appendChild(create_button);
                      //Make go to analyses shortcut
                    })

                }
              }
          }
    create_button.innerHTML = "Create metadata sheet for sequencing and analysis";
    const mybr = document.createElement('br');
    document.getElementById('metadata-table-div').appendChild(mybr);
    document.getElementById('metadata-table-div').appendChild(create_button);

}

function getCities() {
   let rows = document.getElementById("metadata_csv_table").rows;
   let header_row = rows[0];

      for (let i = 0; i < rows.length-1; i++) {
            for (let t = 0; t < rows[i].cells.length; t++) {
                if (header_row.cells[t].innerHTML == "country") {
                    const countryValue = document.getElementById(`input${[i]}${[t]}`).value
                    const countryData= require('/opt/moss/datafiles/cities_and_countries.json');
                    while (document.getElementById(`input${[i]}${[t-1]}`).hasChildNodes()) {
                        document.getElementById(`input${[i]}${[t-1]}`).removeChild(document.getElementById(`input${[i]}${[t-1]}`).firstChild);
                    }
		    const none_option = document.createElement("option");
                    none_option.value = "Select City";
                    none_option.text = "Select City";
                    document.getElementById(`input${[i]}${[t-1]}`).add(none_option);
		    for(let city in countryData[countryValue]) {
                       const cityName = countryData[countryValue][city]
                       const option = document.createElement("option");
                       option.value = cityName;
                       option.text = cityName;
                       document.getElementById(`input${[i]}${[t-1]}`).add(option);
                    }
                    document.getElementById(`input${[i]}${[t-1]}`).defaultValue = "Select City";
                }
            }
        }
}

function generate_table_fastq(file_number) {

    const file_list_obj = document.getElementById('input').files;


    const table = document.createElement('table');
    table.id = "metadata_csv_table";
    table.classList.add('table');

    const headRow = document.createElement('tr');
    headRow.id = "thead_tr";
    let columnNames = [];

    const jsonData= require('/opt/moss/datafiles/ena_list.json');
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
                continue;
            } else if (typeof identifier === "object") {
                td.defaultValue = "";
                td.classList.add("select");
                const input = document.createElement('select');
                input.id = `input${i}${j}`;
                let object_options = [];
                if (columnNames[j] =="country") {
                    const countryData= require('/opt/moss/datafiles/cities_and_countries.json');
                    const countries = Object.keys(countryData);
                        const countryNames = [];
                        countryNames.push.apply(countryNames, countries);
                    object_options = countryNames;
                    input.onclick = function(){window.getCities()};
                } else if (columnNames[j] =="collection_date") {
                    columnNames[j] =="collection_date (YYYY-MM-DD)"
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
    let numeric = new RegExp (/^\d{2}$/);
    if(!numeric.test(inputText)) {
    const message = String(propertyName+" should contain only two digits in numbers");
       errors = errors.concat("\n").concat(message);
       window.alert(message);
    }
    return errors;
}

exports.allNumeric = allNumeric


// function to validate the data input
function validateData(jsonFinal) {
   let errors = "";
     errors = window.allNumeric(jsonFinal.patient_age, "patient age", errors);
   const dateReg = /^\d{4}-\d{2}-\d{2}$/;
   const dateError = "Collection Date should be in YYYY-MM-DD format"
   if(!dateReg.test(jsonFinal.collection_date)) {
      window.alert(dateError);
      errors = errors.concat("\n").concat(dateError);
      return errors;
   }
   const collDate = new Date(jsonFinal.collection_date);
   let timeS = collDate.getTime();

   if (typeof timeS !== 'number' || Number.isNaN(timeS)) {
      window.alert(dateError);
      errors = errors.concat("\n").concat(dateError);
   }
   return errors;
}

exports.validateData = validateData
