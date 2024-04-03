var height = 0;
var window_height;
var loaded_imgs = 0;

function generate_imgs(img_urls){
    for(let i=0; i<img_urls.length; i++){
        url = img_urls[i];
        var img = new Image();
        img.src = url + "&raw=True";
        document.getElementById('scroll-container').appendChild(img);
        console.log(document.getElementById('scroll-container'));
    }
    loaded_imgs += img_urls.length;
}

function load_new_imgs(){
    const num_to_load = 5;
    var server_addr = "http://127.0.0.1:8080"
    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Define the URL of the JSON file you want to fetch
    var jsonUrl = server_addr + `/load_imgs&loaded_imgs=${String(loaded_imgs)}&load=${String(num_to_load)}`;

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
            console.log(res)
            var imgs = res["imgs"]
            for(let i=0;i<imgs.length;i++){
                imgs[i] = server_addr + imgs[i];
            }
            
            generate_imgs(imgs);
            height += document.documentElement.clientHeight;
            console.log("DONE");
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
    console.log("HERE")


    // var server_addr = "http://127.0.0.1:8080";
    // var imgs = [server_addr + "/pearl0.jpg", server_addr + "/pearl2.jpg", server_addr + "/pearl1.jpg"];
    
}

function fInit(){
    load_new_imgs();
}

function auto_pop(){
    var pos = window.scrollY;
    // const H = document.documentElement.clientHeight ;
    console.log(pos/height);
    if(pos / height >= 1){
        load_new_imgs()
    }
}

//window.onload=function(){
$(document).ready(function() {
    fInit();
    document.addEventListener("scroll", auto_pop);
    window_height = window.innerHeight;
});