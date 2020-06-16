// https://stackoverflow.com/questions/34867066/javascript-mouse-click-coordinates-for-image
document.getElementById(imageid).addEventListener('click', function (event) {
// https://stackoverflow.com/a/288731/1497139
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
alert("click on "+this.tagName+" at pixel ("+px+","+py+") mouse pos ("+x+"," + y+ ") relative to boundingClientRect at ("+left+","+top+") client image size: "+cw+" x "+ch+" natural image size: "+iw+" x "+ih );
});



$(document).ready(function() {
    $("img").on("click", function(event) {
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
        alert("click on "+this.tagName+" at pixel ("+px+","+py+") mouse pos ("+x+"," + y+ ") relative to boundingClientRect at ("+left+","+top+") client image size: "+cw+" x "+ch+" natural image size: "+iw+" x "+ih );
    });
});