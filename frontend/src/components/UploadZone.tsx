import { useRef, useState } from "react";

interface Props {
  onFileSelect: (file: File) => void;
  loading: boolean;
}

export function UploadZone({ onFileSelect, loading }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) onFileSelect(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <div
      className="relative rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-300 cursor-pointer"
      style={{
        background: dragOver
          ? "rgba(255, 140, 42, 0.06)"
          : "rgba(33, 30, 50, 0.5)",
        borderColor: dragOver ? "#ff8c2a" : "#3a374f",
        transform: dragOver ? "scale(1.02)" : "scale(1)",
        opacity: loading ? 0.5 : 1,
        pointerEvents: loading ? "none" : "auto",
      }}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp"
        className="hidden"
        onChange={handleChange}
      />

      <div
        className="w-20 h-20 mx-auto mb-5 rounded-2xl flex items-center justify-center"
        style={{
          background: "linear-gradient(135deg, rgba(255,140,42,0.15), rgba(255,140,42,0.05))",
          border: "1px solid rgba(255, 140, 42, 0.2)",
        }}
      >
        <span className="text-4xl">{loading ? "⏳" : "📤"}</span>
      </div>

      <h3 className="text-lg font-semibold mb-2" style={{ color: "#f0e9d9" }}>
        {loading ? "Processing..." : "Upload Document"}
      </h3>

      <p className="text-sm mb-5" style={{ color: "#9b96b0" }}>
        Drag & drop or click to select
      </p>

      <div className="flex flex-wrap justify-center gap-2">
        {["PDF", "PNG", "JPG", "TIFF"].map((ext) => (
          <span
            key={ext}
            className="px-3 py-1.5 rounded-lg text-xs font-medium"
            style={{
              background: "rgba(122, 117, 168, 0.1)",
              color: "#9b96b0",
              border: "1px solid #3a374f",
            }}
          >
            .{ext.toLowerCase()}
          </span>
        ))}
      </div>
    </div>
  );
}
