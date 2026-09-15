import { useState, useCallback } from "react";
import { UploadZone } from "./components/UploadZone";
import { ResultCard } from "./components/ResultCard";
import { SampleDocuments } from "./components/SampleDocuments";
import { StatsPanel } from "./components/StatsPanel";
import { PipelineVisualizer } from "./components/PipelineVisualizer";

export interface ClassificationResult {
  file_name: string;
  ocr: {
    text_preview: string;
    confidence: number;
    word_count: number;
    method: string;
  };
  classification: {
    type: string;
    confidence: number;
    sub_type: string;
    reasoning: string;
    latency_ms: number;
  };
  routing: {
    decision: string;
    reason: string;
  };
  total_latency_ms: number;
  timestamp?: string;
  errors?: string[];
}

export default function App() {
  const [results, setResults] = useState<ClassificationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState("");
  const [error, setError] = useState<string | null>(null);

  const classifyFile = useCallback(async (file: File) => {
    setLoading(true);
    setError(null);
    setCurrentStep("Uploading document...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setCurrentStep("Extracting text (OCR)...");
      await new Promise((r) => setTimeout(r, 500));

      setCurrentStep("Classifying with AI...");
      const response = await fetch("/api/classify", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Classification failed");
      }

      setCurrentStep("Routing decision...");
      const result: ClassificationResult = await response.json();

      setResults((prev) => [result, ...prev]);
      setCurrentStep("Complete!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
      setTimeout(() => setCurrentStep(""), 2000);
    }
  }, []);

  const classifySample = useCallback(async (filename: string) => {
    setLoading(true);
    setError(null);
    setCurrentStep("Processing sample document...");

    try {
      setCurrentStep("Extracting text (OCR)...");
      await new Promise((r) => setTimeout(r, 300));

      setCurrentStep("Classifying with AI...");
      const response = await fetch(`/api/classify-sample/${filename}`, {
        method: "POST",
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Classification failed");
      }

      setCurrentStep("Routing decision...");
      const result: ClassificationResult = await response.json();

      setResults((prev) => [result, ...prev]);
      setCurrentStep("Complete!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
      setTimeout(() => setCurrentStep(""), 2000);
    }
  }, []);

  return (
    <div className="min-h-screen" style={{ background: "#141224" }}>
      {/* Header */}
      <header
        className="sticky top-0 z-50 backdrop-blur-md"
        style={{
          background: "rgba(20, 18, 36, 0.85)",
          borderBottom: "1px solid #3a374f",
        }}
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div
              className="w-11 h-11 rounded-xl flex items-center justify-center glow-pulse"
              style={{
                background: "linear-gradient(135deg, #ff8c2a, #ff6b00)",
                boxShadow: "0 0 15px rgba(255, 140, 42, 0.3)",
              }}
            >
              <span className="text-white text-xl">📄</span>
            </div>
            <div>
              <h1
                className="text-lg font-bold tracking-tight"
                style={{ color: "#f0e9d9" }}
              >
                AI Document Classifier{" "}
                <span style={{ color: "#ff8c2a" }}>AI</span> Classifier
              </h1>
              <p className="text-xs" style={{ color: "#9b96b0" }}>
                Document Intelligence Platform — POC
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span
              className="px-3 py-1.5 rounded-lg text-xs font-medium"
              style={{
                background: "rgba(255, 140, 42, 0.1)",
                color: "#ff8c2a",
                border: "1px solid rgba(255, 140, 42, 0.25)",
              }}
            >
              Claude Sonnet 5
            </span>
            <span
              className="px-3 py-1.5 rounded-lg text-xs font-medium"
              style={{
                background: "rgba(122, 117, 168, 0.1)",
                color: "#9b96b0",
                border: "1px solid #3a374f",
              }}
            >
              LangGraph Pipeline
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Pipeline Visualizer */}
        {(loading || currentStep) && (
          <PipelineVisualizer currentStep={currentStep} />
        )}

        {/* Error */}
        {error && (
          <div
            className="mb-6 p-4 rounded-xl flex items-center gap-3"
            style={{
              background: "rgba(239, 68, 68, 0.08)",
              border: "1px solid rgba(239, 68, 68, 0.2)",
            }}
          >
            <span className="text-xl">⚠️</span>
            <div>
              <p className="font-medium" style={{ color: "#ef4444" }}>
                Classification Error
              </p>
              <p className="text-sm" style={{ color: "#ef4444cc" }}>
                {error}
              </p>
            </div>
          </div>
        )}

        {/* Upload + Samples */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <UploadZone onFileSelect={classifyFile} loading={loading} />
          <SampleDocuments onClassify={classifySample} loading={loading} />
        </div>

        {/* Stats */}
        {results.length > 0 && <StatsPanel results={results} />}

        {/* Results */}
        {results.length > 0 && (
          <div className="mt-8">
            <h2
              className="text-xl font-bold mb-5 flex items-center gap-2"
              style={{ color: "#f0e9d9" }}
            >
              <span>📊</span> Classification Results
              <span className="text-sm font-normal" style={{ color: "#9b96b0" }}>
                ({results.length} documents)
              </span>
            </h2>
            <div className="space-y-4">
              {results.map((result, i) => (
                <ResultCard key={i} result={result} />
              ))}
            </div>
          </div>
        )}

        {/* Empty state */}
        {results.length === 0 && !loading && (
          <div className="text-center py-20">
            <div className="text-7xl mb-5 float">🤖</div>
            <h2
              className="text-xl font-semibold mb-2"
              style={{ color: "#e8e1d4" }}
            >
              No documents classified yet
            </h2>
            <p style={{ color: "#9b96b0" }}>
              Upload a document or try a sample above to see AI classification
              in action
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
