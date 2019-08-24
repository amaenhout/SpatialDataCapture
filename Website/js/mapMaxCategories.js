
//only works for 1 category visualisation
function main(countryselect){


  function getColor(d) {
    return d == "art_culture"  ? '#FF8BB3' : //pink
           d == "geography"  ? '#9090FF' : //blue
           d == "science_technology"  ? '#FFD991' : //amber
           d == "nature_biology"  ? '#8BE68B' : //green
           d == "other" ? '#1A1B1C' : //grey
           d == "politics_economy_society"  ? '#FF6868' : //red
           d == "religion"  ? '#CA9BD1' : //purple
           d == "sports"  ? '#9E9E5C' : //olive
                    '#f4f3ed';;
  }

  function getOpacity(value){
    if(value == "art_culture" ||"geography" ||" science_technology"||"nature_biology"||"other"||"politics_economy_society"||"religion"||"sports"){
      return 0.8
    }
    else{
      return 0.05
    }
  };

  function getApi(border){
    var var1 = border

    url = "http://dev.spatialdatacapture.org:8824/map/"+var1
    var results = []
    $.getJSON (url ,function(data){
      for ( var i = 0;  i < data.length; i++){
          results.push(data[i]);
      }
    })
    //console.log(results)
    return results
  };

  function getValue(array,hexid){
   for (var i = 0; i < array.length; i++){
    if (array[i].hex == hexid){
       return array[i].cat
  }
  }
  }

  // function getValue2(array,hexid){
  //  for (var i = 0; i < array.length; i++){
  //   if (array[i].hex == hexid){
  //      return array[i].value
  // }
  // }
  // }


  var result = getApi(countryselect);

  function style(feature) {
    hex = feature.properties.hex;
    value = getValue(result,hex)
      return {
          fillColor: getColor(value),
          weight: 0.25,
          opacity: 0.9,
          color: 'white',
          dashArray: '2',
          fillOpacity: getOpacity(value)
      };
  }

	//recreate map id -------
	// remove mapid
	var delmapcanvas = document.getElementById("map-canvas");
	delmapcanvas.parentNode.removeChild(delmapcanvas);

	// recreate mapid
	var cremapcanvas  = document.createElement('div');
	cremapcanvas.id=  "map-canvas";

	// add mapid to mapborder div
	var addmappcanvas = document.getElementById("mapborder");
	addmappcanvas.appendChild(cremapcanvas);

	/// create map & set view -------------
	if (countryselect == "europe"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true}).setView([46.263538, 7.938652], 5);
	}
	else if (countryselect == "austria"){
			var mymap = new L.map('map-canvas',{ zoomControl: true}).setView([47.412175, 13.798356], 7);
	}
	else if (countryselect == "belgium"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true}).setView([50.458830, 4.438212], 8);
	}
	else if (countryselect == "france"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true}).setView([47, 3], 6);
	}
	else if (countryselect == "germany"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true}).setView([51, 10], 6);
	}
	else if (countryselect == "italy"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true}).setView([42, 12], 6);
	}
	else if (countryselect == "netherlands"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true}).setView([52, 5.5], 7);
	}
	else if (countryselect == "switzerland"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true}).setView([46.8, 8.3], 7);
	}

	mymap.zoomControl.setPosition('bottomleft')
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012',
    minZoom: 4, maxZoom: 12}).addTo(mymap);


  // var amber_array = ["#FFAD0D", "#FFBB39", "#FFCA65", "#FFD991"]; //Science
  // var red_array = ["#F70000", "#F82E2E", "#F95C5C", "#FB8B8B"]; //politics, economy, society
  // var green_array = ["#00C900", "#2ED22E", "#5CDC5C", "#8BE68B"]; //nature
  // var blue_array = ["#0C0CFF", "#3838FF", "#6464FF", "#9090FF"]; //geography
  // var pink_array = ["#FF0059", "#FF2E77", "#FF5C95", "#FF8BB3"]; //art_culture
  // var purple_array = ["#8B259B", "#A04CAD", "#B574BF", "#CA9BD1"]; //Religion
  // var olive_array = ["#565600", "#686800", "#83832E", "#9E9E5C"]; //sport
  // var grey_array = ["#1A1B1C", "#2A2B2E", "#505154", "#77787A"]; //others
  // var brown_array = ["#5B2910", "#784F3B", "#967666", "#B49D92"]; //plant
  // var magenta_array = ["#C14F82", "#CC6F98", "#D78FAF", "#E2AFC6"]; //person
  // var turquoise_array = ["#157571", "#198E8A", "#42A29F", "#6CB7B4"]; //animal
  // var orange_array = ["#FF5900", "#FF772E", "#FF955C", "#FFB38B"]; //time period
setTimeout(function(){
  var geojson_plot = new L.GeoJSON.AJAX("./json/"+countryselect + ".json", {style:style});
  geojson_plot.on('data:loaded', function(){
  geojson_plot.addTo(mymap);
  });
}, 80);

};

$(window).on('load',function(){
        $('#myModal').modal('show');
    });
