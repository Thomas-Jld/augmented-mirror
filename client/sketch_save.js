let socket;
let body_pos = {};
let display = false;

let xoffset = 50;  // millimeters
let yoffset = 50;

let screenwidth = 392.85; //millimeters
let screenheight = 698.4;

let junctions = [[1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7], [1, 8], [8, 9],
                [9, 10], [1, 11], [11, 12], [12, 13], [1, 0], [0, 14], [14, 16],
                [0, 15], [15, 17]];

let keypoints = ['nose', 'neck', 'r_sho', 'r_elb', 'r_wri', 'l_sho', 'l_elb',
                'l_wri', 'r_hip', 'r_knee', 'r_ank', 'l_hip', 'l_knee', 'l_ank',
                'r_eye', 'l_eye', 'r_ear', 'l_ear'];



let modules = [];
let mOffsetX;
let mOffsetY;

let objectsSelected = false;


function setup() {
  fullscreen(true);
  createCanvas(windowWidth, windowHeight);
  socket = io.connect('http://0.0.0.0:5000');

  let clock = new p5(Clock);
  clock.set(width - 200, 0, 200, 200);
  modules.push(clock);

  let bubble = new p5(HeartBubble);
  bubble.set(0, 0, width, height);
  modules.push(bubble);

  let multiplications = new p5(Multiplications);
  multiplications.set(0, 0, 150, 150);
  modules.push(multiplications);

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
      ellipse(x ,y , 30);
      text(part, x + 20, y + 20);
    }
  }
  drawLine();
  modules.forEach(m => {
    if(m.activated){
      m.show();
      if(m.latched){
        m.setPosition(mouseX - m.OffsetX, mouseY - m.OffsetY);
      }
    }
  });
}

function drawLine(){
  stroke(255);
  strokeWeight(4);
  junctions.forEach(pair => {
    try{
    if(body_pos[keypoints[pair[0]]] != -1 && body_pos[keypoints[pair[1]]] != -1){
      let x1 = width/2 - width*(body_pos[keypoints[pair[0]]][0] - xoffset)/screenwidth;
      let y1 = height*(body_pos[keypoints[pair[0]]][1] - yoffset)/screenheight;
      let x2 = width/2 - width*(body_pos[keypoints[pair[1]]][0] - xoffset)/screenwidth;
      let y2 = height*(body_pos[keypoints[pair[1]]][1] - yoffset)/screenheight;
      line(x1, y1, x2, y2);
    }
  }
  catch(e){

  }
  });
}

function keyPressed(){
  if(key == "c"){
    modules.forEach(m => {
      m.clearSketch();
    });
  }
}

function mousePressed(){
  let selected = false;
  let objectSelected = false;
  modules.forEach(m => {
    if(m.movable && mouseX > m.x && mouseY > m.y && mouseX < m.x + m.width && mouseY < m.y + m.height){
      selected = true;
      if(!objectsSelected){
        m.latched = true;
        objectSelected = true;
        m.OffsetX = mouseX - m.x;
        m.OffsetY = mouseY - m.y;
      }
      else {
        m.latched = false;
      }
    }
  });

  objectsSelected = objectSelected;

  if(!selected){
    modules.forEach(m => {
      if(!m.movable && m.clickable){
        m.onClicked(mouseX, mouseY);
      }
    });
  }
}
