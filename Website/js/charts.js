function getApi(chartname){
	url = "http://dev.spatialdatacapture.org:8824/"+chartname;
	console.log(url)
  var results = []
    $.getJSON (url ,function(data){
    for ( var i = 0;  i < data.length; i++){
      results.push(data[i]);
        }
     })
  return results;
  }
	$(window).on('load',function(){
					$('#myModal').modal('show');
			});

$(document).ready(function(){
  // PERIOD CHART ---------------------------------------------------------
	var periodapi =getApi("periodchart");
	// CHANGE WHEN API WORKS AGAIN
	//periodapi=  [{"1600":0.31,"1700":0.33,"1800":0.4,"1850":0.48,"1900":0.65,"1920":0.76,"1940":0.9,"1960":1.13,"1980":1.23,"2000":1.72,"2020":2.55,"country":"austria"},	{"1600":0,"1700":0,"1800":0,"1850":0,"1900":1.69,"1920":1.69,"1940":1.69,"1960":1.69,"1980":1.69,"2000":1.69,"2020":1.69,"country":"belgium"},	{"1600":5.9,"1700":5.9,"1800":5.93,"1850":5.93,"1900":36.34,"1920":44.9,"1940":50.78,"1960":57.52,"1980":57.55,"2000":57.55,"2020":57.97,"country":"france"}]

	setTimeout(function(){

			var periodcty = [];
			var periodkey=["1600","1700","1800","1850","1900","1920","1940","1960","1980","2000","2020"];

			for (var i= 0;  i < periodapi.length; i++){
				// record countries as periodcty for series names
				var a=periodapi[i].country;
				var a=a.charAt(0).toUpperCase() + a.slice(1)+ " "+ getCountryFlag(a);
				periodcty.push(a);

			}

			var arr=[];
			for(var i= 0;  i < periodapi.length; i++){
				// record timeperiods for series data;
				var pd = []; var a = periodapi[i];
				for(var u= 0;  u < periodkey.length; u++){
					pd.push([Date.UTC(periodkey[u]),a[periodkey[u]]])
				}
				arr.push(pd);
			}

			var perioddata = [];
			for (var i = 0; i < periodapi.length; i++) {
				perioddata.push({
					name: periodcty[i],
					data: arr[i]
				});
			}

			Highcharts.chart('periodgraph', {
				chart: { type: 'spline',backgroundColor:'rgba(255, 255, 255, 0.0)'},
				title: { text: 'Time profile of street names',style: {	color: 'white'}},
				subtitle: { text: 'Street names referring to each time period (cumulative)',style: {	color: 'white'}},
				xAxis: {
					type: 'datetime',
					dateTimeLabelFormats: { year: '%Y'    },
					title: { text: 'Time Period',style: {	color: 'white'} },
					crosshair: {
						width: 0.7,
						color: 'grey'
					},
					labels: {
						style: {
							color: 'white'
						}
					}
				},
				yAxis: { title:
					{ text: '% of existing street names',
						style: {color: 'white'}},
					min: 0,
					gridLineColor: 'rgba(255, 255, 255, 0.0)',
					crosshair: {
						width: 0.7,
						color: 'grey'
					},
					labels: {
						style: {
							color: 'white'
						},
						formatter: function() {
							return this.value+" %";
						}
					}
				},
				legend: {
					itemStyle: {
					color: 'white'
					},
					itemHoverStyle: {
					color: 'red'
					},
					itemHiddenStyle: {
					color: 'grey'
					}
				},
				tooltip: {
						headerFormat: '<b>{series.name}</b><br>',
						pointFormat: 'Before {point.x:%Y}: {point.y:.2f} %'
					},
				plotOptions: {spline: {marker: {enabled: true}}},
				colors: ['#FF8BB3','#ffff00','#3399ff','#9E9E5C','#009933','#ff0000'],
				series: perioddata
			});
		}, 500);


	// BAR CHART --------------------------------------------

	var classapi = getApi("classchart");

	setTimeout(function(){
		// record countries as classcty for xAxis categories
		var classcty = [];
		for (var i= 0;  i < classapi.length; i++){
				var a=classapi[i].country;
				var a=a.charAt(0).toUpperCase() + a.slice(1) + " "+ getCountryFlag(a);
				classcty.push(a);
		}
		//record all keys (excluding country)
		var ck = Object.keys(classapi[0]);
		var classcat = ck.slice(1);

		var cd = [];
		for (var u= 0;  u < classcat.length; u++){
			var v=[];
			for (var i = 0; i < classapi.length; i++) {
			//record values by key
			var val=classapi[i][classcat[u]];
			v.push(val);
		}
		cd.push(v);
		}

		var classdata = [];
		for (var i = 0; i < 8; i++) {
		classdata.push({
			name: classcat[i],
			data: cd[i]
		});
		}

		Highcharts.chart('classgraph', {
			chart: {type: 'bar',backgroundColor:'rgba(255, 255, 255, 0.0)'},
			title: {    text: 'Distribution of street name categories',style: {	color: 'white'}},
			subtitle: { text: 'Comparison across 7 countries',style: {	color: 'white'}},
			xAxis: {
				categories: classcty,
				title: { text: 'Country',style: {	color: 'white'} },
				labels: {
					style: {
						color: 'white'
					}
				},

			},
			yAxis: { title:
					{ text: '% of streets names belonging to each thematic category',
					style: { color: 'white'}},
				gridLineColor: 'rgba(255, 255, 255, 0.0)',
				min: 0,
				max:100,
				labels: {
					style: {
						color: 'white'
					},
					formatter: function() {
						return this.value+" %";
					}
				}
			},

			legend: {
				itemStyle: {
				color: 'white'
				},
				itemHoverStyle: {
				color: 'red'
				},
				itemHiddenStyle: {
				color: 'grey'
				}
			},
      tooltip: {
          pointFormat: '<b>{series.name}</b>: {point.y:.2f} %'
        },
			plotOptions: { series: { stacking: 'normal' } },
			colors: ['#FF8BB3', '#8BE68B', '#9090FF', '#CA9BD1', '#FFD991','#9E9E5C','#FF6868','#77787A'],
			series: classdata
		})
	}, 200);


});


//   [{"1600":0.31,"1700":0.33,"1800":0.4,"1850":0.48,"1900":0.65,"1920":0.76,"1940":0.9,"1960":1.13,"1980":1.23,"2000":1.72,"2020":2.55,"country":"austria"},
// {"1600":0,"1700":0,"1800":0,"1850":0,"1900":1.69,"1920":1.69,"1940":1.69,"1960":1.69,"1980":1.69,"2000":1.69,"2020":1.69,"country":"belgium"},
// {"1600":5.9,"1700":5.9,"1800":5.93,"1850":5.93,"1900":36.34,"1920":44.9,"1940":50.78,"1960":57.52,"1980":57.55,"2000":57.55,"2020":57.97,"country":"france"}]
