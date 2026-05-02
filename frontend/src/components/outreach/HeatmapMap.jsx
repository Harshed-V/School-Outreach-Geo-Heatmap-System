import { useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from "react-leaflet";
import { getScoreColor } from "../../utils/scoreColor";
import "leaflet/dist/leaflet.css";

export const HeatmapMap = ({ districts, focused, onSelect }) => {
  const center = [11.127123, 78.6569];
  const visibleDistricts = districts.filter((district) => district.lat && district.lng);

  useEffect(() => {
    console.log("Heatmap map data:", visibleDistricts);
  }, [visibleDistricts]);

  return (
    <MapContainer
      center={center}
      zoom={8}
      style={{ width: "100%", height: "100%" }}
      className="rounded-lg"
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      {visibleDistricts.map((district) => (
        <CircleMarker
          key={district.id}
          center={[district.lat, district.lng]}
          radius={6 + district.score * 0.2}
          pathOptions={{
            color: getScoreColor(district.score),
            fillColor: getScoreColor(district.score),
            fillOpacity: 0.7,
            weight: focused?.id === district.id ? 2 : 1,
          }}
          eventHandlers={{
            click: () => onSelect(district),
          }}
        >
          <Tooltip direction="top">
            <strong>{district.district || district.name}</strong>
            <br />
            Score: {district.score}
            <br />
            Schools: {district.schools}
          </Tooltip>
          <Popup>
            <div>
              <h3 className="font-bold">{district.district || district.name}</h3>
              <p>Schools: {district.schools}</p>
              <p>Score: {district.score}</p>
              <p>Priority: {district.priority}</p>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
};
