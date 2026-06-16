import type { WeatherLocation } from "../types/solar";

export const weatherLocations: WeatherLocation[] = [
  {
    id: "seoul",
    name: "서울",
    latitude: 37.5665,
    longitude: 126.978,
    note: "도심형 소형 태양광 기준 위치",
  },
  {
    id: "busan",
    name: "부산",
    latitude: 35.1796,
    longitude: 129.0756,
    note: "해안 바람 영향을 확인하기 좋은 위치",
  },
  {
    id: "jeju",
    name: "제주",
    latitude: 33.4996,
    longitude: 126.5312,
    note: "구름과 강수 변화가 큰 위치",
  },
  {
    id: "daejeon",
    name: "대전",
    latitude: 36.3504,
    longitude: 127.3845,
    note: "내륙형 기준 위치",
  },
];

export const defaultWeatherLocation = weatherLocations[0];

export function findWeatherLocation(locationId: string) {
  return weatherLocations.find((location) => location.id === locationId) ?? defaultWeatherLocation;
}
