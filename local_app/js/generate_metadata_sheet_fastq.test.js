var mainJS = require("./generate_metadata_sheet_fastq")

const path = require('path');
const fs = jest.createMockFromModule('fs');


test('check allNumeric in inputfield', () => {
    expect(mainJS.allNumeric("12", "Age", "")).toEqual("");
    Object.defineProperty(global, "window", {
            value: {
                alert: jest.fn(),
                allNumeric: mainJS.allNumeric,
            },
        });
    expect(mainJS.allNumeric("aa", "Age", "")).toContain("Age should contain only numbers upto three digits");
});

test('check extension for the input field', () => {
    expect(mainJS.isExperimentNameValid("experimentName.json")).toEqual(false);
    expect(mainJS.isExperimentNameValid("experimentName")).toEqual(true);
});

test('validate json data', () => {
    var jsonData = {
    "city" : "copenhagen",
    "country" : "Denmark",
    "patient_age" : 52,
    "collection_date" : "2022-01-01"
    }
    var jsonDataEr = {
    "city" : "copenhagen",
    "country" : "Denmark",
    "patient_age" : "52",
    "collection_date" : "20220101"
    }
    var jsonDataEr2 = {
    "city" : "copenhagen",
    "country" : "Denmark",
    "patient_age" : "52",
    "collection_date" : "2022-01-99"
    }
    var jsonDataEr3 = {
    "city" : "copenhagen",
    "country" : "Unspecified country",
    "patient_age" : 23,
    "collection_date" : "2022-09-14"
    }
	expect(mainJS.validateData(jsonData)).toEqual("");
	expect(mainJS.validateData(jsonDataEr)).toContain("Collection Date should be in YYYY-MM-DD format");
	expect(mainJS.validateData(jsonDataEr2)).toContain("Collection Date should be in YYYY-MM-DD format");
    expect(mainJS.validateData(jsonDataEr3)).toContain("Please select country");
});
