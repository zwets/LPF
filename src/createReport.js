function generatePDFReport(analysisId, type) {
    console.log("Generating PDF report for analysis: "+analysisId);
}

async function generatePDFReport2(analysisId, type) {
    dtu_logo_base64 = '/home/satya/dev/moss/local_app/js/image_data/dtu_logo_base64.txt';
    let amr_data = '/opt/LPF_analyses/'+analysisId+'/pdf_resources/amr_data.csv';
    let vir_data = '/opt/LPF_analyses/'+analysisId+'/pdf_resources/virulence_data.csv';
    let plas_data = '/opt/LPF_analyses/'+analysisId+'/pdf_resources/plasmid_data.csv';
    let quast_data = '/opt/LPF_analyses/'+analysisId+'/pdf_resources/quast_report.csv';
    let contigs_jpg = '/opt/LPF_analyses/'+analysisId+'/contigs.jpg';
    let bacterial_parser = '/opt/LPF_analyses/'+analysisId+'/pdf_resources/bacterial_parser.json';
    let bact_parse_data =  require(bacterial_parser);
    const output_pdf_file = '/opt/LPF_analyses/'+analysisId+'/'+analysisId+'.pdf';

    var imageData = "";
        await fetch(dtu_logo_base64) //to fetch the encoded base64 text
        .then(response => response.text()).then(text => imageData = text)
    const { jsPDF } = require("jspdf"); // will automatically load the jspdf
    const { autoTable } = require("jspdf-autotable");  //load autotable in jspdf
    const docsize = 'a4';
    var doc = new jsPDF('l', 'pt', docsize);
    var base64 = require('base-64');
    doc.setTextColor(0,0,255);
    doc.setFontSize(24);
    var title = "LPF ANALYTICAL REPORT, Version: "+(bact_parse_data).version;
    doc.text(110, 60, title);
    doc.addImage(imageData,'PNG', 750, 15, 70, 70);
    doc.setTextColor(0,0,0);
    doc.setFontSize(14);
    var sample =  "The ID: "+(bact_parse_data).entry_id+"\nSample_name: "+(bact_parse_data).sample_name+"\nIdentified reference: "+(bact_parse_data).reference_header_text;
    doc.text(60, 120, sample);
    doc.setTextColor(0, 0, 255);
    doc.text(60, 200, "Sample Information");
    var sample_info = " City: "+(bact_parse_data).city+"\n Country: "+(bact_parse_data).country+"\n Date of Sampling: "+(bact_parse_data).collection_date+"\n Number of associated isolates: "+((bact_parse_data).isolate_list.length);
    doc.setTextColor(0, 0, 0);
    doc.text(80, 220, sample_info);
    doc.setTextColor(0, 0, 255);
    doc.text(60, 320, "CGE Results");
    var hits = " AMR genes in this sample: "+ ((bact_parse_data).resfinder_hits.length)+"\n virulence in this sample: "+((bact_parse_data).virulence_hits.length)+"\n Plasmids genes in this sample: "+((bact_parse_data).plasmid_hits.length)+"\n MLST: "+((bact_parse_data).mlst_type);
    doc.setTextColor(0, 0 ,0);
    doc.text(80, 340, hits);

    if (type == "assembly") {
        await generateAssemblyReport(quast_data, doc, imageData, contigs_jpg); // Assembly Report
    }
    else if (type == "alignment") {
        await generateAlignmentReport(amr_data, vir_data, plas_data, doc, imageData); // Alignment Report
    }
    doc.save(output_pdf_file);
}
