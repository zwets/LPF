var mainJS = require("./generate_metadata_sheet_fastq")

const path = require('path');
const fs = jest.createMockFromModule('fs');


test('check allNumeric in inputfield', () => {
    expect(mainJS.allNumeric("12", "Age", "")).toEqual("");
    Object.defineProperty(global, "window", {
            value: {
                alert: jest.fn(),
                allLetters: mainJS.allLetters,
                allNumeric: mainJS.allNumeric,
            },
        });
    expect(mainJS.allNumeric("aa", "Age", "")).toContain("Age should contain only numbers");
});

test('check allLetters in inputfield', () => {
	expect(mainJS.allLetters("Acdd", "city", "")).toEqual("");
    expect(mainJS.allLetters("aa1", "city", "")).toContain("city should contain only letters");
});

test('check allLetters in inputfield', () => {
    expect(mainJS.allLetters("ABcd", "country", "")).toEqual("");
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
	expect(mainJS.validateData(jsonData)).toEqual("");
	expect(mainJS.validateData(jsonDataEr)).toContain("Collection Date should be in YYYY-MM-DD format");
	expect(mainJS.validateData(jsonDataEr2)).toContain("Collection Date should be in YYYY-MM-DD format");
});


test('split csv into json objects', () => {
    var outJson = { "age" : "12", "name" : "aaa"};
    var csv_string = 'age,name\n12,aaa\n';
	expect(mainJS.convertToJson(csv_string)).toEqual(outJson);
});

