let Hands = ( sketch ) => {
  let hands_joints = [];
  let display = false;

  let xoffset = 0;  // millimeters
  let yoffset = 100;

  let screenwidth = 392.85; //millimeters
  let screenheight = 698.4;

  let junctions = [[[ 0,  1], [ 0,  5], [ 0,  9], [ 0, 13], [ 0, 17], [ 5,  9], [ 9, 13], [13, 17]], 
                   [[ 1,  2], [ 2,  3], [ 3,  4]], 
                   [[ 5,  6], [ 6,  7], [ 7,  8]], 
                   [[ 9, 10], [10, 11], [11, 12]], 
                   [[13, 14], [14, 15], [15, 16]], 
                   [[17, 18], [18, 19], [19, 20]]];

  let keypoints = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];

  let xmul = 0.16
  let ymul = -0.15
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

    sketch.colorMode(HSB);
    socket.on('updateHands',
      function(data) {
        hands_joints = data;
      }
    );
  };


  sketch.show = () => {
    sketch.selfCanvas.clear();
    socket.emit('nextHands', true);
    for(var part in hands_joints) {
      if(part.slice(2,4) != [-1,-1]){
        sketch.fill(200);
        let x = width/2 - width*(part[2] - xoffset)/screenwidth;
        let y = height*(part[3] - yoffset)/screenheight;
        sketch.ellipse(x ,y , 30);
        sketch.text(part, x + 20, y + 20);
      }
    }
    sketch.drawLine();
  }

  sketch.drawLine = () => {
    sketch.stroke(0, 255, 0);
    sketch.strokeWeight(4);
    let ratio = hands_joints[hands_joints.length - 1];
    junctions.forEach(parts => {
      parts.forEach(pair => {
        try{
          if(hands_joints[pair[0]].slice(2,4) != [-1,-1] && hands_joints[pair[1]].slice(2,4) != [-1,-1]){
            let x1 = width/2 - width*(hands_joints[pair[0]][2] - xoffset)/screenwidth;
            let y1 = height*(hands_joints[pair[0]][3] - yoffset)/screenheight;
            let x2 = width/2 - width*(hands_joints[pair[1]][2] - xoffset)/screenwidth;
            let y2 = height*(hands_joints[pair[1]][3] - yoffset)/screenheight;
            sketch.line(x1, y1, x2, y2);
          }
        }
        catch(e){
        }
      })
    });
  }
}
  