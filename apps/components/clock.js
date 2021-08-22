let Clock = ( sketch ) => {
  sketch.name = "clock";

  let r;
  let ec = 10;

  let eh, emin, esec, emilli;
  let h,min, sec, milli;
  let prevsec;

  let color;

  sketch.movable = true;
  sketch.latched = false;
  sketch.activated = false;
  sketch.clickable = false;
  sketch.to_update = false;

  sketch.set = (p1, p2, w, h) => {
    sketch.width = w;
    sketch.height = h;
    sketch.x = p1;
    sketch.y = p2;
    sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);
    // sketch.selfCanvas.hide();
    r = sketch.min(w, h)*0.5 - 3*ec;
    sketch.angleMode(DEGREES);
    sketch.activated = true;
  };

  sketch.setPosition = (x, y) => {
    x = sketch.constrain(x, 0, sketch.windowWidth - sketch.width);
    y = sketch.constrain(y, 0, sketch.windowHeight - sketch.height);
    sketch.x = x;
    sketch.y = y;
    sketch.selfCanvas.position(x, y);
  }

  sketch.show = () => {
    sketch.clear();
    sketch.push();
    sketch.translate(sketch.width/2,sketch.height/2);
    sketch.rotate(-90);
    h = sketch.hour();
    min = sketch.minute();
    sec = sketch.second();
    milli = sketch.millis();

    sketch.strokeWeight(3);
    eh = sketch.map(h % 12, 0 , 12, 0, 360);
    sketch.noFill();
    sketch.stroke(76, 0, 153);
    sketch.arc(0,0,2*r,2*r,0,eh);

    sketch.push();
    sketch.rotate(eh);
    sketch.stroke(76, 0, 153);
    sketch.line(0,0,r * 0.4,0);
    sketch.pop();

    emin = sketch.map(min, 0 , 60, 0, 360);
    sketch.noFill();
    sketch.stroke(200, 200, 0);
    sketch.arc(0,0,2*r+ec,2*r+ec,0,emin);

    sketch.push();
    sketch.rotate(emin);
    sketch.stroke(200, 200, 0);
    sketch.line(0,0,r * 0.6,0);
    sketch.pop();

    esec = sketch.map(sec, 0 , 60, 0, 360);
    sketch.noFill();
    sketch.stroke(50,150,255);
    sketch.arc(0,0,2*r+2*ec,2*r+2*ec,0,esec);

    sketch.push();
    sketch.rotate(esec);
    sketch.stroke(50,150,255);
    sketch.line(0,0,r * 0.8,0);
    sketch.pop();

    emilli = sketch.map(milli, 0 , 1000, 0, 360);
    sketch.noFill();
    sketch.stroke(100, 255, 200);
    sketch.arc(0,0,2*r+3*ec,2*r+3*ec,0,emilli);

    // sketch.push();
    // sketch.rotate(emilli);
    // sketch.stroke(100, 255, 200);
    // sketch.line(0,0,r * 0.9,0);
    // sketch.pop();
    sketch.pop();
  };

  sketch.clearSketch = () => {
  }
};
