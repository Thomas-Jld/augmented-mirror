const io = require('socket.io')(5000);
// const { exec } = require('child_process');

let body_pose = [];
let face_mesh = [];
let right_hand_pose = [];
let left_hand_pose = [];

let origin;
let apps = [];


// exec('ls | grep js', (err, stdout, stderr) => {
//   if (err) {
//     //some err occurred
//     console.error(err)
//   } else {
//    // the *entire* stdout and stderr (buffered)
//    console.log(`stdout: ${stdout}`);
//    console.log(`stderr: ${stderr}`);
//   }
// });

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
    // console.log(data);
  });

  socket.on('get_face', (data) => {
    socket.emit('send_face', face_mesh);
  });

  socket.on('get_pose', (data) => {
    socket.emit('send_pose', body_pose);
  });

  socket.on('get_right_hand', (data) => {
    socket.emit('send_right_hand', right_hand_pose);
  });

  socket.on('get_left_hand', (data) => {
    socket.emit('send_left_hand', left_hand_pose);
  });

  socket.on('pause', (data) => {
    origin.emit('pause', data)
  });
});
