export function calculateSunPosition(time: number) {
  const clampedTime = Math.max(6, Math.min(18, time));
  const sunAzimuth = ((clampedTime - 12) / 6) * 90;
  const normalizedElevation = Math.sin(((clampedTime - 6) / 12) * Math.PI);
  const sunElevation = Math.max(0, normalizedElevation * 70);

  return {
    sunAzimuth: Number(sunAzimuth.toFixed(1)),
    sunElevation: Number(sunElevation.toFixed(1)),
  };
}
