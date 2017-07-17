
var i = 0;

function parseJS(i, url) {
    $("#results").append('<div class="result" id="result-'+i+'"><h1></h1><div class="output">Loading...</div></div>');
    $("#result-"+i+" h1").append("<a></a>");
    $("#result-"+i+" a").text(url).attr({'href':url,'target':'_new'});
    $.getJSON("/parse/ajax?url="+url, function(data) {
        if(data["output"]) {
            $("#result-"+i+" .output").html(data["output"]);
        }else{
            $("#result-"+i+" .output").text("Failed load, parse, or no results.");
        }
    })
}

function parseURLs() {
    // Parse URLs
    var urls = $("#urls").val();
    urls = urls.split("\n");
    // Build index
    if($("ul#index li").size()==0) {
        $("#results").append('<h2>Index</h2><div class="index"><ul id="index"></ul></div><h2>Results</h2>')
    }
    // Parse JS
    urls.forEach(function(url) {
        // parse js file
        parseJS(i, url);
        // add to index
        $("#index").append('<li><a href="#result-'+i+'" id="index-'+i+'"></a></li>');
        $('#index-'+i).text(url);
        i++;
    });
}
