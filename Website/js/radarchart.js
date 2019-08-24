function RadarChart(city){
	$(document).ready(function(){
		function getCountry(city){
			if (["vienna"].includes(city)){
				country = "austria"
			}
			else if (["brussels","bruges"].includes(city)){
				country = "belgium"
			}
			else if (["paris"].includes(city)){
				country = "france"
			}
			else if (["milan","rome"].includes(city)){
				country = "italy"
			}
			else if (["bern","geneva"].includes(city)){
				country = "switzerland"
			}
			return country
		}
		function getCityApi(chartname,city){
			url = "http://dev.spatialdatacapture.org:8824/"+chartname+"/"+city;
			console.log(url)
			var results = []
			$.getJSON (url ,function(data){
				for ( var i = 0;  i < data.length; i++){
					results.push(data[i]);
				}
			})
			console.log(results)
			return results;
		}

		function getCountryApi(chartname,country){
			url = "http://dev.spatialdatacapture.org:8824/"+chartname+"/"+country;
			console.log(url)
			var results = []
			$.getJSON (url ,function(data){
				for ( var i = 0;  i < data.length; i++){
					results.push(data[i]);
				}
			})
			console.log(results)
			return results;
		}

		function capcat(string){
			var b = string.replace(/_/g, " & ");
			return b.replace(/\w\S*/g, function(txt){
							return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
					});
		}


		var country = getCountry(city);

		var citydata = getCityApi("radarchartcity",city);
		var countrydata = getCountryApi("radarchartcountry",country);
		var title =  "Comparison between <br/>" + capcat(city) + " and " + capcat(country) + " "+getCountryFlag(country)
		setTimeout(function(){
			var categories = ['Art & Culture', 'Geography', 'Nature & Biology', 'Politics, Economy & Society', 'Religion', 'Science & Technology', 'Other']
			var citylist = [];
			var countrylist = [];
			for (i = 0; i < categories.length; i++) {
				citylist.push(citydata[0][categories[i]])
				countrylist.push(countrydata[0][categories[i]])
			}
			console.log(citylist)
			console.log(countrylist)

			Highcharts.chart('radarchart', {
					chart: {    polar: true,   type: 'area', backgroundColor:'white'},
					title: {    text: title, x: -20, style: {color: 'black', fontSize:'14px'}},
					pane: {    size: '80%'},
					xAxis: {
						categories: categories,
						tickmarkPlacement: 'on',
						lineWidth: 0,
						labels: {
							style: {color: 'black', fontSize:'10px'}
						},
					},
					yAxis: {
						gridLineInterpolation: 'polygon',
						lineWidth: 0,
						min: 0,
						labels: {
							style: {color: 'black', fontSize:'10px'}
						}
					},
					tooltip: {
						shared: true, pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:,.0f}%</b><br/>'		  },
					legend: {
						align: 'right',
						verticalAlign: 'middle',
						itemStyle: {	color: 'black',fontSize: '10px'},
							itemHoverStyle: {color: 'red '},
							itemHiddenStyle: {color: 'grey'	}
						},
					series: [
						{color: '#4789FF', type: 'area',name: capcat(country), data: countrylist, pointPlacement: 'on' },
						{color: '#FF5733', type: 'line',name: capcat(city),data: citylist, pointPlacement: 'on'	}
					],
					responsive:
					{ rules: [{
						condition: { maxWidth: 500},
						chartOptions: {
							legend: {
								align: 'center',
								verticalAlign: 'bottom'},
							pane: {size: '80%'}
						}
					}]}
				});
			}, 500);
	});
}
