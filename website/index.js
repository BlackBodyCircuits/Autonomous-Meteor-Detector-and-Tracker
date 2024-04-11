//create global variables  
var imgID;
var cams = {};

// https://www.w3schools.com/js/js_cookies.asp
function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

function get_img(ID){

    // server address, this should prob be a global var
    var server_addr = "http://127.0.0.1:8080"
    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Define the URL of the JSON file you want to fetch
    var jsonUrl = server_addr + "/get_img&id=" + String(ID);

    // Configure the request
    xhr.open('GET', jsonUrl, true); // true for asynchronous
    // xhr.setRequestHeader("Access-Control-Allow-Headers", "X-Requested-With, content-type");

    // Set the responseType to 'json' to automatically parse JSON response
    xhr.responseType = 'json';

    // Define a function to handle the successful response
    xhr.onload = function () {
        if (xhr.status === 200) {
            // Access the parsed JSON response
            var res = xhr.response;
            handle_res(res, server_addr)
            // remeber the image we were last looking at
            document.cookie = `imgID=${ID}`;
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

function handle_res(res, server_addr){
    // Access the parsed JSON response
    console.log(res); // Or do something with the JSON data
    var im_name = res["name"]
    var im_src = server_addr + res["img_url"]
    var log_file = server_addr + res["log_url"]
    // var log_file = JSON.stringify(res["log_url"])
    var cam = res["camera"]
    var loc = res["loc"]

    // get the time in local time
    var date = new Date(res["date"])
    const localDate = new Date(date.getTime() + date.getTimezoneOffset() * 60000);
    
    document.getElementById('caption').innerHTML  = im_name;
    document.getElementById('cam').innerHTML  = cam;
    document.getElementById('date').innerHTML  = localDate;
    document.getElementById('loc').innerHTML  = loc;
    document.getElementById('slideshow').src = im_src;
    document.getElementById('raw-link').href = im_src+"&raw=True";
    // document.getElementById('status-link').href = log_file;
    console.log(log_file)
    document.getElementById('status-link').src = log_file;
}

//function will be called on the window load event
function init_index(){
    // load the last looked at image ID
    console.log("HER")
    imgID = getCookie("imgID")

    if (!imgID){
        imgID = 0
        console.log(imgID)
    }
    console.log(imgID)
    // load the firt image in the DB on init
    get_img(imgID)
}

async function FNext(){
    // get the next image
    get_img(imgID -= 1)
}

function FPrev(){
    // get the previous image
    get_img(imgID -= 1)
}

function gallery(){
    // window.open("http://127.0.0.1:5500/website/html/gallery.html");
}

//window.onload=function(){
$(document).ready(function() {
    init_index();
    //document.getElementById('forward').onclick = FNext;
    $('#forward').click(FNext)
    //document.getElementById('backward').onclick = FPrev;
    $('#backward').click(FPrev);
    // $('#gallery-btn').click(gallery);
});
