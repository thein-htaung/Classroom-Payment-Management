$(document).ready(function() {
  fee = document.getElementById("fees").innerHTML;

  document.getElementById("fees").innerHTML = "<p><h5>Ks. "+ numberWithCommas(fee) + "</h5></p>";
  document.getElementById("fees").style.display = 'block';
});


//https://stackoverflow.com/questions/27761543/
function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
