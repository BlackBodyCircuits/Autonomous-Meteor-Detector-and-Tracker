var height = 0;
var window_height;

function generate_imgs(img_urls){
    for(let i=0; i<img_urls.length; i++){
        url = img_urls[i];
        var img = new Image();
        img.src = url;
        document.getElementById('scroll-container').appendChild(img);
        console.log(document.getElementById('scroll-container'));
    }
}

function load_new_imgs(){
    var server_addr = "http://127.0.0.1:8080";
    var imgs = [server_addr + "/pearl0.jpg", server_addr + "/pearl2.jpg", server_addr + "/pearl1.jpg"];
    generate_imgs(imgs);
    height += document.documentElement.clientHeight;
    console.log("DONE");
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