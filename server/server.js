const io = require('socket.io')(5000);

let body_pose = [];
let face_mesh = [];
let right_hand_pose = [];
let left_hand_pose = [];

let origin;
let apps = [];

io.on('connect', socket => {
  if (socket.handshake.headers["user-agent"].split('/')[0] == "python-requests"){
    origin = socket;
    console.log("python: " + socket.id)
  }
  else{
    apps.push(socket);
    console.log("new app: " + socket.id)
  }
  

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

  socket.on('pause', (data) => {
    origin.emit('pause', data)
  });
});
