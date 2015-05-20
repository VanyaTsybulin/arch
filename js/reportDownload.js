/**
 * Created by mandriy on 3/24/15.
 */



function genReportLink() {
    var reportRequest = createRequest();
    reportRequest.open('GET', '/report-download', false);
    reportRequest.send();

    var blob = new Blob([reportRequest.responseText], {type : 'text/xml'});
    var blobURL = window.URL.createObjectURL(blob);
    document.getElementById("reportLink").setAttribute('href', blobURL);
}