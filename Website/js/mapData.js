function mapcount(countryselect, category){
	function getColor(d) {
    //this will never be visualised so the values are unimportant
		return d > 500  ? '#BD0026' :
			d > 100  ? '#FC4E2A' :
			d > 20   ? '#FEB24C' :
			d > 10   ? '#FED976' :
						'#FFEDA0';;
	}
	// function getOpacity(value){
	// 	return value < 0.01 ? 0.3 : 0.82;;
	// };

 	function getColor2(d, array, colour_array) {
    //this is based on quant_array
		return 	d > array[1] ? colour_array[0] :
				d > array[2] ? colour_array[1] :
				d > array[3] ? colour_array[2] :
								colour_array[3] ;;
  	}

	function getApi(border,category){
  	var var1 = border
  	var var2 = category

  	url = "http://dev.spatialdatacapture.org:8824/data/"+var1+"/"+var2
		// console.log(url)
		var results = []
  	$.getJSON (url ,function(data){
		for ( var i = 0;  i < data.length; i++){
			results.push(data[i]);
    		}
			})
	// console.log(results)
	return results


  };
	var allvalues = []; //used to hold all values obtained from api for quantile calculation
	var allvalues2 = [];
	function getValue(array,hexid){
 		for (var i = 0; i < array.length; i++){
  		if (array[i].hex == hexid){
   			allvalues.push(array[i].value)
				value = array[i].value / array[i].sum
				//console.log(value)
				allvalues2.push(value);
     			return array[i].value
    		}
		}
	}

	function getValue2(array,hexid){
	for (var i = 0; i < array.length; i++){
  		if (array[i].hex == hexid){
				return array[i].value
			}
		}
	}

	function getSum(array,hexid){
	for (var i = 0; i < array.length; i++){
			if (array[i].hex == hexid){
				return array[i].sum
			}
		}
	}


	function calculateStatistics(data) {
		let stats = {};
		let sum_of_squares = 0;
		let lower_quartile_index_1;
		let lower_quartile_index_2;

		// data needs to be sorted for median etc
		data = data.sort(function(a, b){return a - b});

		// count is just the size of the data set
		stats.count = data.length;
		stats.maximum = data[stats.count - 1];
		stats.minimum = data[0];

		// initialize total to 0, and then iterate data
		// calculating total and sum of squares
		stats.total = 0;
		for(let i = 0; i < stats.count; i++){
			stats.total += data[i];
			sum_of_squares += Math.pow(data[i], 2);
		}

		// method of calculating median and quartiles is different for odd and even count
		if(is_even(stats.count)){
			stats.median = (data[((stats.count) / 2) - 1] + data[stats.count / 2]) / 2;
			// even / even
			if(is_even(stats.count / 2)){
				lower_quartile_index_1 = (stats.count / 2) / 2;
				lower_quartile_index_2 = lower_quartile_index_1 - 1;

				stats.lower_quartile = (data[lower_quartile_index_1] + data[lower_quartile_index_2]) / 2;
				stats.upper_quartile = (data[stats.count - 1 - lower_quartile_index_1] + data[stats.count - 1 - lower_quartile_index_2]) / 2;
			}
			// even / odd
			else{
				lower_quartile_index_1 = ((stats.count / 2) - 1) / 2;

				stats.lower_quartile = data[lower_quartile_index_1];
				stats.upper_quartile = data[stats.count - 1 - lower_quartile_index_1];
			}
		}
		else{
			stats.median = data[((stats.count + 1) / 2) - 1];
			// odd / even
			if(is_even((stats.count - 1) / 2)){
				lower_quartile_index_1 = ((stats.count - 1) / 2) / 2;
				lower_quartile_index_2 = lower_quartile_index_1 - 1;

				stats.lower_quartile = (data[lower_quartile_index_1] + data[lower_quartile_index_2]) / 2;
				stats.upper_quartile = (data[stats.count - 1 - lower_quartile_index_1] + data[stats.count - 1 - lower_quartile_index_2]) / 2;
			}
			// odd / odd
			else{
				lower_quartile_index_1 = (((stats.count - 1) / 2) - 1) / 2;

				stats.lower_quartile = data[lower_quartile_index_1];
				stats.upper_quartile = data[stats.count - 1 - lower_quartile_index_1];
			}
		}
		return stats;
	}

	function is_even(n){
		return n % 2 == 0;
	}

	var result = getApi(countryselect, category)

  //called but not plotted
	function style(feature) {
    	hex = feature.properties.hex;
		value = getValue(result,hex);
    	return {
          	fillColor: getColor(value),
          	weight: 2,
          	opacity: 1,
          	color: 'white',
          	dashArray: '3',
          	fillOpacity: 0.75
      	};
	  }

	if (category == "before1600" ||  category ==  "p1700-p1800"|| category == "p1900-p1920"|| category == "p1800-p1850"|| category == "p1940-p1960"|| category == "p1980-p2000"|| category == "p1600-p1700"|| category == "p1850-p1900"|| category == "p1920-p1940"|| category == "p1960-p1980"|| category == "p2000-p2020"){
		var category = "period";
	} else if (category == "other_sub"){
		var category = "other";
	}
	else {
		var category = category;
	}
  	var temp_array = [];

	function style2(feature) {
  	hex = feature.properties.hex;
  	value = getValue2(result,hex);
		sum = getSum(result,hex);
		sum > 0 ? proportion = value/sum : proportion = 0 ;
		array = quant_array;

  	return {
		fillColor: getColor2(value, array, colour_array),
		weight: 0.25,
		opacity: 1,
		color: 'white',
		dashArray: '2',
		fillOpacity: 0.75 //0 value hexes are more transparent
  	};
	}

	function style3(feature) {
		hex = feature.properties.hex;
		count = getValue2(result,hex);
		sum = getSum(result,hex);
		if (sum = 0){
			value = 0
		} else {
			value = count/sum
		}
		value = count/sum;
		proportion = value;
		array = quant_array;

		return {
		fillColor: getColor2(value, array, colour_array),
		weight: 0.1,
		opacity: 1,
		color: 'white',
		dashArray: '3',
		fillOpacity: 0.75 //0 value hexes are more transparent
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

  var basemap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012',
		minZoom: 4, maxZoom: 14});


	if (countryselect == "europe"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([46.263538, 7.938652], 5);
	}
	else if (countryselect == "austria"){
			var mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([47.412175, 13.798356], 7);
	}
	else if (countryselect == "belgium"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([50.6, 4.438212], 8);
	}
	else if (countryselect == "france"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap ]}).setView([46.5, 3], 6);
	}
	else if (countryselect == "germany"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([51, 10], 6);
	}
	else if (countryselect == "italy"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([42, 12], 6);
	}
	// else if (countryselect == "netherlands"){
	// 	var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([52, 5.5], 7);
	// }
	else if (countryselect == "switzerland"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([46.8, 8.3], 8);
	}
	else if (countryselect == "brussels"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([50.837, 4.352412], 12);
	}
	else if (countryselect == "bruges"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([51.22, 3.224382], 11);
	}
	else if (countryselect == "geneva"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([46.205945, 6.141384], 13);
	}
	else if (countryselect == "paris"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([48.856876, 2.341254], 12);
	}
	else if (countryselect == "vienna"){
		var	mymap = new L.map('map-canvas',{ zoomControl: true, layers: [basemap]}).setView([48.209390, 16.370096], 11);
	}
	//
	// var mymap = L.map('map', {
	//     center: [39.73, -104.99],
	//     zoom: 10,
	//     layers: [basemap1, basemap2]
	// });
	mymap.zoomControl.setPosition('bottomleft')



	var quant_array = [];
	var amber_array = ["#FFAD0D", "#FFBB39", "#FFCA65", "#FFD991"]; //Science
	var red_array = ["#F70000", "#F82E2E", "#F95C5C", "#FB8B8B"]; //politics, economy, society
	var green_array = ["#00C900", "#2ED22E", "#5CDC5C", "#8BE68B"]; //nature
	var blue_array = ["#0C0CFF", "#3838FF", "#6464FF", "#9090FF"]; //geography
	var pink_array = ["#FF0059", "#FF2E77", "#FF5C95", "#FF8BB3"]; //art_culture
	var purple_array = ["#8B259B", "#A04CAD", "#B574BF", "#CA9BD1"]; //Religion
	var olive_array = ["#565600", "#686800", "#83832E", "#9E9E5C"]; //sport
	var grey_array = ["#1A1B1C", "#2A2B2E", "#505154", "#77787A"]; //others
	var brown_array = ["#5B2910", "#784F3B", "#967666", "#B49D92"]; //plant
	var magenta_array = ["#C14F82", "#CC6F98", "#D78FAF", "#E2AFC6"]; //person
	var turquoise_array = ["#157571", "#198E8A", "#42A29F", "#6CB7B4"]; //animal
	var orange_array = ["#FF5900", "#FF772E", "#FF955C", "#FFB38B"]; //time period

	if (category == "science_technology"){
			var colour_array = amber_array;
} else if (category == "politics_economy_society"){
	var colour_array = red_array;
	}else if (category == "nature_biology"){
	var colour_array = green_array;
	}else if (category == "geography"){
	var colour_array = blue_array;
	}else if (category == "art_culture"){
	var colour_array = pink_array;
	}else if (category == "religion"){
	var colour_array = purple_array;
	}else if (category == "sports"){
	var colour_array = olive_array;
	}else if (category == "other"){
	var colour_array = grey_array;
	}else if (category == "plant"){
	var colour_array = brown_array;
	}else if (category == "person"){
	var colour_array = magenta_array;
	}else if (category == "animal"){
	var colour_array = turquoise_array;
	}else if (category == "period"){
	var colour_array = orange_array;
}

