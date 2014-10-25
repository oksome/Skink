/*
Copyright (c) 2014 "OKso http://okso.me"

This file is part of Skink.

Intercom is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

setup_skink_websocket = function() {
    "use strict";

    var websocket = "ws://" + window.location.host + "/skink/socket?" + location.pathname;
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
            command = command[1];
            console.log("callback_id = [ " + callback_id + " ]");
            console.log("processed command = [ " + command + " ]");
            try {
                var result = eval(command);
                console.log("result = [" + result + "]");
                //ws.send("?" + callback_id + "=" + typeof(result) + ":" + result);
                ws.send(JSON.stringify({
                    "action": "eval",
                    "callback": callback_id,
                    "value": result
                    }));
            }
            catch(err) {
                console.log("error : " + err.name + err.message);
                ws.send(JSON.stringify({
                    "action": "exception",
                    "callback": callback_id,
                    "name": err.name,
                    "description": err.message
                    }));
            }
        }
        console.log("log" + evt.data);
    };
    ws.onopen = function() {
        document.getElementById("stderr").innerHTML = "";

        ws.send(JSON.stringify({
            "action": "info",
            "message": "%(username)s entered the room"
        }));
    };
    ws.onclose = function(evt) {
        document.getElementById("stderr").innerHTML = "Connection closed by server " + evt.reason + "\n";

         setTimeout(function () {
            // Connection has closed so try to reconnect every 3 seconds.
            setup_skink_websocket();
        }, 3*1000);
    };

    window.skink = {
        ws: ws,
        call: function(name, args) {
            this.ws.send(JSON.stringify({
                action: "callback",
                callback: name,
                args: args
            }));
        }
    };
};

window.onload = setup_skink_websocket();
