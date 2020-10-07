let socket;
let body_pos;
let data = {};
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
  if(display){
    socket.emit('next', true);
  }
  for(var part in data) {
    if(data[part] != -1){
      fill(0);
      ellipse(data[part][0]/10, data[part][1]/10, 10);
    }
  }
}

function keyPressed(){
  if(key == ENTER){
    display = true;
  }
  else{
    display = false;
  }
}
