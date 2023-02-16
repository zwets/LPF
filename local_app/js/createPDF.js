function createAlignmentReport() {
    // Load AMR data from /opt/LPF_analyses/<ID>/pdf_resources/amr_data.csv
    // Make AMR table

    // Load viruence data from .......
    // Make virulence table

    // Load plasmid data from .......
    // Make plasmid table

    // Load assembly data from .......
    // Make assembly table

    // All metadata and results from the bacterial parser in stored in /opt/LPF_analyses/<ID>/pdf_resources/bacterial_parser.json

    var doc = new jsPDF();
    doc.text(20, 20, 'Hello world!');
    doc.save('a4.pdf');
}

function createAssemblyReport() {
    var doc = new jsPDF();
    doc.text(20, 20, 'Hello world!');
    doc.save('a4.pdf');
}