function capcat(string){
	var b = string.replace(/_/g, " & ");
	return b.replace(/\w\S*/g, function(txt){
	        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
	    });
}

	function forEachFeature(feature, layer) {
			if (value == undefined){
				if (sum > 0){
					var popupContent = "<p><b>Category: " + capcat(category) + "</br>No.of Streets: " + "0" + "<br>Total Streets: " + sum + "<br>Proportion: NA</b>";
				}
				else {
					var popupContent = "<p><b>Category: " + capcat(category) + "</br>No.of Streets: " + "0" + "<br>Total Streets: 0" + "<br>Proportion: NA</b>";
				}
			}
			else {
				var popupContent = "<p><b>Category: " + capcat(category) + "</br>No. of Streets: " + value + "<br>Total Streets: " + sum + "<br>Proportion: " + (proportion*100).toFixed(2) + '%</b>';
			};
      layer.bindPopup(popupContent);
			layer.on("click", function (e) {
      });
    }

	function forEachFeature2(feature, layer) {
			if (value == undefined){
				if (sum> 0){
					var popupContent = "<p><b>Category: </b>" + capcat(category) + "</br><b>No.of Streets: </b>" + "0" + "<br><b>Total Streets: </b>" + sum + "<br><b>Proportion:</b> NA";
				}
				else {
					var popupContent = "<p><b>Category: </b>" + capcat(category) + "</br><b>No.of Streets: </b>" + "0" + "<br><b>Total Streets:</b> 0" + "<br><b>Proportion:</b> NA ";
				}
			}
			else {
				var popupContent = "<p><b>Category: </b>" + capcat(category) + "</br><b>No. of Streets: </b>" + count + "<br><b>Total Streets: </b>" + sum + "<br><b>Proportion: </b>" + proportion.toFixed(2) + '%';
			};
			layer.bindPopup(popupContent);

			layer.on("click", function (e) {
			});
		}
  //there are 2 geojson plots - the first is not added to map, it is used to call the style function
  //which ultimately calls the API, to populate the allvalues array - which is then used to
  //calculate the quartiles.

	setTimeout(function(){
		var geojson_plot = new L.GeoJSON.AJAX("./json/" +countryselect + ".json", {style:style});
		geojson_plot.on('data:loaded', function(){
		for (var i =0; i < allvalues.length; i++) {
					allvalues[i] = allvalues[i] || 0
			};

		var statslist = calculateStatistics(allvalues);

		// var statslist2 = calculateStatistics(allvalues2);
		quant_array.push(statslist.maximum, statslist.upper_quartile, statslist.median, statslist.lower_quartile);
		//quant_array.push(statslist2.maximum.toFixed(2), statslist2.upper_quartile.toFixed(2), statslist2.median.toFixed(2), statslist2.lower_quartile.toFixed(2));
		// console.log(statslist);
		// console.log(quant_array);


		var geojson_plot2 = new L.GeoJSON.AJAX("./json/" +countryselect + ".json", {onEachFeature: forEachFeature, style:style2});
		var geojson_plot_prop = new L.GeoJSON.AJAX("./json/" +countryselect + ".json", {onEachFeature: forEachFeature2, style:style3});

		var countlayer = L.layerGroup([geojson_plot2]);
		var proplayer = L.layerGroup([geojson_plot_prop]);

		var overlayMaps = {
				"Count": countlayer,
				"Proportion": proplayer
		};

		// L.control.layers(baseMaps).addTo(mymap);
		// L.control.layers(overlayMaps).addTo(mymap);

		 geojson_plot2.addTo(mymap);

		 // if (quant_array,length < 1 || quant_array == undefined){
		 // 	 	var loader = L.control.loader().addTo('mymap');
		 //  		setTimeout(function (){loader.hide();},5000);
		 // }

		 var legend = L.control({position: 'bottomright'});

		 legend.onAdd = function (mymap) {
					var div = L.DomUtil.create('div', 'info legend'),
					labels = [],
					grades = quant_array;

					for (var i = 0; i < grades.length; i++) {
						if(i == 3){
							if(grades[i] != 0)
								div.innerHTML +=
									'<i style="background:' + colour_array[i] + '"></i> ' + '< ' + grades[i] + ' ' + '<br>';
							else
								div.innerHTML +=
									'<i style="background:' + colour_array[i] + '"></i> ' + grades[i] + ' ' + '<br>';
							}
							else{
								div.innerHTML +=
									 '<i style="background:' + colour_array[i] + '"></i> '+
									 Math.round(grades [i+1]) + ' - ' + Math.round(grades[i]) + '<br>';
								 }
						}
			return div;
		 };

		 legend.addTo(mymap);
		});
	}, 80);

		function getStreets(border){
    	var var1 = border

    	url = "http://dev.spatialdatacapture.org:8824/streets/"+var1
		// console.log(url)
		var results = []
    	$.getJSON (url ,function(data){
			for ( var i = 0;  i < data.length; i++){
				results.push(data[i]);
      		}
				})
		// console.log(results)
		return results
			}
}

$(window).on('load',function(){
				$('#myModal').modal('show');
		});
