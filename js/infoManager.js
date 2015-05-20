/**
 * Created by mandriy on 3/10/15.
 */


importScripts('utils.js');

function getSystemSnapshotObject() {
    var snapshotRequest = createRequest();
    var systemSnapshot;
    snapshotRequest.onreadystatechange = function () {
        if (snapshotRequest.readyState == 4 && snapshotRequest.status == 200) {
            var pureSnapshot = JSON.parse(snapshotRequest.responseText);
            var tasks_number = pureSnapshot.done + pureSnapshot.available + pureSnapshot.active ;
            systemSnapshot = {
                nodesNumber: pureSnapshot.active ,
                donePercentage: (pureSnapshot.done / tasks_number) * 100,
                remainPercentage : (pureSnapshot.available / tasks_number) * 100 ,
                progressPercentage : (pureSnapshot.active / tasks_number * 100)
            }
        }
    };
    snapshotRequest.open('GET', '/system-snapshot', false);
    snapshotRequest.send();
    return systemSnapshot;
}

self.addEventListener('message', function(e) {
    var intervalID;
    var request_send_snapshot = function () {
                    var systemSnapshot = getSystemSnapshotObject();
                    self.postMessage(systemSnapshot);
                    if (systemSnapshot.donePercentage === 100) {
                        clearInterval(intervalID);
                        self.close();
                    }
                };
    request_send_snapshot();
    intervalID = setInterval(request_send_snapshot, 2000);
});

