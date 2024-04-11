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

function check_errs(cam, ID){
    console.log(cam["errs"].length)
    if(!(ID in cams)){
        cams[ID] = {"status": "GOOD", "last_reset": new Date().getTime()}
        console.log(cams)
        document.cookie =`cams=${JSON.stringify(cams)}`;
    }
    // if no erors were found
    if(cam["errs"].length == 0){
        return "GOOD"
    }
    // if the camera was previously good
    console.log(cams)
    if(cams[ID]["status"] == "GOOD"){
        // only raise an error if one we detected after the cam was reset
        var err_time;
        for(let i=0;i<cam["errs"].length;i++){
            err_time = new Date(cam["time"])
            console.log(err_time.getTime())
            console.log(cams[ID]["last_reset"])
            console.log(err_time.getTime() > cams[ID]["last_reset"])
            console.log(err_time.getTime() < cams[ID]["last_reset"])
            if(err_time.getTime() > cams[ID]["last_reset"]){
                cams[ID]["status"] = cam["errs"][i]
                document.cookie = `cams=${JSON.stringify(cams)}`
                status_notification(ID, cam["errs"][i])
                return cam["errs"][i]
            }
        }
    }else{
        return cams[ID]["status"] 
    }
    return "GOOD"
}

function check_status(){
    var server_addr = "http://127.0.0.1:8080"
    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();
  
    // Define the URL of the JSON file you want to fetch
    var jsonUrl = server_addr + "/get_status&known_errs=" + "";
  
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
            var updated_cams = document.createDocumentFragment();
            var old_cam;
            // {'cams': {1: {'errs': [], 'time': [], 'connection': 'DISCONNECTED'}, 30: {'err': ['OBSTRUCTION DETECTED'], 'time': ['2024-02-29T12:45:00Z'], 'connection': 'DISCONNECTED'}}}
            Object.entries(res["cams"]).forEach(([ID, cam]) => {
                // get the data from the log

                err = check_errs(cam, ID);
                // console.log(err)
                // status_msg = log[0];
                connection = cam["connection"];
                console.log(`${ID}: ${err}, ${connection}`);
                old_cam = document.getElementById(ID)
                // remove old camera div if it exists
                if (old_cam){
                    document.getElementById('sidenav').removeChild(old_cam);
                }
                // create a new cam div with the correct info
                updated_cams.appendChild(create_cam_node(ID, err, connection));
            });
            // update the sidebar
            document.getElementById('sidenav').appendChild(updated_cams);
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
  
function create_colored_text(msg, val, expected){
    var uncolored = document.createElement("p");
    var colored = document.createElement("span");

    colored.innerHTML = `${val}`;
    var col = val == expected ? "#008000" : "#FF0000" 
    colored.setAttribute("style", `color: ${col}`)

    uncolored.innerHTML = `${msg}`;
    uncolored.appendChild(colored);

    return uncolored
}

function create_notification(body){
    let title = "AMDAT Camera Issue";
    let icon = 'https://qph.cf2.quoracdn.net/main-qimg-87285efb98cb80b570ba20d62131200a';
    return new Notification(title, {body, icon});
  }
  
  // https://developer.mozilla.org/en-US/docs/Web/API/notification
function status_notification(ID, err) {
    if (!("Notification" in window)) {
      // Check if the browser supports notifications
      alert("Sorry this browser does not support desktop notification");
    } else if (Notification.permission === "granted") {
      // Check whether notification permissions have already been granted;
      // if so, create a notification
      const notification = create_notification(`Camera ${ID} has thrown the error: ${err}`)
      notification.onclick = () => {
          notification.close();
          window.parent.focus();
    }
    } else if (Notification.permission !== "denied") {
      // We need to ask the user for permission
      Notification.requestPermission().then((permission) => {
        // If the user accepts, let's create a notification
        if (permission === "granted") {
          const notification = new Notification("Hi there!");
          notification.onclick = () => {
                notification.close();
                window.parent.focus();
          }
  
        }
      });
    }
    else {
      alert("To Recive Status Notifications Turn On Notifications For AMDAT")
    }
  
  
    // At last, if the user has denied notifications, and you
    // want to be respectful there is no need to bother them anymore.
  }

function create_cam_node(ID, status_msg, connection_msg){
    var camera_node = document.createElement('div');
    camera_node.setAttribute("class", "camera-div");
    camera_node.setAttribute("id", ID);

    const title = document.createElement("h3");
    title.innerHTML = `Camera: ${ID}`;

    var status = create_colored_text("Status: ", status_msg, "GOOD");

    var reset_btn = document.createElement("button");
    reset_btn.setAttribute("class", "reset-status-btn");
    reset_btn.setAttribute("id", ID);
    reset_btn.innerHTML = "Reset Status";
    reset_btn.onclick = reset_status

    var connection = create_colored_text("Connection: ", connection_msg, "CONNECTED");

    
    camera_node.appendChild(title);
    camera_node.appendChild(status);
    camera_node.appendChild(connection);
    camera_node.appendChild(reset_btn);

    return camera_node
}

function reset_status(){
    const cam_ID = $(this).attr('id');
    console.log(cam_ID);
    cams[cam_ID]["status"] = "GOOD";
    cams[cam_ID]["last_reset"] = new Date().getTime();
    document.cookie = `cams=${JSON.stringify(cams)}`
    check_status()
}

//function will be called on the window load event
function fInit(){
    // load the last looked at image ID
    imgID = getCookie("imgID")
    cam_cookie = getCookie("cams")
    console.log(cam_cookie)
    if(cam_cookie){
        cams = JSON.parse(cam_cookie)
    }else{
        cams = {}
    }
    
    console.log(cams)
    if (!imgID){
        imgID = 0
        console.log(imgID)
    }
    console.log(imgID)
    // load the firt image in the DB on init
    get_img(imgID)


    var divs = [[1, "GOOD", "CONNECTED"], [2, "BAD", "CONNECTED"]];

    var docFrag = document.createDocumentFragment();
    for(var i = 0; i < divs.length; i++) {
        docFrag.appendChild(create_cam_node.apply(null, divs[i])); // Note that this does NOT go to the DOM
    }
    document.getElementById('sidenav').appendChild(docFrag);

    const interval = setInterval(check_status, 1000 * 60* 5);
    check_status()
    // status_notification("TEST", "TEST");

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
    fInit();
    //document.getElementById('forward').onclick = FNext;
    $('#forward').click(FNext)
    //document.getElementById('backward').onclick = FPrev;
    $('#backward').click(FPrev);
    // $('#gallery-btn').click(gallery);
});
