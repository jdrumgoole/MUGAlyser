
const client = stitch.Stitch.initializeDefaultAppClient('mugalyserstats-efuqk'); // get stitch client - MUGAlyserStats stitch app
client.auth.loginWithCredential(new stitch.AnonymousCredential()).then(user => { // login anonymously
    console.log(`logged in to stitch anonymously as user ${user.id}`)
});

invalid = ["find", "None", "api", "url", "about", "pro", "jobs", "apps", "meetup_api", "topics", "cities", "privacy", "terms", "cookie_policy", "facebook_account_tie", "fbconnectxd_ssl.html", "help"];
var urlnames_exact = [];
var urlnames_all = [];

$(document).ready(function () {

  // on submit function for textbox with meetup.com search criteria
  $('#inputForm').submit(function(e) {
    $('#allresults').val('');           // clear any previous data in results text area
    $('#exactresults').val('');

    var searchfor = document.forms["inputForm"]["userInput"].value.trim().split(" ");  // remove extra leading or trailing whitespace on search text

    // request response from meetup.com, searching for all results on the given topic
    $.ajax({
      type: 'get',
      url:"https://www.meetup.com/topics/"+searchfor[0]+"/all/",
      success: function(resp) {
        var html = $(resp);
        var links = $('a', html);                                                                         // extract all links from the html
        for( var key in links ) {                                                                         
          key = String(links[key]);
          if(key.match("https://www\.meetup\.com/(.*)/")) {                                               // check if url is in the appropriate format
            if (key.split('/').length-1 === 4) {                                                          // with no extra path specification
              key = key.replace("https://www.meetup.com/", "").replace("/", "")                           // extract only the group name from the url
              if(!invalid.includes(key)) {                                                                // check the name is not one of the links present on every meetup search page
                $('#allresults').val(document.getElementById('allresults').value + '\n' + key);           // add to list of all results
                urlnames_all.push(key);
                searchfor.forEach(function(val) {                                                         
                  if (key.toLowerCase().includes(val.toLowerCase()) && !urlnames_exact.includes(key)) {   // if one of the search words is in the url name 
                    $('#exactresults').val(document.getElementById('exactresults').value + '\n' + key);   // add it to the exact matches
                    urlnames_exact.push(key);
                  }
                });
              }
            }
          }
        }
      },
      error: function (resp) { // indicates that there is no topic in meetup with the searched name
        console.error("No results for that search.");
        alert('No search results');
      }
    });
		e.preventDefault();
		return false;
	});
})

// user clicked on "Retrieve and Store Data"
function getdataButtonClick(all) {
  var urls = [];

  // check which data they requested, all or exact matches
  if (all) {
    urls = urlnames_all;
  } else {
    urls = urlnames_exact;
  }

  var dbName = prompt("Database name: ");

  // If this app becomes more stitch oriented, the ajax requests should be moved to http requests within the requestData stitch function
  /*stitch.Stitch.defaultAppClient.callFunction("requestData", [urls, dbName]).then( val => {
    if (!val) {
      console.error("Inserting data failed. Check database name.");
    }
  });*/

  var batchID = new Date().getUTCSeconds(); // get number based on current time for unique batch ID

  // call stitch function to insert beginning audit document
  stitch.Stitch.defaultAppClient.callFunction("insertData", [{timestamp: new Date().toISOString, batchID: batchID}, dbName, "audit"]).then( val => {
      if (!val) {
        console.error("Inserting data failed. Check database name.");
      }
  });

  // collect data for each meetup user group
  urls.forEach(function(urlname) {

    // request json response for the group data
    $.ajax({
      type: 'get',
      url:'https://api.meetup.com/'+urlname+'?&sign=true&photo-host=public',
      success: function(resp) {
        stitch.Stitch.defaultAppClient.callFunction("insertData", [resp, dbName, "groups"]).then( val => {
            if (!val) {
              console.error("Inserting data failed. Check database name.");
            }
        });
      },
      error: function(resp) {
        console.log("An error occured retrieving data for " + dbName + " groups. Some access to the data may have been restricted.");
      }
    });

    // request json response for the members data
    $.ajax({
      type: 'get',
      url:'https://api.meetup.com/'+urlname+'/members?&sign=true&photo-host=public',
      success: function(resp) {
        for (var doc in resp) {
          stitch.Stitch.defaultAppClient.callFunction("insertData", [doc, dbName, "members"]).then( val => {
            if (!val) {
              console.error("Inserting data failed. Check database name.");
            }
          });
        }
      },
      error: function(resp) {
        console.log("An error occured retrieving data for " + dbName + " members. Some access to the data may have been restricted.");
      }
    });

    // request json response for the events data
    $.ajax({
      type: 'get',
      url:'https://api.meetup.com/'+urlname+'/events?&sign=true&photo-host=public',
      success: function(resp) {
        for (var doc in resp) {
          if (doc.status == "past") {
            stitch.Stitch.defaultAppClient.callFunction("insertData", [doc, dbName, "past_events"]).then( val => {
              if (!val) {
                console.error("Inserting data failed. Check database name.");
              }
            });
          } else {
            stitch.Stitch.defaultAppClient.callFunction("insertData", [doc, dbName, "upcoming_events"]).then( val => {
              if (!val) {
                console.error("Inserting data failed. Check database name.");
              }
            });
          }
        }
      },
      error: function(resp) {
        console.log("An error occured retrieving data for " + dbName + " events. Some access to the data may have been restricted.");
      }
    });

    // call stitch function to insert ending audit document
    stitch.Stitch.defaultAppClient.callFunction("insertData", [{timestamp: new Date().toISOString, batchID: batchID}, dbName, "audit"]).then( val => {
        if (!val) {
          console.error("Inserting data failed. Check database name.");
        }
    });

  });
}