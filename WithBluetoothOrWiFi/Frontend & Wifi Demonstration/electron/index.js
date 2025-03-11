document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port = 65432;
var server_addr = "192.168.1.21";   // the IP address of your Raspberry PI

function clientCommand(input){
    
    const net = require('net');
    
    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('connected to server!');
        // send the message
        client.write(`${input}\r\n`);
    });
    
    // get the data from the server and parse through the stats returned
    client.on('data', (data) => {
        let serverData = data.toString().trim();
        document.getElementById("bluetooth").innerHTML = serverData;
        console.log(serverData);

        let stats = serverData.split("\n");
        //order is battery, temp, speed from wifi_server.py -> send_data()
        let battery = stats[0].trim();
        let temp = stats[1].trim();
        let speed = stats[2].trim();
        document.getElementById("battery").innerText = battery;
        document.getElementById("temperature").innerText = temp;
        document.getElementById("speed").innerText = speed;

        client.end();
        client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });
}

// for detecting which key is been pressed w,a,s,d
function updateKey(e) {

    e = e || window.event;

    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "blue";
        clientCommand("w");
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "blue";
        clientCommand("s");
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "blue";
        clientCommand("a");
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "blue";
        clientCommand("d");
    }
}

// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "red";
    document.getElementById("downArrow").style.color = "red";
    document.getElementById("leftArrow").style.color = "red";
    document.getElementById("rightArrow").style.color = "red";
}


// // update data for every 50ms
// function update_data() {
//     setInterval(function () {
//         // get image from python server
//         client();
//     }, 50);
// }
