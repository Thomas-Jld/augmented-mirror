let socket;
let body_pos = {};
let display = false;

let xoffset = -5;  // millimeters
let yoffset = 40;

let screenwidth = 392.85; //millimeters
let screenheight = 698.4;


function setup() {
  fullscreen(true);
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
  background(0);
  socket.emit('next', true);
  for(var part in body_pos) {
    if(body_pos[part] != -1){
      fill(200);
      let x = width/2 - width*(body_pos[part][0] - xoffset)/screenwidth;
      let y = height*(body_pos[part][1] - yoffset)/screenheight;
      ellipse(x ,y , 10);
      text(part, x + 20, y + 20);
    }
  }
}
