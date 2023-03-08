import { parse } from 'csv-parse';
function generatePDFReport(analysisId, type) {
    dtu_logo_base64 = '/opt/LPF/local_app/js/image_data/dtu_logo_base64.txt';
    parseCSV('/opt/LPF_analyses/'+analysisId+'/pdf_resources/amr_data.csv');
}

function parseCSV(file) {
    const records = [];
    // Initialize the parser
    const parser = parse({
        delimiter: ','
    });
    parser.on(file, function(){
        let record;
        while ((record = parser.read()) !== null) {
            records.push(record);
        }
    });
    console.log(records);

}