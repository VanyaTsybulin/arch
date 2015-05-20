/**
 * Created by mandriy on 3/3/15.
 */

importScripts('utils.js');

function sendResultAsJSON(task_id, result) {
    var request = createRequest();
    request.open('POST', '/save-result', true);
    var json_obj = { "task_id" : task_id,
                     "result" : result };
    request.send(JSON.stringify(json_obj))
}

function rollbackTask(task_id) {
    var rollbackRequest = createRequest();
    rollbackRequest.open('GET', '/task-rollback/' + task_id, true);
    rollbackRequest.send()
}

function acceptReceiving(task_id) {
    var acceptRequest = createRequest();
    acceptRequest.open('GET', '/accept-receiving/' + task_id, false);
    acceptRequest.send()
}

var current_task_id = false;

function workCycle() {
    var request = createRequest();
    var result = null;
    var processedSuccessfully = false;
    var whetherShouldStop = false;
    request.onreadystatechange = function () {
        try {
            if (request.readyState == 4 && request.status == 200) {
                var task = JSON.parse(request.responseText);
                current_task_id = task.task_id;
                if (current_task_id > 0) {
                    acceptReceiving(current_task_id);
                    self.postMessage(String(current_task_id));
                    result = getNames(task.text);
                    processedSuccessfully = true;
                } else {
                    whetherShouldStop = true;
                    if (current_task_id < 0) {
                        setTimeout(doWork, 5000)
                    } else {
                        self.close()
                    }
                }
            }
        } catch (err) {
            if (current_task_id)
                rollbackTask(current_task_id)
        }
    };
    request.open('GET', '/get-task', false);
    request.send();
    if (processedSuccessfully) {
        sendResultAsJSON(current_task_id, result);
        self.postMessage('done');
        current_task_id = false;
    }
    return whetherShouldStop;
}

function doWork(e) {
    while (!workCycle()) {
    }
}

self.addEventListener('message', doWork);
