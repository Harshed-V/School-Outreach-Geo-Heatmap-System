import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, useMap, GeoJSON } from "react-leaflet";
import L from "leaflet";
import geoData from "../data/tamilnadu_districts.json";

// ─── VERIFIED against actual GeoJSON dtname values ───────────────────────────
// GeoJSON uses:   Kanniyakumari / The Nilgiris / Tuticorin / Thiruvallur /
//                 Thiruvarur    / Tirupathur
// Backend uses:   kanyakumari  / nilgiris     / thoothukudi / tiruvallur /
//                 tiruvarur    / tirupattur
// All keys are lowercase-normalized GeoJSON names → canonical backend names
const DISTRICT_ALIAS = {
  // ── GeoJSON mismatches (confirmed from dtname field) ──
  "kanniyakumari":    "kanyakumari",
  "kanyakumari":      "kanyakumari",
  "the nilgiris":     "nilgiris",
  "nilgiris":         "nilgiris",
  "tuticorin":        "thoothukudi",
  "thoothukudi":      "thoothukudi",
  "thiruvallur":      "tiruvallur",
  "tiruvallur":       "tiruvallur",
  "thiruvarur":       "tiruvarur",
  "tiruvarur":        "tiruvarur",
  "tirupathur":       "tirupattur",   // GeoJSON spells it Tirupathur
  "tirupattur":       "tirupattur",
  // ── Straight matches (same name, just normalised) ──
  "ariyalur":         "ariyalur",
  "chengalpattu":     "chengalpattu",
  "chennai":          "chennai",
  "coimbatore":       "coimbatore",
  "cuddalore":        "cuddalore",
  "dharmapuri":       "dharmapuri",
  "dindigul":         "dindigul",
  "erode":            "erode",
  "kallakurichi":     "kallakurichi",
  "kanchipuram":      "kanchipuram",
  "kancheepuram":     "kanchipuram",
  "karur":            "karur",
  "krishnagiri":      "krishnagiri",
  "madurai":          "madurai",
  "mayiladuthurai":   "mayiladuthurai",
  "nagapattinam":     "nagapattinam",
  "namakkal":         "namakkal",
  "perambalur":       "perambalur",
  "pudukkottai":      "pudukkottai",
  "ramanathapuram":   "ramanathapuram",
  "ranipet":          "ranipet",
  "salem":            "salem",
  "sivaganga":        "sivaganga",
  "tenkasi":          "tenkasi",
  "thanjavur":        "thanjavur",
  "theni":            "theni",
  "tiruchirappalli":  "tiruchirappalli",
  "trichy":           "tiruchirappalli",
  "tirunelveli":      "tirunelveli",
  "tiruppur":         "tiruppur",
  "tiruvannamalai":   "tiruvannamalai",
  "vellore":          "vellore",
  "villupuram":       "villupuram",
  "virudhunagar":     "virudhunagar",
};

function normalize(name) {
  if (!name) return "";
  // lowercase + trim + drop leading "the "
  return name.toLowerCase().replace(/^the\s+/, "").trim();
}

// Canonical lookup: alias dict first, fallback to normalized string
function getCanonicalDistrict(name) {
  const n = normalize(name);
  return DISTRICT_ALIAS[n] ?? n;
}

function getColor(score) {
  if (score > 80) return "#d73027";
  if (score > 60) return "#fc8d59";
  if (score > 40) return "#fee08b";
  if (score > 20) return "#d9ef8b";
  return "#91cf60";
}



export const DistrictMap = ({ districts = [], focused, onSelectDistrict }) => {
  const center = [11.0, 78.0];
  const zoom = 7;

  // Create score lookup using the hybrid system
  const scoreMap = useMemo(() => {
    const map = {};
    if (Array.isArray(districts)) {
      districts.forEach(d => {
        if (d && d.district) {
          map[getCanonicalDistrict(d.district)] = d.score;
        }
      });
    }
    return map;
  }, [districts]);

  const style = (feature) => {
    // Check multiple potential keys for district name based on common GeoJSONs
    const rawName = feature.properties.district || 
                    feature.properties.DISTRICT || 
                    feature.properties.NAME_2 || 
                    feature.properties.dtname;

    const geoName = getCanonicalDistrict(rawName);
    const score = scoreMap[geoName];

    // handle missing data
    if (score === undefined) {
      return {
        fillColor: "#cccccc",
        weight: 1,
        color: "white",
        fillOpacity: 0.5
      };
    }

    return {
      fillColor: getColor(score),
      weight: 1, // Single boundary line weight for full district
      color: "white",
      fillOpacity: 0.7
    };
  };

  const onEachFeature = (feature, layer) => {
    const rawName = feature.properties.district || 
                    feature.properties.DISTRICT || 
                    feature.properties.NAME_2 || 
                    feature.properties.dtname || "Unknown";
                 
    const geoName = getCanonicalDistrict(rawName);
    const score = scoreMap[geoName];

    console.log("District:", geoName, "Score:", scoreMap[geoName]);

    layer.bindTooltip(`
      <strong>${geoName}</strong><br/>
      Score: ${score !== undefined ? score.toFixed(1) : "No data"}
    `);

    layer.on({
      mouseover: (e) => {
        e.target.setStyle({
          weight: 2,
          color: "#000",
          fillOpacity: 0.9
        });
      },
      mouseout: (e) => {
        e.target.setStyle({
          weight: 1,
          color: "white",
          fillOpacity: 0.7
        });
      },
      click: () => {
        const districtData = Array.isArray(districts) 
          ? districts.find(d => getCanonicalDistrict(d.district) === geoName)
          : null;
        if (districtData && onSelectDistrict) {
          onSelectDistrict(districtData);
        }
      }
    });
  };

  // key=districts.length forces GeoJSON to fully remount once API data arrives,
  // so Leaflet re-applies styles with the populated scoreMap.
  const geoKey = `geo-${districts.length}-${Object.keys(scoreMap).length}`;

  return (
    <MapContainer center={center} zoom={zoom} className="map" style={{ height: "100%", width: "100%", minHeight: "400px" }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON key={geoKey} data={geoData} style={style} onEachFeature={onEachFeature} />
      
    </MapContainer>
  );
};
