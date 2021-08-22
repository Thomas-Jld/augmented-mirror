let Multiplications = (sketch) => {
  sketch.name = "multiplications";


  let tbl = 6;
  let mdl = 96;
  let r;
  let S1;
  let a = 0;

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

    r = sketch.min(w, h);
    sketch.angleMode(RADIANS);
    sketch.colorMode(HSB);
  };

  sketch.setPosition = (x, y) => {
    x = sketch.constrain(x, 0, sketch.windowWidth - sketch.width);
    y = sketch.constrain(y, 0, sketch.windowHeight - sketch.height);
    sketch.x = x;
    sketch.y = y;
    sketch.selfCanvas.position(x, y);
  };

  sketch.show = () => {
    sketch.clear();
    sketch.push();
    sketch.translate(sketch.width / 2, sketch.width / 2);
    sketch.noFill();
    sketch.stroke(255);
    // rotate(a);
    // a-=0.01;
    //ellipse(0,0,r);
    for (let i = 1; i <= mdl; i++) {
      let num = (i * tbl) % mdl;
      sketch.stroke((i / mdl) * 360, 255, 255);
      sketch.line(r / 2 * sketch.sin(TWO_PI * i / mdl), r / 2 * sketch.cos(TWO_PI * i / mdl), r / 2 * sketch.sin(TWO_PI * num / mdl), r / 2 * sketch.cos(TWO_PI * num / mdl));
    }
    tbl += 0.01;
    sketch.pop();
  };
}
