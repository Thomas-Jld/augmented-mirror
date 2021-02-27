let Pose = ( sketch ) => {
  let body_pos = {};
  let display = false;

  let xoffset = 20;  // millimeters
  let yoffset = 50;

  let screenwidth = 392.85; //millimeters
  let screenheight = 698.4;

  let junctions = [[[ 0, 1],[ 0, 4],[ 1, 2],[ 2, 3],[ 3, 7],
                    [ 4, 5],[ 5, 6],[ 6, 8]],
                    [[9,10]],
                    [[11,12],[11,13],[11,23],[12,14],[12,24],
                    [13,15],[14,16],[15,17],[15,19],[15,21],
                    [16,18],[16,20],[16,22],[17,19],[18,20],
                    [23,24],[23,25],[24,26],[25,27],[26,28],
                    [27,29],[27,31],[28,30],[28,32]]];

  let keypoints = ['nose', 'left_eye_inner', 'left_eye', 'left_eye_outer', 
                  'right_eye_inner', 'right_eye', 'right_eye_outer',
                  'left_ear', 'right_ear', 'mouth_left', 'mouth_right', 
                  'left_shoulder', 'right_shoulder', 'left_elbow',
                  'right_elbow', 'left_wrist', 'right_wrist', 'left_pinky',
                  'right_pinky', 'left_index', 'right_index', 'left_thumb',
                  'right_thumb', 'left_hip', 'right_hip', 'left_knee',
                  'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
                  'left_foot_index', 'right_foot_index'];


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


    socket.on('updateJoint',
      function(data) {
        body_pos = data;
        // console.log(data);
      }
    );
  };


  sketch.show = () => {
    sketch.selfCanvas.clear();
    socket.emit('nextJoint', true);
    for(var part in body_pos) {
      if(part.slice(2,4) != [-1,-1]){
        sketch.fill(200);
        let x = width/2 - width*(part[2] - xoffset)/screenwidth;
        let y = height*(part[3] - yoffset)/screenheight;
        sketch.ellipse(x ,y ,30);
        sketch.text(part[1], x + 20, y + 20);
      }
    }
    sketch.drawLine();
  }

  sketch.drawLine = () => {
    sketch.stroke(255);
    sketch.strokeWeight(4);
    junctions.forEach(parts => {
      parts.forEach(pair => {
        try {
          if (body_pos[pair[0]].slice(2, 4) != [-1, -1] &&
            body_pos[pair[1]].slice(2, 4) != [-1, -1]) {
            let x1 = width / 2 - width * (body_pos[pair[0]][2] - xoffset) / screenwidth;
            let y1 = height * (body_pos[pair[0]][3] - yoffset) / screenheight;
            let x2 = width / 2 - width * (body_pos[pair[1]][2] - xoffset) / screenwidth;
            let y2 = height * (body_pos[pair[1]][3] - yoffset) / screenheight;
            if (y1 > 0 && y2 > 0) {
              sketch.line(x1, y1, x2, y2);
            }
          }
        } catch (e) {}
      })
    });
  }
}
