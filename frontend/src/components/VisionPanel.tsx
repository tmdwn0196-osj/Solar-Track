import { ScanSearch } from "lucide-react";
import { Metric } from "./Metric";
import type { VisionState } from "../types/solar";

export function VisionPanel({ vision }: { vision: VisionState }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <ScanSearch size={18} />
        <h2>Vision</h2>
      </div>
      <div className="metric-grid">
        <Metric label="구름" value={vision.cloudDetected ? "감지" : "정상"} tone={vision.cloudDetected ? "warn" : "good"} />
        <Metric label="오염" value={vision.soilingDetected ? "의심" : "정상"} tone={vision.soilingDetected ? "warn" : "good"} />
        <Metric label="음영" value={vision.shadeDetected ? "의심" : "정상"} tone={vision.shadeDetected ? "warn" : "good"} />
        <Metric label="Class" value={vision.primaryClass ?? "virtual"} />
        <Metric label="신뢰도" value={formatConfidence(vision.confidence)} />
      </div>
      {vision.detections && vision.detections.length > 0 ? (
        <ul className="compact-list">
          {vision.detections.map((detection) => (
            <li key={detection.className}>
              <span>{detection.className}</span>
              <strong>{formatConfidence(detection.confidence)}</strong>
            </li>
          ))}
        </ul>
      ) : null}
      <p className="panel-note">{vision.note}</p>
    </section>
  );
}

function formatConfidence(confidence?: number) {
  if (confidence === undefined) return "-";
  return `${Math.round(confidence * 100)}%`;
}
