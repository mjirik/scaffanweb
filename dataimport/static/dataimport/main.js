//

// https://stackoverflow.com/questions/34867066/javascript-mouse-click-coordinates-for-image
//document.getElementById(imageid).addEventListener('click', function (event) {
//// https://stackoverflow.com/a/288731/1497139
//bounds=this.getBoundingClientRect();
//var left=bounds.left;
//var top=bounds.top;
//var x = event.pageX - left;
//var y = event.pageY - top;
//var cw=this.clientWidth
//var ch=this.clientHeight
//var iw=this.naturalWidth
//var ih=this.naturalHeight
//var px=x/cw*iw
//var py=y/ch*ih
//alert("click on "+this.tagName+" at pixel ("+px+","+py+") mouse pos ("+x+"," + y+ ") relative to boundingClientRect at ("+left+","+top+") client image size: "+cw+" x "+ch+" natural image size: "+iw+" x "+ih );
//});



$(document).ready(function() {
//    $("img").on("click", function(event) {
//    document.getElementById(imageid).addEventListener('click', function (event) {
    $("#previewimg").on("click", function(event) {
//    document.getElementById("previewimg").on("click", function(event) {
        bounds=this.getBoundingClientRect();
        var left=bounds.left;
        var top=bounds.top;
        var x = event.pageX - left;
        var y = event.pageY - top;
        var cw=this.clientWidth
        var ch=this.clientHeight
        var iw=this.naturalWidth
        var ih=this.naturalHeight
        var px=x/cw*iw
        var py=y/ch*ih
//        alert("click on "+this.tagName+" at pixel ("+px+","+py+") mouse pos ("+x+"," + y+ ") relative to boundingClientRect at ("+left+","+top+") client image size: "+cw+" x "+ch+" natural image size: "+iw+" x "+ih );
//        alert(window.location.href)
//        alert(window.location.pathname)
//        makeAjaxPost(px, py, window.location.pathname)
        addHiddenInput(px, py)
    });
});

function addHiddenInput(px, py) {
    var inputx = document.createElement("input");
    inputx.setAttribute("type", "hidden");
    inputx.setAttribute("name", "x");
    inputx.setAttribute("value", px);
    //append to form element that you want .
    document.getElementById("lobulepoints").appendChild(inputx);

    var inputy = document.createElement("input");
    inputy.setAttribute("type", "hidden");
    inputy.setAttribute("name", "y");
    inputy.setAttribute("value", py);
    //append to form element that you want .
    document.getElementById("lobulepoints").appendChild(inputy);

}

function makeAjaxPost(px, py, href) {
$.ajax({
    // points to the url where your data will be posted
    url:href,
//    url:'/postendpoint/$',
    // post for security reason
    type: "POST",
    // data that you will like to return
    data: {px: px, py:py},
    // what to do when the call is success
    success:function(response){},
    // what to do when the call is complete ( you can right your clean from code here)
    complete:function(){},
    // what to do when there is an error
    error:function (xhr, textStatus, thrownError){}
});

}


function draw()
  {
var canvas = document.getElementById('circle');
if (canvas.getContext)
{
var ctx = canvas.getContext('2d');
var X = canvas.width / 2;
var Y = canvas.height / 2;
var R = 45;
ctx.beginPath();
ctx.arc(X, Y, R, 0, 2 * Math.PI, false);
ctx.lineWidth = 3;
ctx.strokeStyle = '#FF0000';
ctx.stroke();
}
}