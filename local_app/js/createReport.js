import * as fs from 'fs';
import * as path from 'path';
import * as csv from 'fast-csv';
function generatePDFReport(analysisId, type) {
    dtu_logo_base64 = '/opt/LPF/local_app/js/image_data/dtu_logo_base64.txt';
    console.log(dtu_logo_base64);
    parseCSV('/opt/LPF_analyses/'+analysisId+'/pdf_resources/amr_data.csv');
}


function parseCSV(file) {
    fs.createReadStream(path.resolve(__dirname, 'assets', file))
    .pipe(csv.parse({ headers: true }))
    .on('error', error => console.error(error))
    .on('data', row => console.log(row))
    .on('end', (rowCount: number) => console.log(`Parsed ${rowCount} rows`));
}