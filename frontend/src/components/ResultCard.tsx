import type { ClassificationResult } from "../App";

const DOC_TYPE_ICONS: Record<string, string> = {
  payslip: "💰",
  bank_statement: "🏦",
  tax_return: "📋",
  drivers_license: "🪪",
  passport: "🛂",
  invoice: "🧾",
  utility_bill: "⚡",
  trust_deed: "📜",
  company_registration: "🏢",
  financial_statement: "📊",
  letter_of_offer: "✉️",
  contract: "📝",
  unknown: "❓",
};

const ROUTE_CONFIG: Record<
  string,
  { label: string; color: string; bg: string; border: string; icon: string }
> = {
  auto_accept: {
    label: "Auto-Accepted",
    color: "#22c55e",
    bg: "rgba(34, 197, 94, 0.08)",
    border: "rgba(34, 197, 94, 0.2)",
    icon: "✅",
  },
  review: {
    label: "Needs Review",
    color: "#eab308",
    bg: "rgba(234, 179, 8, 0.08)",
    border: "rgba(234, 179, 8, 0.2)",
    icon: "⚠️",
  },
  reject: {
    label: "Rejected",
    color: "#ef4444",
    bg: "rgba(239, 68, 68, 0.08)",
    border: "rgba(239, 68, 68, 0.2)",
    icon: "❌",
  },
};

function ConfidenceBar({ value }: { value: number }) {
  const color =
    value >= 85 ? "#22c55e" : value >= 60 ? "#eab308" : "#ef4444";

  return (
    <div
      className="w-full h-2 rounded-full overflow-hidden"
      style={{ background: "rgba(58, 55, 79, 0.5)" }}
    >
      <div
        className="h-full rounded-full transition-all duration-1000"
        style={{ width: `${value}%`, background: color }}
      />
    </div>
  );
}

export function ResultCard({ result }: { result: ClassificationResult }) {
  const { classification, routing, ocr, total_latency_ms } = result;
  const route = ROUTE_CONFIG[routing.decision] || ROUTE_CONFIG.reject;
  const icon = DOC_TYPE_ICONS[classification.type] || "❓";

  return (
    <div
      className="rounded-2xl overflow-hidden"
      style={{
        background: "rgba(33, 30, 50, 0.6)",
        border: "1px solid #3a374f",
      }}
    >
      {/* Header */}
      <div className="p-5 flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <div
            className="text-4xl w-14 h-14 rounded-xl flex items-center justify-center"
            style={{
              background: "rgba(255, 140, 42, 0.1)",
              border: "1px solid rgba(255, 140, 42, 0.2)",
            }}
          >
            {icon}
          </div>
          <div>
            <h3
              className="text-lg font-bold capitalize"
              style={{ color: "#f0e9d9" }}
            >
              {classification.type.replace(/_/g, " ")}
            </h3>
            <p className="text-sm" style={{ color: "#9b96b0" }}>
              {result.file_name}
            </p>
          </div>
        </div>

        <div
          className="px-4 py-2 rounded-xl text-sm font-medium"
          style={{
            background: route.bg,
            color: route.color,
            border: `1px solid ${route.border}`,
          }}
        >
          {route.icon} {route.label}
        </div>
      </div>

      {/* Confidence */}
      <div className="px-5 pb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm" style={{ color: "#9b96b0" }}>
            AI Confidence
          </span>
          <span className="text-sm font-bold" style={{ color: "#f0e9d9" }}>
            {classification.confidence}%
          </span>
        </div>
        <ConfidenceBar value={classification.confidence} />
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 px-5 pb-4">
        {[
          { label: "Sub Type", value: classification.sub_type || "—" },
          { label: "OCR Confidence", value: `${ocr.confidence}%` },
          { label: "Words Extracted", value: ocr.word_count.toString() },
          { label: "Total Latency", value: `${total_latency_ms}ms` },
        ].map((item) => (
          <div
            key={item.label}
            className="p-3 rounded-xl"
            style={{ background: "rgba(20, 18, 36, 0.5)" }}
          >
            <p className="text-xs mb-1" style={{ color: "#9b96b0" }}>
              {item.label}
            </p>
            <p className="text-sm font-medium" style={{ color: "#f0e9d9" }}>
              {item.value}
            </p>
          </div>
        ))}
      </div>

      {/* Reasoning */}
      <div className="px-5 pb-4">
        <div
          className="p-3 rounded-xl"
          style={{
            background: "rgba(20, 18, 36, 0.3)",
            border: "1px solid #3a374f",
          }}
        >
          <p className="text-xs mb-1" style={{ color: "#9b96b0" }}>
            AI Reasoning
          </p>
          <p className="text-sm" style={{ color: "#e8e1d4" }}>
            {classification.reasoning}
          </p>
        </div>
      </div>

      {/* Routing Reason */}
      <div className="px-5 pb-4">
        <div
          className="p-3 rounded-xl"
          style={{ background: route.bg, border: `1px solid ${route.border}` }}
        >
          <p className="text-xs mb-1" style={{ color: "#9b96b0" }}>
            Routing Decision
          </p>
          <p className="text-sm" style={{ color: route.color }}>
            {routing.reason}
          </p>
        </div>
      </div>

      {/* OCR Preview */}
      <details className="px-5 pb-5">
        <summary
          className="text-xs cursor-pointer"
          style={{ color: "#9b96b0" }}
        >
          View OCR Text Preview
        </summary>
        <pre
          className="mt-2 p-3 rounded-xl text-xs overflow-x-auto max-h-40"
          style={{
            background: "rgba(20, 18, 36, 0.5)",
            color: "#9b96b0",
          }}
        >
          {ocr.text_preview || "(no text extracted)"}
        </pre>
      </details>
    </div>
  );
}
