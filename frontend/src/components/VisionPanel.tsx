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
      </div>
      <p className="panel-note">{vision.note}</p>
    </section>
  );
}
