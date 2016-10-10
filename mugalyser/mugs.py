'''
Created on 10 Oct 2016

@author: jdrumgoole
'''
from collections import OrderedDict
MUGS = {
    "DublinMUG"                                  : { "country" : "Ireland"},
    "Glasgow-MongoDB-User-Group"                 : { "country" : "United Kingdom"},
    "London-MongoDB-User-Group"                  : { "country" : "United Kingdom"},
    "Thames-Valley-MongoDB-User-Group"           : { "country" : "United Kingdom"},
    "Manchester-MongoDB-User-Group"              : { "country" : "United Kingdom"}, 
    "MongoDB-Edinburgh"                          : { "country" : "United Kingdom"},
    "Belfast-MongoDB-User-Group"                 : { "country" : "United Kingdom"},
    "Toulouse-MongoDB-User-Group"                : { "country" : "France"},
    "Bordeaux-MongoDB-User-Group"                : { "country" : "France"},
    "Nantes-MongoDB-User-Group"                  : { "country" : "France"},
    "Paris-MongoDB-User-Group"                   : { "country" : "France"},
    "Lyon-MongoDB-User-Group"                    : { "country" : "France"},
    "MongoDB-Rennes"                             : { "country" : "France"},
    "mongodb-spain"                              : { "country" : "Spain"},
    "Madrid-MongoDB-User-Group"                  : { "country" : "Spain"},
    "Malaga-MongoDB-User-Group"                  : { "country" : "Spain"},
    "Sevilla-MongoDB-User-Group"                 : { "country" : "Spain"},
    "Lisbon-MongoDB-User-Group"                  : { "country" : "Portugal"},
    "Coimbra-MongoDB-User-Group"                 : { "country" : "Portugal"},
    "MUGBerlin"                                  : { "country" : "Germany"},
    "Mannheim-MongoDB-User-Group"                : { "country" : "Germany"},
    "mugh-MongoDB-User-Group-in-Hamburg"         : { "country" : "Germany"},
    "Frankfurt-Rhine-Main-MongoDB-User-Group"    : { "country" : "Germany"},
    "Paderborn-MongoDB-User-Group"               : { "country" : "Germany"},
    "Dusseldorf-MongoDB-User-Group"              : { "country" : "Germany"},
    "Swiss-MongoDB-User-Group"                   : { "country" : "Switzerland"},
    "Geneva-MongoDB-User-Group"                  : { "country" : "Switzerland"},
    "MongoDB-Roma"                               : { "country" : "Italy"},
    "MongoDB-Milan"                              : { "country" : "Italy"},
    "Padova-MongoDB-User-Group"                  : { "country" : "Italy"},
    "MongoDB-Prague"                             : { "country" : "Czech Republic"},
    "MongoDB-Vienna"                             : { "country" : "Austria"},
    "MongoDB-Budapest"                           : { "country" : "Hungary"},
    "Wroclaw-MongoDB-User-Group"                 : { "country" : "Poland"},
    "Warsaw-MongoDB-User-Group"                  : { "country" : "Poland"},
    "Iasi-MongoDB-User-Group"                    : { "country" : "Romania"},
    "Dnipropetrovsk-MongoDB-User-Group"          : { "country" : "Ukraine"},
    "Vilnius-MongoDB-User-Group"                 : { "country" : "Lithunia"},
    "Krasnodar-MongoDB-User-Group"               : { "country" : "Russia"},
    "Moscow-MongoDB-User-Group"                  : { "country" : "Russia"},
    "Norway-MongoDB-User-Group"                  : { "country" : "Norway"},
    "Bergen-NoSQL"                               : { "country" : "Norway"},
    "Copenhagen-MongoDB-User-Group"              : { "country" : "Sweden"},
    "Finland-MongoDB-User-Group"                 : { "country" : "Finland"},

    "Tbilisi-MongoDB-User-Group"                 : { "country" : "Georgia"},
    "MongoDB-Istanbul"                           : { "country" : "Turkey"},
    "Thessaloniki-MongoDB"                       : { "country" : "Greece"},
    "mongo-il"                                   : { "country" : "Israel"},
    "Cairo-MongoDB-Meet-up"                      : { "country" : "Egypt"},
    "Casablanca-MongoDB-User-Group"              : { "country" : "Morocco"},
    
    #Canadian MUGS
    "Vancouver-MongoDB-User-Group"               : { "country" : "Canada"},       
    "Montreal-MUG"                               : { "country" : "Canada"},
    "Victoria-MongoDB-Meetup"                    : { "country" : "Canada"},
    "Toronto-MongoDB-User-Group"                 : { "country" : "Canada"},
    
    #US MUGS
    "seattlemug"                                 : { "country" : "USA"},
    "Spokane-MongoDB-User-Group"                 : { "country" : "USA"},
    "Portland-MongoDB-User-Group"                : { "country" : "USA"},
    "Keizer-MongoDB-User-Group"                  : { "country" : "USA"},
    "San-Francisco-MongoDB-User-Group"           : { "country" : "USA"},
    "Los-Angeles-MongoDB-User-Group"             : { "country" : "USA"},
    "Orange-County-MongoDB-User-Group"           : { "country" : "USA"},
    "MongoDB-San-Diego-Meetup"                   : { "country" : "USA"},
    "Phoenix-MongoDB-User-Group"                 : { "country" : "USA"},
    "boulder-denver-mongo"                       : { "country" : "USA"},  
    "Dallas-mongoDB-Meetup"                      : { "country" : "USA"},
    "Austin-MongoDB-User-Group"                  : { "country" : "USA"},
    "Houston-MongoDB-User-Group-MUG"             : { "country" : "USA"},
    "Minneapolis-Mongo-DB-User-Group"            : { "country" : "USA"},
    "Saint-Louis-MongoDB-User-Group"             : { "country" : "USA"},
    "Little-Rock-MongoDB-User-Group"             : { "country" : "USA"},
    "Chicago-MongoDB-User-Group"                 : { "country" : "USA"},
    "Huntsville-MongoDB-User-Group"              : { "country" : "USA"},
    "Atlanta-MongoDB-User-Group"                 : { "country" : "USA"},
    "Cincinnati-MongoDB-User-Group"              : { "country" : "USA"},
    "Detroit-MongoDB-User-Group"                 : { "country" : "USA"},
    "Columbus-MongoDB-Meetup-Group"              : { "country" : "USA"},
    "Charlotte-MongoDB-User-Group"               : { "country" : "USA"},
    "MongoRaleigh"                               : { "country" : "USA"},
    "Pittsburgh-MongoDB-User-Group"              : { "country" : "USA"},
    "Western-New-York-MongoDB-User-Group"        : { "country" : "USA"},
    "Richmond-MongoDB-User-Group"                : { "country" : "USA"},
    "Washington-DC-MongoDB-Users-Group"          : { "country" : "USA"},
    "Baltimore-MongoDB-Users-Group"              : { "country" : "USA"},
    "Philadelphia-MongoDB-User-Group"            : { "country" : "USA"},
    "New-York-MongoDB-User-Group"                : { "country" : "USA"},
    "Boston-MongoDB-User-Group"                  : { "country" : "USA"},
    "Orlando-MongoDB-User-Group"                 : { "country" : "USA"},
    "Miami-MongoDB-Meetup"                       : { "country" : "USA"},
    
    "Mexico-City-MongoDB-User-Group"             : { "country" : "Mexico"},
    
    "El-Salvador-MongoDB-User-Group"             : { "country" : "El-Salvador"},
    
    "Santo-Domingo-MongoDB-User-Group"           : { "country" : "Dominican Republic"},
    
    "Caracas-MongoDB-User-Group"                 : { "country" : "Venezuela"},
    
    "Cali-MongoDB-User-Group"                    : { "country" : "Columbia"},
    
    "mongodbperu"                                : { "country" : "Peru"},
    
    "SP-MongoDB"                                 : { "country" : "Brazil"},
    
    "Santiago-MongoDB-User-Group"                : { "country" : "Chile"},
    
    "Islamabad-MongoDB-User-Group"               : { "country" : "Pakistan"},
    
    "mongo-dilli"                                : { "country" : "India"},
    
    "Mumbai-MongoDB-User-Group"                  : { "country" : "India"},
    
    "Bangalore-MongoDB-User-Group"               : { "country" : "India"},
    
    "Butwal-MongoDB-User-Group"                  : { "country" : "Nepal"}, 
    
    "Nepal-MongoDB-User-Group"                   : { "country" : "Nepal"},
    

    
    "MelbourneMUG"                               : { "country" : "Australia"},
    
    "SydneyMUG"                                  : { "country" : "Australia"},
    
}

