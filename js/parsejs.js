
var results = []

var total = 0;
var current = 0;

class Result {
    constructor(url, result, output) {
        this.url = url;
        this.result = result;
        this.output = output;
    }
}        

function toggleHeaders() {
    $("#headers").toggle();
}

function getCustomHeaders() {
    var headers = $('#customHeaders').val().split("\n");
    var customHeaders = [];
    for (var i=0; i < headers.length; i++) {
        if (/\S/.test(headers[i]))
            customHeaders.push($.trim(headers[i]));
    }
    if(customHeaders) return JSON.stringify(customHeaders);
    return null;
}

function parseJS(url) {
    $.post("/parse/ajax", {
        url: url,
        headers: getCustomHeaders(),
    }, function(data) {
        var succeeded = false;
        // success if we have output
        if(data["output"]) succeeded = true;
        // push our data to results
        var index = results.push(new Result(data["url"],succeeded,data["output"]));
        // length-1 to get newest index
        addResult(index-1);
        // remove from total
        updateProgress();
    });
}

function parseURLs() {
    // Parse URLs
    var urls = $("#urls").val();
    urls = urls.split("\n");
    // Empty results div
    resetResults();
    // Reset progress bar
    resetProgress();
    // Progress bar
    total = urls.length;
    current = 0;
    $(".progress").show();
    // Parse JS
    urls.forEach(function(url) {
        parseJS(url);
    });
}

function updateProgress() {
    // remove from total
    current = current+1
    // get new progress %
    progress = (current/total)*100;
    
    // update
    $("#progress").attr("aria-valuenow",progress);
    $("#progress").css("width",progress+"%");
    $("#progress").text(Math.ceil(progress)+"%");
}

function resetProgress() {
    $("#progress").attr("aria-valuenow",0);
    $("#progress").css("width","0%");
    $("#progress").text("0%");
}

function resetResults() {
    results = []
    rebuildResults();
}

function rebuildResults() {
    $("#results").empty();
    $("#results").html('<h2>Index</h2><div id="index"><ul></ul></div><h2>Results</h2><div id="output"></div>');
}

function buildIndex() {
    $("#index ul").empty();
    $.each(results, function(i, val) {
        if(hideResults() && val["result"] == false) return;
        $("#index ul").append('<li id="index-'+i+'"><a href="#result-'+i+'"></a></li>');
        $('#index-'+i+' a').text(val["url"]);
    });
}

function appendIndex(i) {
    if(hideResults() && results[i]["result"] == false) return;
    $("#index ul").append('<li id="index-'+i+'"><a href="#result-'+i+'"></a></li>');
    $('#index-'+i+' a').text(results[i]["url"]);
}

function buildResults() {
    $("#output").empty();
    $.each(results, function(i, val) {
        if(hideResults() && val["result"] == false) return;
        if(val["result"] == false) val["output"] = "no results";
        $("#output").append('<div class="result" id="result-'+i+'"><h1></h1><div class="output">'+val["output"]+'</div></div>');
        $("#result-"+i+" h1").append("<a></a>");
        $("#result-"+i+" a").text(val["url"]).attr({'href':val["url"],'target':'_new'});
    });
}

function appendResults(i) {
    if(hideResults() && results[i]["result"] == false) return;
    if(results[i]["result"] == false) results[i]["output"] = "no results";
    $("#output").append('<div class="result" id="result-'+i+'"><h1></h1><div class="output">'+results[i]["output"]+'</div></div>');
    $("#result-"+i+" h1").append("<a></a>");
    $("#result-"+i+" a").text(results[i]["url"]).attr({'href':results[i]["url"],'target':'_new'});
}

function addResult(i) {
    appendIndex(i)
    appendResults(i)
}

function toggleResults() {
    rebuildResults();
    buildIndex();
    buildResults();
}

function hideResults() {
    if($("#hideResults").is(":checked")) return true;
    return false;
}

$(function() {
    rebuildResults();
    $('#hideResults').change(function() { 
        toggleResults();
    });
});