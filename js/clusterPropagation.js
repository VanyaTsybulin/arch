/**
 * Created by mandriy on 3/9/15.
 */

include('/js/utils.js');

var worker;
var current_task_id = false;

function include(url) {
    var script = document.createElement('script');
    script.src = url;
    document.getElementsByTagName('head')[0].appendChild(script)
}

function terminateWorker() {
    if (typeof worker !== 'undefined') {
        worker.terminate()
    }
    if (current_task_id) {
        var rollbackRequest = createRequest();
        rollbackRequest.open('GET', '/task-rollback/' + current_task_id, true);
        rollbackRequest.send()
    }
}

function propagate() {
    if(typeof(Worker) !== "undefined") {
        if(typeof(worker) == "undefined") {
            document.getElementById("body_id").setAttribute('onunload', "terminateWorker()");
            worker = new Worker("js/cluster.js");
            worker.addEventListener('message', function(e) {
                if (e.data == 'done') {
                    current_task_id = false;
                } else {
                    current_task_id = parseInt(e.data);
                }
            });
            worker.postMessage('start');
        }
    } else {
        alert("Sorry, web workers are not supported in your browser. Please, check out fro new versions.")
    }
}

