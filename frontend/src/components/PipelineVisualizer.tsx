const STEPS = [
  { key: "upload", label: "Upload", icon: "📤" },
  { key: "ocr", label: "OCR", icon: "🔍" },
  { key: "classify", label: "Classify", icon: "🤖" },
  { key: "route", label: "Route", icon: "🔀" },
  { key: "done", label: "Done", icon: "✅" },
];

function getActiveStep(currentStep: string): number {
  const s = currentStep.toLowerCase();
  if (s.includes("upload")) return 0;
  if (s.includes("ocr") || s.includes("extract")) return 1;
  if (s.includes("classif") || s.includes("ai")) return 2;
  if (s.includes("rout")) return 3;
  if (s.includes("complete")) return 4;
  return 2;
}

export function PipelineVisualizer({ currentStep }: { currentStep: string }) {
  const activeIdx = getActiveStep(currentStep);

  return (
    <div
      className="mb-8 p-5 rounded-2xl"
      style={{
        background: "rgba(33, 30, 50, 0.5)",
        border: "1px solid #3a374f",
      }}
    >
      <div className="flex items-center justify-between">
        {STEPS.map((step, i) => (
          <div key={step.key} className="flex items-center flex-1">
            {/* Step */}
            <div className="flex flex-col items-center">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center text-xl transition-all duration-500"
                style={{
                  background:
                    i < activeIdx
                      ? "rgba(34, 197, 94, 0.15)"
                      : i === activeIdx
                        ? "rgba(255, 140, 42, 0.15)"
                        : "rgba(20, 18, 36, 0.5)",
                  border: `2px solid ${
                    i < activeIdx
                      ? "#22c55e"
                      : i === activeIdx
                        ? "#ff8c2a"
                        : "#3a374f"
                  }`,
                  transform: i === activeIdx ? "scale(1.1)" : "scale(1)",
                  boxShadow:
                    i === activeIdx
                      ? "0 0 15px rgba(255, 140, 42, 0.3)"
                      : "none",
                }}
              >
                {i < activeIdx ? "✓" : step.icon}
              </div>
              <span
                className="text-xs mt-2 font-medium"
                style={{
                  color: i <= activeIdx ? "#f0e9d9" : "#4a4768",
                }}
              >
                {step.label}
              </span>
            </div>

            {/* Connector */}
            {i < STEPS.length - 1 && (
              <div className="flex-1 mx-2 mt-[-20px]">
                <div
                  className="h-0.5 rounded-full transition-all duration-500"
                  style={{
                    background: i < activeIdx ? "#22c55e" : "#3a374f",
                  }}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Current step text */}
      <div className="mt-4 text-center">
        <span
          className="text-sm"
          style={{ color: "#ff8c2a", animation: "pulse 1.5s ease-in-out infinite" }}
        >
          {currentStep}
        </span>
      </div>
    </div>
  );
}
