import { ScanSearch } from "lucide-react";
import { Metric } from "./Metric";
import type { VisionState } from "../types/solar";

const classLabels: Record<string, string> = {
  sky_clear: "맑은 하늘",
  sky_cloudy: "흐린 하늘",
  panel_clean: "정상 패널",
  panel_soiling: "패널 오염",
  panel_partial_shadow: "부분 음영",
  sun_cloud_block: "구름 가림",
};

export function VisionPanel({ vision }: { vision: VisionState }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <ScanSearch size={18} />
        <h2>비전</h2>
      </div>
      <div className="metric-grid">
        <Metric label="구름" value={vision.cloudDetected ? "감지" : "정상"} tone={vision.cloudDetected ? "warn" : "good"} />
        <Metric label="오염" value={vision.soilingDetected ? "의심" : "정상"} tone={vision.soilingDetected ? "warn" : "good"} />
        <Metric label="음영" value={vision.shadeDetected ? "의심" : "정상"} tone={vision.shadeDetected ? "warn" : "good"} />
        <Metric label="주요 분류" value={formatClassName(vision.primaryClass)} />
        <Metric label="신뢰도" value={formatConfidence(vision.confidence)} />
      </div>
      {vision.detections && vision.detections.length > 0 ? (
        <ul className="compact-list">
          {vision.detections.map((detection) => (
            <li key={detection.className}>
              <span>{formatClassName(detection.className)}</span>
              <strong>{formatConfidence(detection.confidence)}</strong>
            </li>
          ))}
        </ul>
      ) : null}
      <p className="panel-note">{vision.note}</p>
    </section>
  );
}

function formatClassName(className?: string) {
  if (!className) return "가상 데이터";
  return classLabels[className] ?? className;
}

function formatConfidence(confidence?: number) {
  if (confidence === undefined) return "-";
  return `${Math.round(confidence * 100)}%`;
}
