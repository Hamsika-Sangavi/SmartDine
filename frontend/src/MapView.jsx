import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function MapView({ restaurants }) {
  const valid = restaurants.filter((r) => r.latitude && r.longitude);

  if (valid.length === 0) {
    return <p>No location data available for these results.</p>;
  }

  const center = [valid[0].latitude, valid[0].longitude];

  return (
    <MapContainer center={center} zoom={12} style={{ height: "400px", width: "100%", borderRadius: "8px" }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {valid.map((r) => (
        <Marker key={r.id} position={[r.latitude, r.longitude]}>
          <Popup>
            <strong>{r.name}</strong>
            <br />
            ⭐ {r.rate} | ₹{r.approx_cost} for two
            <br />
            {r.cuisines}
            <br />
            <a
              href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(
                `${r.name}, ${r.location}, Bengaluru`
              )}`}
              target="_blank"
              rel="noreferrer"
            >
              🧭 Get directions
            </a>
            <br />
            <a
              href={`https://www.openstreetmap.org/?mlat=${r.latitude}&mlon=${r.longitude}#map=16/${r.latitude}/${r.longitude}`}
              target="_blank"
              rel="noreferrer"
            >
              🗺️ View on OpenStreetMap
            </a>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

export default MapView;