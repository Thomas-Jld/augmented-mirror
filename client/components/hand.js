let Hands = ( sketch ) => {
  let hands_joints = [];
  let display = false;

  let xoffset = 50;  // millimeters
  let yoffset = 50;

  let screenwidth = 392.85; //millimeters
  let screenheight = 698.4;

  let junctions = [[0, 1], [0, 5], [0, 9], [0, 13], [0, 17], [1, 2], [2, 3], [3, 4], [5, 9],
                  [5, 6], [6, 7], [7, 8], [9, 10], [9, 13], [10, 11], [11, 12], [13, 14], [13, 17],
                  [14, 15], [15, 16], [17, 18], [18, 19], [19, 20]];

  let keypoints = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];


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


    socket.on('updateHands',
      function(data) {
        hands_joints = data;
        console.log(data)
      }
    );
  };


  sketch.show = () => {
    sketch.selfCanvas.clear();
    socket.emit('nextHands', true);
    let ratio = hands_joints[hands_joints.length - 1];
    for(let i = 0; i < hands_joints.length - 1; i++){
      for(var index in keypoints) {
        sketch.fill(0, 255, 0);
        let ratio = hands_joints[hands_joints.length - 1];
        let x = width*(hands_joints[i][index][0]*ratio[0] - xoffset)/screenwidth;
        let y = height*(hands_joints[i][index][1]*ratio[1] - yoffset)/screenheight;
        sketch.ellipse(x ,y , 5);
        // sketch.text(i, x + 20, y + 20);
      }
    }
    sketch.drawLine();
  }

  sketch.drawLine = () => {
    sketch.stroke(0, 255, 0);
    sketch.strokeWeight(4);
    let ratio = hands_joints[hands_joints.length - 1];
    junctions.forEach(pair => {
      for(let i = 0; i < hands_joints.length - 1; i++){
        let x1 = width*(hands_joints[i][pair[0]][0]*ratio[0] - xoffset)/screenwidth;
        let y1 = height*(hands_joints[i][pair[0]][1]*ratio[1] - yoffset)/screenheight;
        let x2 = width*(hands_joints[i][pair[1]][0]*ratio[0] - xoffset)/screenwidth;
        let y2 = height*(hands_joints[i][pair[1]][1]*ratio[1] - yoffset)/screenheight;
        sketch.line(x1, y1, x2, y2);
      }
    });
  }
}
  