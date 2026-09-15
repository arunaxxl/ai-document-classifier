import type { ClassificationResult } from "../App";

interface Props {
  results: ClassificationResult[];
}

export function StatsPanel({ results }: Props) {
  const totalDocs = results.length;
  const avgConfidence = Math.round(
    results.reduce((s, r) => s + r.classification.confidence, 0) / totalDocs
  );
  const avgLatency = Math.round(
    results.reduce((s, r) => s + r.total_latency_ms, 0) / totalDocs
  );
  const autoAccepted = results.filter(
    (r) => r.routing.decision === "auto_accept"
  ).length;
  const needsReview = results.filter(
    (r) => r.routing.decision === "review"
  ).length;
  const rejected = results.filter(
    (r) => r.routing.decision === "reject"
  ).length;
  const autoAcceptRate = Math.round((autoAccepted / totalDocs) * 100);

  const typeDistribution = results.reduce(
    (acc, r) => {
      const t = r.classification.type;
      acc[t] = (acc[t] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="mb-8">
      <h2
        className="text-xl font-bold mb-5 flex items-center gap-2"
        style={{ color: "#f0e9d9" }}
      >
        <span>📈</span> Pipeline Stats
      </h2>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <MetricCard label="Documents" value={totalDocs.toString()} icon="📄" color="#ff8c2a" />
        <MetricCard
          label="Avg Confidence"
          value={`${avgConfidence}%`}
          icon="🎯"
          color={avgConfidence >= 85 ? "#22c55e" : avgConfidence >= 60 ? "#eab308" : "#ef4444"}
        />
        <MetricCard label="Avg Latency" value={`${avgLatency}ms`} icon="⚡" color="#7a75a8" />
        <MetricCard label="Auto-Accepted" value={`${autoAcceptRate}%`} icon="✅" color="#22c55e" />
        <MetricCard label="Needs Review" value={needsReview.toString()} icon="⚠️" color="#eab308" />
      </div>

      {/* Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Type Distribution */}
        <div
          className="rounded-xl p-5"
          style={{ background: "rgba(33, 30, 50, 0.5)", border: "1px solid #3a374f" }}
        >
          <h4 className="text-sm font-medium mb-4" style={{ color: "#9b96b0" }}>
            Document Type Distribution
          </h4>
          <div className="space-y-3">
            {Object.entries(typeDistribution)
              .sort(([, a], [, b]) => b - a)
              .map(([type, count]) => (
                <div key={type} className="flex items-center gap-3">
                  <span className="text-xs w-28 truncate capitalize" style={{ color: "#9b96b0" }}>
                    {type.replace(/_/g, " ")}
                  </span>
                  <div
                    className="flex-1 h-2 rounded-full overflow-hidden"
                    style={{ background: "rgba(58, 55, 79, 0.5)" }}
                  >
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${(count / totalDocs) * 100}%`,
                        background: "linear-gradient(90deg, #ff8c2a, #ff6b00)",
                      }}
                    />
                  </div>
                  <span className="text-xs w-8 text-right" style={{ color: "#9b96b0" }}>
                    {count}
                  </span>
                </div>
              ))}
          </div>
        </div>

        {/* Routing Distribution */}
        <div
          className="rounded-xl p-5"
          style={{ background: "rgba(33, 30, 50, 0.5)", border: "1px solid #3a374f" }}
        >
          <h4 className="text-sm font-medium mb-4" style={{ color: "#9b96b0" }}>
            Routing Decisions
          </h4>
          <div className="space-y-3">
            <RouteBar label="Auto-Accepted" count={autoAccepted} total={totalDocs} color="#22c55e" />
            <RouteBar label="Needs Review" count={needsReview} total={totalDocs} color="#eab308" />
            <RouteBar label="Rejected" count={rejected} total={totalDocs} color="#ef4444" />
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: string;
  icon: string;
  color: string;
}) {
  return (
    <div
      className="rounded-xl p-4"
      style={{ background: "rgba(33, 30, 50, 0.5)", border: "1px solid #3a374f" }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xl">{icon}</span>
        <span className="text-2xl font-bold" style={{ color }}>{value}</span>
      </div>
      <p className="text-xs" style={{ color: "#9b96b0" }}>{label}</p>
    </div>
  );
}

function RouteBar({
  label,
  count,
  total,
  color,
}: {
  label: string;
  count: number;
  total: number;
  color: string;
}) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm" style={{ color: "#e8e1d4" }}>{label}</span>
        <span className="text-sm" style={{ color: "#9b96b0" }}>
          {count} ({pct}%)
        </span>
      </div>
      <div
        className="h-2 rounded-full overflow-hidden"
        style={{ background: "rgba(58, 55, 79, 0.5)" }}
      >
        <div
          className="h-full rounded-full transition-all duration-1000"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}
