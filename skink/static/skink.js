$(document).ready(function() {
    "use strict";

    var websocket = "ws://" + window.location.host + "/realtime/";
    var ws;
    if (window.WebSocket) {
        ws = new WebSocket(websocket);
    }
    else if (window.MozWebSocket) {
        ws = new MozWebSocket(websocket);
    }
    else {
        alert("WebSocket Not Supported");
        return;
    }

    window.onbeforeunload = function(e) {
        console.log("Bye bye...");
        ws.close(1000, "%(username)s left the room");

        if (!e) e = window.event;
        e.stopPropagation();
        e.preventDefault();
    };
    ws.onmessage = function (evt) {
        console.log("received message [", evt.data + "]");

        // Execute a void command:
        if (evt.data.indexOf("$") === 0) {
            var command = evt.data.substr(1);
            //console.log('exec of [ ' + command + ' ]');
            eval(command);
        }

        // Execute a command and return the synchronously:
        else if (evt.data.indexOf("?") === 0) {
            var command = evt.data.substr(1).split("=", 2);
            console.log("raw command = [ " + command + " ]");
            var callback_id = command[0];
            var command = command[1];
            console.log("callback_id = [ " + callback_id + " ]");
            console.log("processed command = [ " + command + " ]");
            try {
                var result = eval(command);
                console.log("result = [" + result + "]");
                ws.send("?" + callback_id + "=" + typeof(result) + ":" + result);
            }
            catch(err) {
                console.log("error : " + err.name + err.message);
                ws.send("!" + callback_id + "=" + err.name + ":" + err.message);
            }
        }
        console.log("log" + evt.data);
    };
    ws.onopen = function() {
        ws.send("%(username)s entered the room");
    };
    ws.onclose = function(evt) {
        $("#stderr").val("Connection closed by server: " + evt.code + " \"" + evt.reason + "\"\n");
    };

    window.skink = ws;
});