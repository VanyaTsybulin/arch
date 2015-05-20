/**
 * Created by mandriy on 3/22/15.
 */


 var infoManager;

 function propagateInfoManager() {
    if(typeof(Worker) !== "undefined") {
        if(typeof(infoManager) == "undefined") {
            infoManager = new Worker("js/infoManager.js");
            infoManager.addEventListener('message', function(e){
                var systemSnapshot = e.data;
                document.getElementById('nodesNumber').textContent = systemSnapshot.nodesNumber;
                document.getElementById('doneWorkPercentage').textContent = systemSnapshot.donePercentage + "%";
                document.getElementById('done').setAttribute('style', 'width:' + systemSnapshot.donePercentage +'%');
                document.getElementById('remain').setAttribute('style', 'width:' + systemSnapshot.remainPercentage +'%');
                document.getElementById('progress').setAttribute('style', 'width:' + systemSnapshot.progressPercentage +'%');
            }, false);
            infoManager.postMessage('start');
        }
    } else {
        alert("Sorry, web workers are not supported in your browser. Please, check out fro new versions.")
    }
 }

