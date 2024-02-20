//create a psedo-class
function PicFrame(displayName, imgnum){
    //create and assign property
    this.DisplayName = displayName;
    //create and assign property
    this.ViewCount = 0;
    //create and assign property to new instance of an Image object
    this.DisplayImage = new Image();
    this.DisplayImage.src = "./images/img" + imgnum + ".jpg";
}


//create global variables
var arrName = ["The Chief","Baby Yoda","The Mountain","Master of the Mystic Arts","Lets do this one Last Time"];     //array to hold names of pictures
var arrPicFrame = [];                                                       //an empty array to hold picframe objects
var currentIndex = 0;                                                       //a current displayed picture index value
var auto = false;                                                           //a flag to determine if auto is triggered
var timerID = 0;                                                            //timer

//function will be called on the window load event
function fInit(){
    //this will only load a singluar pic
    /*create new pic frame object using indexed name and index number*/
    //var newPicFrame = new PicFrame(arrName[currentIndex],currentIndex);
    /*add the new object to the global array*/
    //arrPicFrame[currentIndex] = newPicFrame;

    //this preloads all the images
    for (let i = 0; i < arrName.length; i++) {
        arrPicFrame.push(new PicFrame(arrName[i],i))
    }

    //invoke show pic function
    ShowPic();
}

function ShowPic(){

    //when called will the cb will only be executed after the fadeout is complete
    $('#slideshow').fadeOut("slow",cbShowPic);
    $('#slideshow').fadeIn();
    
}

//function will be invoked to update the src of the main image object to the
//src of the currently set global index value in image object array
function cbShowPic(){
    //update the src of the main image to hte src of the currently set 
    //global index calue
    var counter = arrPicFrame[currentIndex].ViewCount += 1;

    //document.getElementById("slideshow").src = "./images/img" + currentIndex + ".jpg" ;
    $('#slideshow').prop('src',"./images/img" + currentIndex + ".jpg");
    //document.getElementById('caption').innerHTML = arrName[currentIndex] + "(" + counter + ")";
    $('#caption').prop('innerHTML', arrName[currentIndex] + "(" + counter + ")");
}

async function FNext(){
    //increment the current index
    currentIndex++;
    //if it is outside the bounds of the array, wrap it
    //since we cant use if just check it with mod
    currentIndex = currentIndex % 5;
    //invoke showpic
    //ShowPic();

//     fetch("https://storefrontgateway.saveonfoods.com/api/stores/1982/categories/30791/groupby?productCount=1000&take=10&skip=1")
//   .then((response) => response.json())
//   .then((json) => {
//     console.log(json["items"][0]["items"]["name"])
//     //console.log(json["items"][0]["items"]["name"])
//     });


    // URL of the image you want to load
    var imageUrl = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Fireball_imaged_by_the_Perenjori_DFN_station.jpg/330px-Fireball_imaged_by_the_Perenjori_DFN_station.jpg";

    // Fetch the image
    // fetch(imageUrl)
    //     .then(response => response.blob()) // Get the response as a Blob
    //     .then(blob => {
    //         // Create a new FileReader object
    //         var reader = new FileReader();

    //         // Define a function to handle the FileReader's load event
    //         reader.onload = function() {
    //             // Set the 'src' attribute of the <img> element to the image data URL
    //             document.getElementById('slideshow').src = reader.result;
    //         }

    //         // Read the image blob as a data URL
    //         reader.readAsDataURL(blob);
    //     })
    //     .catch(error => {
    //         console.error('Error fetching the image:', error);
    //     });


      // URL of the image you want to load
      //var imageUrl = "https://example.com/image.jpg";

    imageUrl = "https://github.com/BlackBodyCircuits/Autonomous-Meteor-Detector-and-Tracker/blob/main/test_json.json"

      // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Define the URL of the JSON file you want to fetch
    var jsonUrl = "https://storefrontgateway.saveonfoods.com/api/stores/1982/categories/30791/groupby?productCount=1000&take=10&skip=1";

    // Configure the request
    xhr.open('GET', jsonUrl, true); // true for asynchronous
    xhr.setRequestHeader("Access-Control-Allow-Headers", "X-Requested-With, content-type");

    // Set the responseType to 'json' to automatically parse JSON response
    xhr.responseType = 'json';

    // Define a function to handle the successful response
    xhr.onload = function () {
        if (xhr.status === 200) {
            // Access the parsed JSON response
            var jsonResponse = xhr.response;
            console.log(jsonResponse); // Or do something with the JSON data
        } else {
            console.error('Failed to fetch JSON:', xhr.status);
        }
    };

    // Define a function to handle errors
    xhr.onerror = function () {
        console.error('Error fetching JSON');
    };

    // Send the request
    xhr.send();

    
}


function FPrev(){
    //pseudo decrement
    //if we increase by 4 and mod we should go back to image previously
    currentIndex+=4;
    //if it is outside the bounds of the array, wrap it
    //since we cant use if just check it with mod
    currentIndex = currentIndex % 5
    //invoke showpic
    ShowPic();
}

function FAuto(){
    if(auto){
        //flip the auto switch
        auto = !auto;
        clearTimeout(timerID);
        //document.getElementById('autoimage').src = "./images/play.png"  
        $('#autoimage').prop('src', "./images/play.png");
    } 
    else 
    {
        timerID = setInterval(FNext,1500);
        auto = !auto;
        //document.getElementById('autoimage').src = "./images/pause.png"   
        $('#autoimage').prop('src', "./images/pause.png");
    }
}


//window.onload=function(){
$(document).ready(function() {
    fInit();
    //document.getElementById('forward').onclick = FNext;
    $('#forward').click(FNext)
    //document.getElementById('backward').onclick = FPrev;
    $('#backward').click(FPrev);
    //document.getElementById('auto').onclick = FAuto;
    $('#auto').click(FAuto);
});