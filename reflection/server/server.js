const io = require('socket.io')(5000);

let joint = {};
let mesh = {};
let hands = [];

io.on('connect', socket => {
  // either with send()
  console.log(socket);

  // or with emit() and custom event names
  socket.emit('greetings', "Hi !");

  socket.on('joint', (data) => {
    joint = data;
    console.log(data);
  });


  socket.on('mesh', (data) => {
    mesh = data;
    console.log(data);
  });

  socket.on('hands', (data) => {
    hands = data;
    console.log(data);
  });

  socket.on('nextJoint', (data) => {
    socket.emit('updateJoint', joint);
  });

  socket.on('nextHands', (data) => {
    socket.emit('updateHands', joint);
  });
});
