import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMap, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default Leaflet marker icons in React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconRetinaUrl: iconRetina,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

export interface LocationMapProps {
  latitude: number | null;
  longitude: number | null;
  height?: string | number;
  width?: string | number;
  zoom?: number;
  readOnly?: boolean;
}

// Component to recenter map when coordinates change
const MapUpdater = ({ lat, lng, zoom }: { lat: number; lng: number; zoom: number }) => {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lng], zoom);
  }, [lat, lng, zoom, map]);
  return null;
};

export const LocationMap: React.FC<LocationMapProps> = ({ 
  latitude, 
  longitude, 
  height = 300, 
  width = '100%',
  zoom = 15,
  readOnly = true
}) => {
  const defaultLat = -23.55052; // Default to SP, Brazil if null
  const defaultLng = -46.633308;
  
  const lat = latitude ?? defaultLat;
  const lng = longitude ?? defaultLng;
  const hasLocation = latitude !== null && longitude !== null;

  return (
    <div style={{ height, width, borderRadius: 8, overflow: 'hidden', position: 'relative', zIndex: 1 }}>
      <MapContainer 
        center={[lat, lng]} 
        zoom={zoom} 
        scrollWheelZoom={!readOnly}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {hasLocation && (
          <Marker position={[lat, lng]}>
            <Popup>
              Localização Registrada
            </Popup>
          </Marker>
        )}
        <MapUpdater lat={lat} lng={lng} zoom={zoom} />
      </MapContainer>
    </div>
  );
};
