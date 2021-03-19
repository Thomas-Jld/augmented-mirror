let Selector = (sketch) => {
    sketch.name = "selector";

    sketch.movable = true;
    sketch.latched = false;
    sketch.activated = true;
    sketch.clickable = true;
    sketch.display_bubbles = false;

    sketch.mx = 0;
    sketch.my = 0;

    sketch.cursor = [0, 0];

    // sketch.rotation = 0;
    sketch.sliding = 0;

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);
        sketch.angleMode(RADIANS);
        sketch.menu = new Menu(sketch.x, sketch.y, 4, 150, [0, 1, 2, 3]);
    };


    sketch.show = () => {
        sketch.clear();
        sketch.push();
        for (let i = 0; i < sketch.menu.bubbles.length; i++) {
            sketch.menu.bubbles[i].show();
            sketch.menu.bubbles[i].update(sketch.mx, sketch.my);
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

            this.slots = [-2 * this.d, -this.d, 0, this.d, 2 * this.d];
            this.bubbles = [];

            for (let i = 0; i < nb; i++) {
                this.bubbles.push(new Bubble(this.x, this.y, this.slots[i], this.d, this.choices[i], this));
            }
        }

        unselect() {
            for (let i = 0; i < this.bubbles.length; i++) {
                this.bubbles[i].selected = false;
            }
        }
    }

    class Bubble {
        constructor(x, y, slide, d, choice, parent) {
            this.x = x;
            this.y = y;
            // this.angle = angle;
            this.slide = slide;
            this.rx = this.x;
            this.ry = this.y;
            this.d = d;
            this.choice = choice;
            this.r = this.d / 2;
            this.per = 0;
            this.mul = 0.92;
            this.color = 200;
            this.c = 0;
            this.selected = false;
            this.parent = parent;
        }

        show() {
            sketch.stroke(255);
            sketch.strokeWeight(6);
            if (this.selected) {
                sketch.fill(255, 129, 0);
            } else {
                sketch.fill(100, 0.7);
            }
            if (this.per > 0.1) {
                sketch.ellipse(this.rx, this.ry, this.r * this.per);
            }
            // ellipse(this.x, this.y, this.r * this.per);
        }

        update(x, y) {
            this.x = lerp(this.x, x, 0.6);
            this.y = lerp(this.y, y, 0.6);
            this.rx = this.x + this.per * this.d / 2;
            this.ry = this.y + this.per * this.slide - sketch.sliding;
            if (!sketch.display_bubbles) {
                this.per *= this.mul;
            } else {
                if (this.per < 1) {
                    this.per += 0.04;
                }
                if (!this.selected && sketch.dist(this.rx,
                        this.ry, sketch.cursor[0], sketch.cursor[1]) < this.r) {
                    this.c += 1;
                    sketch.stroke(255);
                    sketch.strokeWeight(4);
                    sketch.noFill();
                    //console.log(this.c);
                    sketch.arc(this.rx, this.ry,
                        2 * this.r, 2 * this.r,
                        0, 2 * Math.PI * this.c / 40);
                    if (this.c >= 40) {
                        this.parent.unselect();
                        sketch.sliding = this.slide;
                        this.selected = true;
                        choseAction(this.choice);
                    }
                } else {
                    this.c = 0;
                }
            }

        }
    }

    class SelectBar {
        constructor(x, y, d, choice, parent) {
            this.x = x;
            this.y = y;
            this.d = d;
            this.choice = choice;
            this.parent = parent;
        }
    }
}