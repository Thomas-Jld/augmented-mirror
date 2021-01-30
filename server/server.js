const io = require('socket.io')(5000);

let body_pose = [];
let face_mesh = [];
let right_hand_pose = [];
let left_hand_pose = [];

io.on('connect', socket => {
  // either with send()
  console.log(socket);

  // or with emit() and custom event names
  socket.emit('greetings', "Hi !");

  socket.on('global_data', (data) => {
    body_pose = data["body_pose"];
    right_hand_pose = data["right_hand_pose"];
    left_hand_pose = data["left_hand_pose"];
    face_mesh = data["face_mesh"];
    console.log(data);
  });


  socket.on('nextJoint', (data) => {
    socket.emit('updateJoint', body_pose);
  });

  socket.on('nextHands', (data) => {
    socket.emit('updateHands', right_hand_pose + left_hand_pose);
  });
});
