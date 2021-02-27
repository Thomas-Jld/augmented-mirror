let Selector = (sketch) => {

    sketch.movable = true;
    sketch.latched = false;
    sketch.activated = true;
    sketch.clickable = true;
    sketch.display_bubbles = true;

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);
        sketch.angleMode(DEGREES);
        sketch.menu = new Menu(sketch.x, sketch.y, 3, 20, [])
    };


    sketch.show = () => {
        sketch.clear();
        sketch.push();
        sketch.fill(255, 0, 0);
        sketch.ellipse(sketch.x, sketch.y, 20);
        for (let i = 0; i < sketch.menu.bubbles.length; i++) {
            sketch.menu.bubbles[i].show();
            sketch.menu.bubbles[i].update();
        }
        sketch.pop();;
    };


    class Menu{
        constructor(x, y, nb, r, choices){
            this.x = x;
            this.y = y;
            this.nb = nb;
            this.r = r;
            this.choices = choices;

            this.slots = [2*Math.PI/3, Math.PI/3, Math.PI, 0];
            this.bubbles = [];

            for(let i = 0; i <= nb; i++){
                this.bubbles.push(new Bubble(this.x, this.y, this.slots[i], 20, this.choices[i]));
            }
        }
    }

    class Bubble {
        constructor(x, y, angle, r, choice) {
            this.x = x;
            this.y = y;
            this.angle = angle;
            this.r = r;
            this.choice = choice;
            this.d = 50;
            this.per = 0;
            this.mul = 0.99;
            this.color = [100, 0.8];
        }

        show() {
            sketch.stroke(255);
            sketch.fill(this.color);
            sketch.ellipse(this.x*(1+this.per*this.d*Math.cos(this.angle)), this.y*(1+this.per*this.d*Math.sin(this.angle)), this.r*this.per);
        }

        update() {
            if (!sketch.display_bubbles){
                this.per = this.per * this.mul;
            }
            else{
                if(this.per != 1){
                    this.per += 0.02;
                }
            }
        }
    }
}