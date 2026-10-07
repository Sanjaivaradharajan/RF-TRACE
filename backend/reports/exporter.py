import typing as t

def generate_latex_report(report_data: t.Dict[str, t.Any]) -> str:
    """Generates LaTeX (.tex) report source string from signal analysis result dictionary."""
    file_info = report_data.get("file", {})
    params = report_data.get("params", {})
    mod = report_data.get("modulation", {})
    fec = report_data.get("fec", [])
    demod = report_data.get("demod", {})
    bits = report_data.get("bits", "")

    filename = file_info.get("name", "signal_capture.iq")
    mod_detected = mod.get("detected", "QPSK")
    confidence = float(mod.get("confidence", 0.0)) * 100
    probs = mod.get("probs", {})
    dsp_evidence = mod.get("dspEvidence", [])
    cnn_evidence = mod.get("cnnEvidence", [])
    ones_count = sum(1 for b in bits if b == '1')
    total_bits = len(bits) or 1

    def escape_tex(s: str) -> str:
        return (
            str(s)
            .replace("\\", "\\textbackslash ")
            .replace("_", "\\_")
            .replace("%", "\\%")
            .replace("$", "\\$")
            .replace("&", "\\&")
            .replace("#", "\\#")
        )

    lines = [
        "% =========================================================",
        f"% RF-TRACE SIGINT SIGNAL PROFILE ANALYSIS REPORT",
        f"% Capture File: {filename}",
        "% =========================================================",
        "\\documentclass[11pt, a4paper]{article}",
        "\\usepackage[utf8]{inputenc}",
        "\\usepackage[margin=0.8in]{geometry}",
        "\\usepackage{booktabs}",
        "\\usepackage{xcolor}",
        "\\usepackage{amsmath}",
        "\\usepackage{hyperref}",
        "\\usepackage{enumitem}",
        "",
        "\\definecolor{rfaccent}{RGB}{2, 132, 199}",
        "\\definecolor{rfheader}{RGB}{13, 19, 31}",
        "",
        "\\hypersetup{",
        "    colorlinks=true,",
        "    linkcolor=rfaccent,",
        "    urlcolor=rfaccent,",
        f"    pdftitle={{RF-TRACE Report - {escape_tex(filename)}}}",
        "}",
        "",
        "\\begin{document}",
        "",
        "\\begin{center}",
        "    {\\color{rfaccent}\\rule{\\linewidth}{2pt}}\\\\[0.4em]",
        "    {\\Huge \\bfseries \\color{rfheader} RF-TRACE SIGNAL PROFILE REPORT}\\\\[0.3em]",
        f"    {{\\large \\bfseries SIGINT Intelligence Summary \\quad | \\quad \\texttt{{{escape_tex(filename)}}}}}\\\\[0.4em]",
        "    {\\color{rfaccent}\\rule{\\linewidth}{1pt}}",
        "\\end{center}",
        "",
        "\\vspace{1em}",
        "",
        "\\section*{1. Capture File Metadata}",
        "\\begin{table}[h!]",
        "\\centering",
        "\\begin{tabular}{ll}",
        "\\toprule",
        "\\textbf{Attribute} & \\textbf{Value} \\\\",
        "\\midrule",
        f"File Name & \\texttt{{{escape_tex(filename)}}} \\\\",
        f"File Format & {escape_tex(file_info.get('format', 'IQ'))} \\\\",
        f"Sample Format & {escape_tex(file_info.get('sampleFormat', 'int16'))} \\\\",
        f"Duration & {file_info.get('durationS', 0.0):.2f} seconds \\\\",
        f"File Size & {file_info.get('sizeBytes', 0) / 1024 / 1024:.2f} MB \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
        "\\section*{2. Extracted Signal Parameters}",
        "\\begin{table}[h!]",
        "\\centering",
        "\\begin{tabular}{llll}",
        "\\toprule",
        "\\textbf{Parameter} & \\textbf{Measured Value} & \\textbf{Unit} & \\textbf{Provenance} \\\\",
        "\\midrule",
    ]

    for p in params.values():
        lbl = escape_tex(p.get("label", ""))
        val = escape_tex(p.get("value", "N/A"))
        unit = escape_tex(p.get("unit", ""))
        src = escape_tex(p.get("source", ""))
        lines.append(f"{lbl} & {val} & {unit} & {src} \\\\")

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
        "\\section*{3. Modulation Classification \\& Evidence}",
        "\\begin{itemize}[leftmargin=*]",
        f"    \\item \\textbf{{Detected Scheme:}} {{\\Large \\textbf{{\\color{{rfaccent}}{escape_tex(mod_detected)}}}}}",
        f"    \\item \\textbf{{Classification Confidence:}} {confidence:.1f}\\%",
        "\\end{itemize}",
        "",
        "\\subsection*{Class Probabilities}",
        "\\begin{table}[h!]",
        "\\centering",
        "\\begin{tabular}{lr}",
        "\\toprule",
        "\\textbf{Modulation Candidate} & \\textbf{Probability} \\\\",
        "\\midrule",
    ])

    for k, v in sorted(probs.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"{escape_tex(k)} & {float(v)*100:.1f}\\% \\\\")

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
        "\\subsection*{DSP Evidence Metrics}",
        "\\begin{table}[h!]",
        "\\centering",
        "\\begin{tabular}{lll}",
        "\\toprule",
        "\\textbf{Metric} & \\textbf{Value} & \\textbf{Diagnostic Note} \\\\",
        "\\midrule",
    ])

    for e in dsp_evidence:
        m_name = escape_tex(e.get("metric", ""))
        m_val = escape_tex(e.get("value", ""))
        m_note = escape_tex(e.get("note", ""))
        lines.append(f"{m_name} & {m_val} & {m_note} \\\\")

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
        "\\subsection*{AI CNN Recognition Evidence}",
        "\\begin{itemize}",
    ])

    for e in cnn_evidence:
        lines.append(f"    \\item {escape_tex(e)}")

    lines.extend([
        "\\end{itemize}",
        "",
        "\\section*{4. Forward Error Correction (FEC) Candidates}",
        "\\begin{table}[h!]",
        "\\centering",
        "\\begin{tabular}{lrl}",
        "\\toprule",
        "\\textbf{Scheme Name} & \\textbf{Likelihood Score} & \\textbf{Status} \\\\",
        "\\midrule",
    ])

    for f in fec:
        s_name = escape_tex(f.get("name", ""))
        s_score = float(f.get("score", 0.0)) * 100
        s_status = escape_tex(f.get("status", ""))
        lines.append(f"{s_name} & {s_score:.0f}\\% & {s_status} \\\\")

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
        "\\section*{5. Demodulation \\& Bit Analysis}",
        "\\begin{table}[h!]",
        "\\centering",
        "\\begin{tabular}{ll}",
        "\\toprule",
        "\\textbf{Metric} & \\textbf{Result} \\\\",
        "\\midrule",
        f"Demodulation Status & {escape_tex(demod.get('status', 'Complete'))} \\\\",
        f"Recovered Bit Count & {demod.get('recoveredBits', len(bits))} bits \\\\",
        f"Ones / Zeros & {ones_count} / {total_bits - ones_count} \\\\",
        f"Ones Ratio & {ones_count / total_bits:.3f} \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
        "\\vfill",
        "\\begin{center}",
        "    {\\small \\color{gray} Document generated automatically by RF-TRACE SIGINT Workstation Engine.}",
        "\\end{center}",
        "",
        "\\end{document}",
        "",
    ])

    return "\n".join(lines)
