import jsPDF from 'jspdf';
import type { AnalysisResult } from '../types';

/**
 * Downloads raw JSON report
 */
export function exportToJson(result: AnalysisResult) {
  const jsonStr = JSON.stringify(result, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${result.file.name.replace(/\.[^/.]+$/, '')}_rf-trace_report.json`;
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Generates and downloads a publication-ready LaTeX (.tex) report
 */
export function exportToLatex(result: AnalysisResult) {
  const escapeTex = (str: string) =>
    str.replace(/\\/g, '\\textbackslash ')
       .replace(/_/g, '\\_')
       .replace(/%/g, '\\%')
       .replace(/\$/g, '\\$')
       .replace(/&/g, '\\&')
       .replace(/#/g, '\\#');

  const dateStr = new Date().toISOString().split('T')[0];
  const ones = [...result.bits].filter((b) => b === '1').length;
  const modConfPct = (result.modulation.confidence * 100).toFixed(1);

  let tex = `% =========================================================
% RF-TRACE SIGINT SIGNAL PROFILE ANALYSIS REPORT
% Generated: ${dateStr}
% Capture File: ${result.file.name}
% =========================================================
\\documentclass[11pt, a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[margin=0.8in]{geometry}
\\usepackage{booktabs}
\\usepackage{xcolor}
\\usepackage{amsmath}
\\usepackage{hyperref}
\\usepackage{enumitem}

\\definecolor{rfaccent}{RGB}{2, 132, 199}
\\definecolor{rfheader}{RGB}{13, 19, 31}
\\definecolor{rfsub}{RGB}{71, 85, 105}

\\hypersetup{
    colorlinks=true,
    linkcolor=rfaccent,
    urlcolor=rfaccent,
    pdftitle={RF-TRACE Report - ${escapeTex(result.file.name)}}
}

\\begin{document}

\\begin{center}
    {\\color{rfaccent}\\rule{\\linewidth}{2pt}}\\\\[0.4em]
    {\\Huge \\bfseries \\color{rfheader} RF-TRACE SIGNAL PROFILE REPORT}\\\\[0.3em]
    {\\large \\bfseries SIGINT Intelligence Summary \\quad | \\quad \\texttt{${escapeTex(result.file.name)}}}\\\\[0.4em]
    {\\color{rfaccent}\\rule{\\linewidth}{1pt}}
\\end{center}

\\vspace{1em}

\\section*{1. Capture File Metadata}
\\begin{table}[h!]
\\centering
\\begin{tabular}{ll}
\\toprule
\\textbf{Attribute} & \\textbf{Value} \\\\
\\midrule
File Name & \\texttt{${escapeTex(result.file.name)}} \\\\
File Format & ${escapeTex(result.file.format)} \\\\
Sample Format & ${escapeTex(result.file.sampleFormat)} \\\\
Duration & ${(result.file.durationS ?? 0).toFixed(2)} seconds \\\\
File Size & ${(result.file.sizeBytes / 1024 / 1024).toFixed(2)} MB \\\\
\\bottomrule
\\end{tabular}
\\end{table}

\\section*{2. Extracted Signal Parameters}
\\begin{table}[h!]
\\centering
\\begin{tabular}{llll}
\\toprule
\\textbf{Parameter} & \\textbf{Measured Value} & \\textbf{Unit} & \\textbf{Provenance} \\\\
\\midrule
`;

  Object.values(result.params).forEach((p) => {
    tex += `${escapeTex(p.label)} & ${escapeTex(p.value ?? 'N/A')} & ${escapeTex(p.unit ?? '')} & ${escapeTex(p.source)} \\\\\n`;
  });

  tex += `\\bottomrule
\\end{tabular}
\\end{table}

\\section*{3. Modulation Classification \\& Evidence}
\\begin{itemize}[leftmargin=*]
    \\item \\textbf{Detected Scheme:} {\\Large \\textbf{\\color{rfaccent}${escapeTex(result.modulation.detected)}}}
    \\item \\textbf{Classification Confidence:} ${modConfPct}\\%
\\end{itemize}

\\subsection*{Class Probabilities}
\\begin{table}[h!]
\\centering
\\begin{tabular}{lr}
\\toprule
\\textbf{Modulation Candidate} & \\textbf{Probability} \\\\
\\midrule
`;

  Object.entries(result.modulation.probs)
    .sort((x, y) => y[1] - x[1])
    .forEach(([k, v]) => {
      tex += `${escapeTex(k)} & ${(v * 100).toFixed(1)}\\% \\\\\n`;
    });

  tex += `\\bottomrule
\\end{tabular}
\\end{table}

\\subsection*{DSP Evidence Metrics}
\\begin{table}[h!]
\\centering
\\begin{tabular}{lll}
\\toprule
\\textbf{Metric} & \\textbf{Value} & \\textbf{Diagnostic Note} \\\\
\\midrule
`;

  result.modulation.dspEvidence.forEach((e) => {
    tex += `${escapeTex(e.metric)} & ${escapeTex(e.value)} & ${escapeTex(e.note)} \\\\\n`;
  });

  tex += `\\bottomrule
\\end{tabular}
\\end{table}

\\subsection*{AI CNN Recognition Evidence}
\\begin{itemize}
`;
  result.modulation.cnnEvidence.forEach((e) => {
    tex += `    \\item ${escapeTex(e)}\n`;
  });

  tex += `\\end{itemize}

\\section*{4. Forward Error Correction (FEC) Candidates}
\\begin{table}[h!]
\\centering
\\begin{tabular}{lrl}
\\toprule
\\textbf{Scheme Name} & \\textbf{Likelihood Score} & \\textbf{Status} \\\\
\\midrule
`;

  result.fec.forEach((f) => {
    tex += `${escapeTex(f.name)} & ${(f.score * 100).toFixed(0)}\\% & ${escapeTex(f.status)} \\\\\n`;
  });

  tex += `\\bottomrule
\\end{tabular}
\\end{table}

\\section*{5. Demodulation \\& Bit Analysis}
\\begin{table}[h!]
\\centering
\\begin{tabular}{ll}
\\toprule
\\textbf{Metric} & \\textbf{Result} \\\\
\\midrule
Demodulation Status & ${escapeTex(result.demod.status)} \\\\
Recovered Bit Count & ${result.demod.recoveredBits} bits \\\\
Ones / Zeros & ${ones} / ${result.bits.length - ones} \\\\
Ones Ratio & ${(ones / result.bits.length).toFixed(3)} \\\\
\\bottomrule
\\end{tabular}
\\end{table}

\\vfill
\\begin{center}
    {\\small \\color{rfsub} Document generated automatically by RF-TRACE SIGINT Workstation Engine.}
\\end{center}

\\end{document}
`;

  const blob = new Blob([tex], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${result.file.name.replace(/\.[^/.]+$/, '')}_rf-trace_report.tex`;
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Generates and downloads a PDF document (.pdf)
 */
export function exportToPdf(result: AnalysisResult) {
  const doc = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' });
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 15;
  let y = 15;

  // Header Banner
  doc.setFillColor(13, 19, 31); // Dark slate header #0d131f
  doc.rect(0, 0, pageWidth, 26, 'F');

  doc.setTextColor(6, 182, 212); // Accent Cyan #06b6d4
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(16);
  doc.text('RF-TRACE | SIGINT Signal Profile Report', margin, 12);

  doc.setTextColor(203, 213, 225); // Slate subtext
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.text(`File: ${result.file.name}   |   Date: ${new Date().toISOString().split('T')[0]}`, margin, 19);

  y = 34;

  // Helper for section title
  const addSectionTitle = (title: string) => {
    if (y > 260) {
      doc.addPage();
      y = 20;
    }
    doc.setFillColor(2, 132, 199);
    doc.rect(margin, y, 3, 5, 'F');

    doc.setTextColor(2, 6, 23);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.text(title.toUpperCase(), margin + 5, y + 4);
    y += 8;
  };

  // Helper for key-value row
  const addRow = (key: string, value: string) => {
    if (y > 275) {
      doc.addPage();
      y = 20;
    }
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    doc.setTextColor(71, 85, 105);
    doc.text(key, margin + 2, y);

    doc.setFont('courier', 'bold');
    doc.setTextColor(2, 6, 23);
    doc.text(value, pageWidth - margin - 2, y, { align: 'right' });

    doc.setDrawColor(226, 232, 240);
    doc.setLineWidth(0.2);
    doc.line(margin + 2, y + 1.5, pageWidth - margin - 2, y + 1.5);
    y += 6;
  };

  // 1. File Info
  addSectionTitle('1. Input File Metadata');
  addRow('File Name', result.file.name);
  addRow('Format / Sample Format', `${result.file.format} (${result.file.sampleFormat})`);
  addRow('Duration', `${(result.file.durationS ?? 0).toFixed(2)} seconds`);
  addRow('Size', `${(result.file.sizeBytes / 1024 / 1024).toFixed(2)} MB`);
  y += 4;

  // 2. Parameters
  addSectionTitle('2. Extracted Signal Parameters');
  Object.values(result.params).forEach((p) => {
    addRow(p.label, `${p.value ?? 'N/A'} ${p.unit} [${p.source}]`);
  });
  y += 4;

  // 3. Modulation
  addSectionTitle('3. Modulation Recognition & Confidence');
  const confPct = Math.min(100, Math.max(0, result.modulation.confidence > 1 ? result.modulation.confidence : result.modulation.confidence * 100));

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(10);
  doc.setTextColor(2, 132, 199);
  doc.text(`Detected Scheme: ${result.modulation.detected}`, margin + 2, y);
  y += 5;

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.setTextColor(71, 85, 105);
  doc.text(`Confidence Score: ${confPct.toFixed(1)}%`, margin + 2, y);
  y += 3;

  // Draw Confidence progress bar
  doc.setFillColor(241, 245, 249);
  doc.rect(margin + 2, y, pageWidth - (margin * 2) - 4, 3, 'F');
  doc.setFillColor(2, 132, 199);
  const barWidth = ((pageWidth - (margin * 2) - 4) * confPct) / 100;
  doc.rect(margin + 2, y, barWidth, 3, 'F');
  y += 8;

  // Probabilities
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(9);
  doc.setTextColor(2, 6, 23);
  doc.text('Probability Breakdown:', margin + 2, y);
  y += 5;

  Object.entries(result.modulation.probs)
    .sort((x, y) => y[1] - x[1])
    .forEach(([k, v]) => {
      const p = Math.min(100, Math.max(0, v > 1 ? v : v * 100));
      addRow(`  Candidate: ${k}`, `${p.toFixed(1)}%`);
    });
  y += 4;

  // DSP & CNN Evidence
  addSectionTitle('4. Supporting Evidence');
  result.modulation.dspEvidence.forEach((e) => {
    addRow(e.metric, `${e.value} (${e.note})`);
  });
  y += 4;

  // 5. FEC Candidates
  addSectionTitle('5. FEC / Interleaving Evaluation');
  result.fec.forEach((f) => {
    addRow(f.name, `${(f.score * 100).toFixed(0)}% [${f.status}]`);
  });
  y += 4;

  // 6. Demodulation
  addSectionTitle('6. Demodulation Summary');
  addRow('Status', result.demod.status);
  addRow('Recovered Bits', `${result.demod.recoveredBits} bits`);

  const ones = [...result.bits].filter((b) => b === '1').length;
  addRow('Bit Distribution (1s / 0s)', `${ones} / ${result.bits.length - ones}`);
  addRow('Ones Ratio', (ones / result.bits.length).toFixed(3));

  // Footer page numbers
  const totalPages = doc.internal.pages.length - 1;
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.setTextColor(148, 163, 184);
    doc.text(`RF-TRACE SIGINT Engine  |  Page ${i} of ${totalPages}`, pageWidth / 2, 290, { align: 'center' });
  }

  doc.save(`${result.file.name.replace(/\.[^/.]+$/, '')}_rf-trace_report.pdf`);
}
