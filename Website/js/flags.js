function getCountryFlag(country) {
	if (["vienna"].includes(country)){
		country = "austria"
	}
	else if (["brussels","bruges"].includes(country)){
		country = "belgium"
	}
	else if (["paris"].includes(country)){
		country = "france"
	}
	else if (["milan","rome"].includes(country)){
		country = "italy"
	}
	else if (["bern","geneva"].includes(country)){
		country = "switzerland"
	}
	
	if (country == "austria"){
		var cc = "at"
	} else if (country == "belgium"){
		var cc = "be"
	}else if (country == "france"){
		var cc = "fr"
	} else if (country == "germany"){
		var cc = "de"
	}else if (country == "netherlands"){
		var cc = "nl"
	}else if (country == "italy"){
		var cc = "it"
	}else if (country == "switzerland"){
        var cc = "ch"
    }else if (country == "europe"){
		return "🇪🇺"
	} else {
		var cc = ""
	}

	// Mild sanity check.
	if (cc.length !== 2)
	  return "";
  
	// Convert char to Regional Indicator Symbol Letter
	function risl(chr) {
	  return String.fromCodePoint(0x1F1E6 - 65 + chr.toUpperCase().charCodeAt(0));
	}
  
	// Create RISL sequence from country code.
	return risl(cc[0]) + risl(cc[1]);
  }
  