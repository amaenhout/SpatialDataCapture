function topstreets(country,category,hex = 0){

    function getApiBorder(border,category){
        var country = border
        var category = category
  
        url = "http://dev.spatialdatacapture.org:8824/topborder/"+country+"/"+category
          console.log(url)
          var results = []
        $.getJSON (url ,function(data){
          for ( var i = 0;  i < data.length; i++){
            
            results.push(data[i].name);
            }
        })
        
        return results
    };
    
    function getApiHex(hex,country,category){
        var hex = hex
        var country = country
        var category = category
    
        url = "http://dev.spatialdatacapture.org:8824/tophex/"+hex+"/"+country+"/"+category
        console.log(url)
        var results = []
        $.getJSON (url ,function(data){
            //console.log(data)
            for ( var i = 0;  i < data.length; i++){
                results.push(data[i].name);
                }
                })
        
        return results

        };
    
    function Capitalize(string) 
    {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    if (hex == 0){
        var top  =  getApiBorder(country,category)
    }
    else{
        var top  = getApiHex(hex,country,category)    
    }
    console.log(top)
    setTimeout(function(){
        $("#name_one").text(Capitalize(top[0]))
        $("#name_two").text(Capitalize(top[1]))
        $("#name_three").text(Capitalize(top[2]))
        $("#name_four").text(Capitalize(top[3]))
        $("#name_five").text(Capitalize(top[4]))
        
    },1000);


}
