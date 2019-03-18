/*
Some global variables
*/
var parcels_bins = "https://raw.githubusercontent.com/YayinC/Others/master/parcels_bins.geojson";
var parcels_agri = "https://raw.githubusercontent.com/YayinC/Others/master/parcels_agri.geojson";
var grainbins = "https://raw.githubusercontent.com/YayinC/Others/master/grainbins.geojson";

var mapcenter = [-89.904563,40.025750];
var zoomlevel = 10;
maxColors = ["#f0f9e8", "#bae4bc", "#7bccc4", "#43a2ca", "#0868ac"]
/**
Set up the map
**/
var map = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/light-v9",
    center: mapcenter,
    zoom: zoomlevel
});

map.addControl(new mapboxgl.NavigationControl());

/**
Load the layers
**/
var loadlayers = function(){
  map.on("load", function () {
    map.addSource("parcels_bins", {
          "type": "geojson",
          "data":  parcels_bins
        });

    map.addSource("parcels_agri", {
            "type": "geojson",
            "data":  parcels_agri
        });

    map.addSource("grainbins", {
            "type": "geojson",
            "data":  grainbins
        });

    map.addLayer({
          "id": "parcels_agri",
          "type": "fill",
          "source": "parcels_agri",
          "paint": {
              "fill-color": "#2b2b2b",
              "fill-opacity": 0.1
          }
      });


    map.addLayer({
          "id": "parcels_bins",
          "type": "fill",
          "source": "parcels_bins",
          "paint": {
              "fill-color": {
                property: 'bushels_54',
                stops: [
                    [60000, maxColors[0]],
                    [80000, maxColors[1]],
                    [120000, maxColors[2]],
                    [250000, maxColors[3]],
                    [1000000, maxColors[4]]]
                  },
              "fill-opacity": 0.75
          }
          });

    map.addLayer({
            "id": "grainbins",
            "type": "fill",
            "source": "grainbins",
            "paint": {
                "fill-color": "#FFC000",
                "fill-opacity": 0.75
          }
          });
      });
};

loadlayers();

function thousandSep(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

map.on("mouseenter", "parcels_bins", function (e) {
      var minCap = thousandSep(Math.round(e.features[0].properties.bushels_15));
      var maxCap = thousandSep(Math.round(e.features[0].properties.bushels_54));
      var ownername = e.features[0].properties.OWNER_copy
      document.getElementById('content').innerHTML = "Parcel Owner: <br>" + ownername +
      "<br><br> The Capacity Range: <br>" + minCap + " - " + maxCap + " bushels";
  });

map.on("mouseleave", "parcels_bins", function (e) {
    document.getElementById('content').innerHTML = "";
});


map.on('click', 'grainbins', function(e) {

    var radius = e.features[0].properties.radius.toFixed(2);
    var area = thousandSep(Math.round(e.features[0].properties.area));

    var description = "Radius: " + radius + " ft<br>Area: " + area + " sqft"

    new mapboxgl.Popup()
        .setLngLat(e.lngLat)
        .setHTML(description)
        .addTo(map);

});

map.on('mouseenter', 'grainbins', function () {
    map.getCanvas().style.cursor = 'pointer';
});

// Change it back to a pointer when it leaves.
map.on('mouseleave', 'grainbins', function () {
    map.getCanvas().style.cursor = '';
});
