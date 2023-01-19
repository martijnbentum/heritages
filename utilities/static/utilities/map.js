
// leaflet map setup
var mymap = L.map('mapid').setView([52.0055328,4.67565177],5);
var attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">'
attribution += 'OpenStreetMap contributors &copy; '
attribution += '<a href="https://carto.com/attribution">CARTO</a>'
const tileUrl = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
const tiles = L.tileLayer(tileUrl,{attribution});
tiles.addTo(mymap);

