"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    setResults(data);
    setLoading(false);
  };

  const handleDownload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/api/report", {
      method: "POST",
      body: formData,
    });

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = response.headers.get("x-greencheck-filename") || "GreenCheck_Report.pdf";
    a.click();
    URL.revokeObjectURL(url);
  };


  return (
    <div className="container mx-auto p-4">
      <header className="text-center mb-8">
        <h1 className="text-3xl font-black tracking-tight text-dark-grey">GreenCheck Workspace</h1>
        <p className="text-muted-foreground">
          Upload marketing materials for OCR, run a greenwashing risk analysis, and export a shareable PDF report powered by the GreenCheck engine.
        </p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card>
          <CardHeader>
            <CardTitle>Upload Creative</CardTitle>
          </CardHeader>
          <CardContent>
            <Input type="file" onChange={handleFileChange} />
            <Button onClick={handleAnalyze} disabled={!file || loading} className="mt-4">
              {loading ? "Analyzing..." : "Analyze"}
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
          </CardHeader>
          <CardContent>
            {results ? (
              <div>
                <p>Score: {results.score}</p>
                <p>Level: {results.level}</p>
                <Button onClick={handleDownload} className="mt-4">Download Report</Button>
              </div>
            ) : (
              <p>
                Results combine heuristic rules and the existing GreenCheck transformer nudges.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
