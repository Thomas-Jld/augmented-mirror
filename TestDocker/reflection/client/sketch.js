let socket;
let body_pos = {};
let display = false;

function setup() {
  createCanvas(windowWidth, windowHeight);
  socket = io.connect('http://0.0.0.0:5000');


  socket.on('update',
    function(data) {
      body_pos = data;
      console.log(data);
    }
  );
  frameRate(30);
}

function draw() {
  background(200);
  if(keyIsPressed){
    socket.emit('next', true);
  }
  for(var part in body_pos) {
    if(body_pos[part] != -1){
      fill(0);
      ellipse(body_pos[part][0]/10, body_pos[part][1]/10, 10);
    }
  }
}
