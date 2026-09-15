const SAMPLES = [
  { name: "sample_payslip.png", label: "Payslip", icon: "💰", type: "payslip" },
  { name: "sample_bank_statement.png", label: "Bank Statement", icon: "🏦", type: "bank_statement" },
  { name: "sample_tax_return.png", label: "Tax Return", icon: "📋", type: "tax_return" },
  { name: "sample_drivers_license.png", label: "Driver's License", icon: "🪪", type: "drivers_license" },
  { name: "sample_invoice.png", label: "Invoice", icon: "🧾", type: "invoice" },
  { name: "sample_utility_bill.png", label: "Utility Bill", icon: "⚡", type: "utility_bill" },
];

interface Props {
  onClassify: (filename: string) => void;
  loading: boolean;
}

export function SampleDocuments({ onClassify, loading }: Props) {
  return (
    <div
      className="rounded-2xl p-6"
      style={{
        background: "rgba(33, 30, 50, 0.5)",
        border: "1px solid #3a374f",
      }}
    >
      <h3 className="text-lg font-semibold mb-1" style={{ color: "#f0e9d9" }}>
        📁 Sample Documents
      </h3>
      <p className="text-sm mb-5" style={{ color: "#9b96b0" }}>
        Click any sample to classify instantly
      </p>

      <div className="grid grid-cols-2 gap-3">
        {SAMPLES.map((sample) => (
          <button
            key={sample.name}
            onClick={() => onClassify(sample.name)}
            disabled={loading}
            className="flex items-center gap-3 p-3.5 rounded-xl transition-all duration-200 text-left group"
            style={{
              background: "rgba(20, 18, 36, 0.5)",
              border: "1px solid #3a374f",
              opacity: loading ? 0.4 : 1,
              cursor: loading ? "not-allowed" : "pointer",
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.currentTarget.style.background = "rgba(42, 38, 64, 0.8)";
                e.currentTarget.style.borderColor = "#4a4768";
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(20, 18, 36, 0.5)";
              e.currentTarget.style.borderColor = "#3a374f";
            }}
          >
            <span className="text-2xl group-hover:scale-110 transition-transform">
              {sample.icon}
            </span>
            <div>
              <p className="text-sm font-medium" style={{ color: "#f0e9d9" }}>
                {sample.label}
              </p>
              <p className="text-xs" style={{ color: "#9b96b0" }}>
                Expected: {sample.type}
              </p>
            </div>
          </button>
        ))}
      </div>

      <button
        onClick={() =>
          SAMPLES.forEach((s, i) =>
            setTimeout(() => onClassify(s.name), i * 2000)
          )
        }
        disabled={loading}
        className="mt-5 w-full py-3 rounded-xl text-white font-semibold text-sm transition-all duration-200"
        style={{
          background: loading
            ? "rgba(255, 140, 42, 0.3)"
            : "linear-gradient(135deg, #ff8c2a, #ff6b00)",
          cursor: loading ? "not-allowed" : "pointer",
          opacity: loading ? 0.6 : 1,
          boxShadow: loading ? "none" : "0 0 20px rgba(255, 140, 42, 0.3)",
        }}
        onMouseEnter={(e) => {
          if (!loading) e.currentTarget.style.boxShadow = "0 0 30px rgba(255, 140, 42, 0.5)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.boxShadow = "0 0 20px rgba(255, 140, 42, 0.3)";
        }}
      >
        🚀 Classify All Samples
      </button>
    </div>
  );
}
