"use client";

import { ChangeEvent, useMemo, useState } from "react";
import Button from "@/components/Button";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080";

const humanize = (value: string | null | undefined) =>
  (value ?? "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (match) => match.toUpperCase())
    .trim();

type AnalyzeResponse = {
  risk_level: string;
  score: number;
  triggers: Record<string, string[]>;
  rationale: string;
  recommendations: string[];
  raw?: Record<string, unknown>;
};

type OcrResponse = {
  text: string;
  spans: unknown[];
  confidences: number[];
};

export default function AppDashboard() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [extractedText, setExtractedText] = useState("");
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [analysisPayload, setAnalysisPayload] = useState<Record<string, unknown> | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const hasAnalysis = useMemo(() => !!analysis, [analysis]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setSelectedFile(file ?? null);
    setStatus(null);
    setError(null);
    setAnalysis(null);
    setAnalysisPayload(null);
    if (!file) {
      setExtractedText("");
    }
  };

  const runOcrAndAnalyze = async () => {
    if (!selectedFile && !extractedText.trim()) {
      setError("Please upload an image or provide text to analyze.");
      return;
    }

    setIsProcessing(true);
    setError(null);
    setStatus("Processing upload…");

    let textForAnalysis = extractedText;

    try {
      if (selectedFile) {
        const formData = new FormData();
        formData.append("image", selectedFile);

        const ocrResponse = await fetch(`${API_BASE_URL}/api/ocr`, {
          method: "POST",
          body: formData
        });

        if (!ocrResponse.ok) {
          const details = await ocrResponse.json().catch(() => ({}));
          throw new Error(details.detail || "OCR request failed");
        }

        const data = (await ocrResponse.json()) as OcrResponse;
        textForAnalysis = data.text || "";
        setExtractedText(textForAnalysis);
        setStatus("Text extracted. Running analysis…");
      } else {
        setStatus("Running analysis…");
      }

      const analyzeResponse = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textForAnalysis })
      });

      if (!analyzeResponse.ok) {
        const details = await analyzeResponse.json().catch(() => ({}));
        throw new Error(details.detail || "Analysis request failed");
      }

      const analysisData = (await analyzeResponse.json()) as AnalyzeResponse & {
        raw?: Record<string, unknown>;
      };

      setAnalysis({
        ...analysisData,
        risk_level: humanize(analysisData.risk_level)
      });
      setAnalysisPayload(analysisData.raw ?? analysisData);
      setStatus("Analysis complete.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error during analysis.");
      setStatus(null);
    } finally {
      setIsProcessing(false);
    }
  };

  const exportReport = async () => {
    if (!hasAnalysis || !analysisPayload) {
      return;
    }

    setIsExporting(true);
    setError(null);
    setStatus("Generating report…");

    try {
      const response = await fetch(`${API_BASE_URL}/api/report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: extractedText, analysis: analysisPayload })
      });

      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(details.detail || "Failed to generate report");
      }

      const blob = await response.blob();
      const filename =
        response.headers.get("x-leafcheck-filename") || "LeafCheck_Report.pdf";
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setStatus("Report downloaded.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error while exporting.");
      setStatus(null);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background-dark/5 px-4 py-10 md:px-10">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8">
        <header className="flex flex-col gap-2">
          <h1 className="text-3xl font-black tracking-tight text-dark-grey">LeafCheck Workspace</h1>
          <p className="max-w-2xl text-base text-neutral-grey">
            Upload marketing materials for OCR, run a greenwashing risk analysis, and export a shareable PDF report powered by the LeafCheck engine.
          </p>
        </header>

        <section className="rounded-xl border border-neutral-grey/30 bg-background-light p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-dark-grey">1. Upload Creative</h2>
          <p className="mt-2 text-sm text-neutral-grey">
            Supported formats: PNG, JPG, WebP, PDF (first page). The backend uses RapidOCR preprocessing for optimal extraction.
          </p>
          <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-center">
            <input
              type="file"
              accept="image/*,application/pdf"
              onChange={handleFileChange}
              className="block w-full max-w-md rounded-lg border border-neutral-grey/40 bg-white px-3 py-2 text-sm text-dark-grey focus:border-primary focus:outline-none"
            />
            <Button onClick={runOcrAndAnalyze} disabled={isProcessing}>
              {isProcessing ? "Processing…" : "Run OCR & Analyze"}
            </Button>
          </div>
          <p className="mt-2 text-xs text-neutral-grey">
            Prefer pasting text? Skip the upload and paste directly into the editor below, then click “Run OCR & Analyze”.
          </p>
        </section>

        <section className="rounded-xl border border-neutral-grey/30 bg-background-light p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-dark-grey">2. Review & Edit Text</h2>
          <textarea
            value={extractedText}
            onChange={(event) => setExtractedText(event.target.value)}
            rows={10}
            className="mt-4 w-full rounded-lg border border-neutral-grey/40 bg-white p-4 text-sm text-dark-grey focus:border-primary focus:outline-none"
            placeholder="Extracted text will appear here. You can edit before analyzing."
          />
        </section>

        <section className="rounded-xl border border-neutral-grey/30 bg-background-light p-6 shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-dark-grey">3. Analysis Output</h2>
              <p className="text-sm text-neutral-grey">
                Results combine heuristic rules and the existing LeafCheck transformer nudges.
              </p>
            </div>
            <Button
              onClick={exportReport}
              disabled={!hasAnalysis || isExporting}
              variant="secondary"
            >
              {isExporting ? "Exporting…" : "Export PDF"}
            </Button>
          </div>

          {status && (
            <div className="mt-4 rounded-lg border border-primary/50 bg-primary/10 px-3 py-2 text-sm text-dark-grey">
              {status}
            </div>
          )}

          {error && (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          {analysis && (
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <div className="rounded-lg border border-neutral-grey/30 bg-white p-4">
                <h3 className="text-lg font-semibold text-dark-grey">Summary</h3>
                <div className="mt-3 space-y-2 text-sm">
                  <p>
                    <span className="font-medium text-dark-grey">Risk Level:</span> {analysis.risk_level}
                  </p>
                  <p>
                    <span className="font-medium text-dark-grey">Score:</span> {analysis.score}
                  </p>
                  <p>
                    <span className="font-medium text-dark-grey">Rationale:</span> {analysis.rationale}
                  </p>
                  {analysis.recommendations.length > 0 && (
                    <div className="space-y-1">
                      <p className="font-medium text-dark-grey">Recommendations:</p>
                      <ul className="list-disc space-y-1 pl-5 text-neutral-grey">
                        {analysis.recommendations.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
              <div className="rounded-lg border border-neutral-grey/30 bg-white p-4">
                <h3 className="text-lg font-semibold text-dark-grey">Triggers</h3>
                <ul className="mt-3 space-y-2 text-sm text-dark-grey">
                  {Object.entries(analysis.triggers || {}).map(([category, values]) => (
                    <li key={category} className="rounded-md bg-primary/10 px-3 py-2">
                      <span className="font-medium capitalize">{humanize(category)}</span>
                      <span className="ml-1 text-neutral-grey">({values.length})</span>
                      <div className="mt-1 text-xs text-dark-grey/80">
                        {values.join(", ") || "—"}
                      </div>
                    </li>
                  ))}
                  {Object.keys(analysis.triggers || {}).length === 0 && (
                    <li className="rounded-md bg-primary/10 px-3 py-2 text-sm text-dark-grey">
                      No triggers detected.
                    </li>
                  )}
                </ul>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
