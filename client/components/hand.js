let Hands = ( sketch ) => {
    let body_pos = {};
    let display = false;
  
    let xoffset = 50;  // millimeters
    let yoffset = 50;
  
    let screenwidth = 392.85; //millimeters
    let screenheight = 698.4;
  
    let junctions = [[0, 1], [0, 5], [0, 9], [0, 13], [0, 17], [1, 2], [2, 3], [3, 4],
                    [5, 6], [6, 7], [7, 8], [8, 9], [13, 14], [14, 15], [15, 16],
                    [17, 18], [18, 19], [19, 20]];
  
    let keypoints = [0,1,,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
  
  
    sketch.movable = false;
    sketch.latched = false;
    sketch.activated = true;
    sketch.clickable = false;
  
    sketch.set = (p1, p2, w, h) => {
      sketch.width = w;
      sketch.height = h;
      sketch.x = p1;
      sketch.y = p2;
      sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);
  
  
      socket.on('update',
        function(data) {
          hands_joints = data;
        }
      );
    };
  
  
    sketch.show = () => {
      sketch.selfCanvas.clear();
      socket.emit('nextHands', true);
      for(var part in body_pos) {
        if(body_pos[part] != -1){
          sketch.fill(200);
          let x = width/2 - width*(body_pos[part][0] - xoffset)/screenwidth;
          let y = height*(body_pos[part][1] - yoffset)/screenheight;
          sketch.ellipse(x ,y , 30);
          sketch.text(part, x + 20, y + 20);
        }
      }
      sketch.drawLine();
    }
  
    sketch.drawLine = () => {
      sketch.stroke(0, 255, 0);
      sketch.strokeWeight(4);
      junctions.forEach(pair => {
        try{
        if(body_pos[keypoints[pair[0]]] != -1 && body_pos[keypoints[pair[1]]] != -1){
          let x1 = width/2 - width*(body_pos[keypoints[pair[0]]][0] - xoffset)/screenwidth;
          let y1 = height*(body_pos[keypoints[pair[0]]][1] - yoffset)/screenheight;
          let x2 = width/2 - width*(body_pos[keypoints[pair[1]]][0] - xoffset)/screenwidth;
          let y2 = height*(body_pos[keypoints[pair[1]]][1] - yoffset)/screenheight;
          sketch.line(x1, y1, x2, y2);
        }
      }
      catch(e){
  
      }
      });
    }
  }
  