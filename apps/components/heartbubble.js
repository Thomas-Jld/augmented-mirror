let HeartBubble = (sketch) => {
  sketch.name = "heart";

  let Balloon;
  let Balls = [];

  sketch.movable = false;
  sketch.latched = false;
  sketch.activated = false;
  sketch.clickable = true;
  sketch.to_update = false;

  sketch.set = (p1, p2, w, h) => {
    sketch.width = w;
    sketch.height = h;
    sketch.x = p1;
    sketch.y = p2;
    sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);
  };


  sketch.show = () => {
    sketch.clear();
    sketch.push();
  	for( let i = 0; i < Balls.length; i++){
    	Balls[i].show();
    	Balls[i].update();
  	}
    sketch.pop();
  };


  sketch.onClicked = (x, y) => {
  	Balls.push(new Ball(mouseX,mouseY,floor(random(200))));
  };

  sketch.clearSketch = () => {
    Balls = [];
  };

  class Ball{
  	constructor(x,y,s){
  		this.x = x;
  		this.y = y;
  		this.r = 1;
  		this.count = 0;
  		this.size = s;
  		this.color = [floor(random(255)),floor(random(255)),floor(random(255)),floor(random(150))];
  	}
  	show(){
  		sketch.fill(this.color);
  		sketch.noStroke();
  	  sketch.ellipse(this.x,this.y,this.r);
  	}
  	update(){
  		this.r = this.size*sin(radians(this.count));
  		this.count++;
  	}
  }
}
