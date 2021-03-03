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
        sketch.menu = new Menu(sketch.x, sketch.y, 3, 100, [])
    };


    sketch.show = () => {
        sketch.clear();
        sketch.push();
        for (let i = 0; i < sketch.menu.bubbles.length; i++) {
            sketch.menu.bubbles[i].show();
            sketch.menu.bubbles[i].update(sketch.x, sketch.y);
        }
        sketch.pop();
    };


    class Menu {
        constructor(x, y, nb, d, choices) {
            this.x = x;
            this.y = y;
            this.nb = nb;
            this.d = d;
            this.choices = choices;
    
            this.slots = [Math.PI / 3, 2 * Math.PI / 3, Math.PI, 0];
            this.bubbles = [];
    
            for (let i = 0; i < nb; i++) {
                this.bubbles.push(new Bubble(this.x, this.y, this.slots[i], this.d, this.choices[i]));
            }
        }
    }

    class Bubble {
        constructor(x, y, angle, d, choice) {
            this.x = x + this.per * this.d * Math.cos(this.angle);
            this.y = y - this.per * this.d * Math.sin(this.angle);
            this.angle = angle;
            this.d = d;
            this.choice = choice;
            this.r = this.d / 2;
            this.per = 0;
            this.c = 0;
            this.mul = 0.99;
            this.color = 200;
        }
    
        show() {
            sketch.stroke(255);
            sketch.fill(200, 0.7);
            sketch.ellipse(this.x , this.y, this.r * this.per);
            // ellipse(this.x, this.y, this.r * this.per);
        }
    
        update(x, y) {
            this.x = x + this.per * this.d * Math.cos(this.angle);
            this.y = y - this.per * this.d * Math.sin(this.angle);
            if (!display_bubbles) {
                this.per *= this.mul;
            } else {
                if (this.per < 1) {
                    this.per += 0.04;
                }
            }
        }

        // clicked() {
            
        // }
    }
}