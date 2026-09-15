1|import { useState, useCallback } from "react";
2|import { UploadZone } from "./components/UploadZone";
3|import { ResultCard } from "./components/ResultCard";
4|import { SampleDocuments } from "./components/SampleDocuments";
5|import { StatsPanel } from "./components/StatsPanel";
6|import { PipelineVisualizer } from "./components/PipelineVisualizer";
7|
8|export interface ClassificationResult {
9|  file_name: string;
10|  ocr: {
11|    text_preview: string;
12|    confidence: number;
13|    word_count: number;
14|    method: string;
15|  };
16|  classification: {
17|    type: string;
18|    confidence: number;
19|    sub_type: string;
20|    reasoning: string;
21|    latency_ms: number;
22|  };
23|  routing: {
24|    decision: string;
25|    reason: string;
26|  };
27|  total_latency_ms: number;
28|  timestamp?: string;
29|  errors?: string[];
30|}
31|
32|export default function App() {
33|  const [results, setResults] = useState<ClassificationResult[]>([]);
34|  const [loading, setLoading] = useState(false);
35|  const [currentStep, setCurrentStep] = useState("");
36|  const [error, setError] = useState<string | null>(null);
37|
38|  const classifyFile = useCallback(async (file: File) => {
39|    setLoading(true);
40|    setError(null);
41|    setCurrentStep("Uploading document...");
42|
43|    const formData = new FormData();
44|    formData.append("file", file);
45|
46|    try {
47|      setCurrentStep("Extracting text (OCR)...");
48|      await new Promise((r) => setTimeout(r, 500));
49|
50|      setCurrentStep("Classifying with AI...");
51|      const response = await fetch("/api/classify", {
52|        method: "POST",
53|        body: formData,
54|      });
55|
56|      if (!response.ok) {
57|        const err = await response.json();
58|        throw new Error(err.detail || "Classification failed");
59|      }
60|
61|      setCurrentStep("Routing decision...");
62|      const result: ClassificationResult = await response.json();
63|
64|      setResults((prev) => [result, ...prev]);
65|      setCurrentStep("Complete!");
66|    } catch (err) {
67|      setError(err instanceof Error ? err.message : "Unknown error");
68|    } finally {
69|      setLoading(false);
70|      setTimeout(() => setCurrentStep(""), 2000);
71|    }
72|  }, []);
73|
74|  const classifySample = useCallback(async (filename: string) => {
75|    setLoading(true);
76|    setError(null);
77|    setCurrentStep("Processing sample document...");
78|
79|    try {
80|      setCurrentStep("Extracting text (OCR)...");
81|      await new Promise((r) => setTimeout(r, 300));
82|
83|      setCurrentStep("Classifying with AI...");
84|      const response = await fetch(`/api/classify-sample/${filename}`, {
85|        method: "POST",
86|      });
87|
88|      if (!response.ok) {
89|        const err = await response.json();
90|        throw new Error(err.detail || "Classification failed");
91|      }
92|
93|      setCurrentStep("Routing decision...");
94|      const result: ClassificationResult = await response.json();
95|
96|      setResults((prev) => [result, ...prev]);
97|      setCurrentStep("Complete!");
98|    } catch (err) {
99|      setError(err instanceof Error ? err.message : "Unknown error");
100|    } finally {
101|      setLoading(false);
102|      setTimeout(() => setCurrentStep(""), 2000);
103|    }
104|  }, []);
105|
106|  return (
107|    <div className="min-h-screen" style={{ background: "#141224" }}>
108|      {/* Header */}
109|      <header
110|        className="sticky top-0 z-50 backdrop-blur-md"
111|        style={{
112|          background: "rgba(20, 18, 36, 0.85)",
113|          borderBottom: "1px solid #3a374f",
114|        }}
115|      >
116|        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
117|          <div className="flex items-center gap-4">
118|            <div
119|              className="w-11 h-11 rounded-xl flex items-center justify-center glow-pulse"
120|              style={{
121|                background: "linear-gradient(135deg, #ff8c2a, #ff6b00)",
122|                boxShadow: "0 0 15px rgba(255, 140, 42, 0.3)",
123|              }}
124|            >
125|              <span className="text-white text-xl">📄</span>
126|            </div>
127|            <div>
128|              <h1
129|                className="text-lg font-bold tracking-tight"
130|                style={{ color: "#f0e9d9" }}
131|              >
132|                AI Document Classifier{" "}
133|                <span style={{ color: "#ff8c2a" }}>AI</span> Classifier
134|              </h1>
135|              <p className="text-xs" style={{ color: "#9b96b0" }}>
136|                Document Intelligence Platform — POC
137|              </p>
138|            </div>
139|          </div>
140|          <div className="flex items-center gap-3">
141|            <span
142|              className="px-3 py-1.5 rounded-lg text-xs font-medium"
143|              style={{
144|                background: "rgba(255, 140, 42, 0.1)",
145|                color: "#ff8c2a",
146|                border: "1px solid rgba(255, 140, 42, 0.25)",
147|              }}
148|            >
149|              Claude Sonnet 5
150|            </span>
151|            <span
152|              className="px-3 py-1.5 rounded-lg text-xs font-medium"
153|              style={{
154|                background: "rgba(122, 117, 168, 0.1)",
155|                color: "#9b96b0",
156|                border: "1px solid #3a374f",
157|              }}
158|            >
159|              LangGraph Pipeline
160|            </span>
161|          </div>
162|        </div>
163|      </header>
164|
165|      <main className="max-w-7xl mx-auto px-6 py-8">
166|        {/* Pipeline Visualizer */}
167|        {(loading || currentStep) && (
168|          <PipelineVisualizer currentStep={currentStep} />
169|        )}
170|
171|        {/* Error */}
172|        {error && (
173|          <div
174|            className="mb-6 p-4 rounded-xl flex items-center gap-3"
175|            style={{
176|              background: "rgba(239, 68, 68, 0.08)",
177|              border: "1px solid rgba(239, 68, 68, 0.2)",
178|            }}
179|          >
180|            <span className="text-xl">⚠️</span>
181|            <div>
182|              <p className="font-medium" style={{ color: "#ef4444" }}>
183|                Classification Error
184|              </p>
185|              <p className="text-sm" style={{ color: "#ef4444cc" }}>
186|                {error}
187|              </p>
188|            </div>
189|          </div>
190|        )}
191|
192|        {/* Upload + Samples */}
193|        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
194|          <UploadZone onFileSelect={classifyFile} loading={loading} />
195|          <SampleDocuments onClassify={classifySample} loading={loading} />
196|        </div>
197|
198|        {/* Stats */}
199|        {results.length > 0 && <StatsPanel results={results} />}
200|
201|        {/* Results */}
202|        {results.length > 0 && (
203|          <div className="mt-8">
204|            <h2
205|              className="text-xl font-bold mb-5 flex items-center gap-2"
206|              style={{ color: "#f0e9d9" }}
207|            >
208|              <span>📊</span> Classification Results
209|              <span className="text-sm font-normal" style={{ color: "#9b96b0" }}>
210|                ({results.length} documents)
211|              </span>
212|            </h2>
213|            <div className="space-y-4">
214|              {results.map((result, i) => (
215|                <ResultCard key={i} result={result} />
216|              ))}
217|            </div>
218|          </div>
219|        )}
220|
221|        {/* Empty state */}
222|        {results.length === 0 && !loading && (
223|          <div className="text-center py-20">
224|            <div className="text-7xl mb-5 float">🤖</div>
225|            <h2
226|              className="text-xl font-semibold mb-2"
227|              style={{ color: "#e8e1d4" }}
228|            >
229|              No documents classified yet
230|            </h2>
231|            <p style={{ color: "#9b96b0" }}>
232|              Upload a document or try a sample above to see AI classification
233|              in action
234|            </p>
235|          </div>
236|        )}
237|      </main>
238|    </div>
239|  );
240|}
241|