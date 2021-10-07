let Selector = (sketch) => {
    sketch.name = "selector";

    sketch.movable = false;
    sketch.latched = false;
    sketch.activated = false;
    sketch.clickable = false;
    sketch.display_bubbles = false;
    sketch.to_update = false;

    sketch.mx = 0;
    sketch.my = 0;

    sketch.cursor = [0, 0];

    // sketch.rotation = 0;
    sketch.sliding = 0;

    let description = `This is the alpha version of an interractive mirror. Place yourself at about 1m50 for a better experience. Use your left hand to display the menu.`

    let icons = ["info.svg", "disco.svg", "settings.svg"];

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);

        sketch.angleMode(RADIANS);
        sketch.textAlign(CENTER, CENTER);
        sketch.textStyle(BOLD);

        sketch.imageMode(CENTER);

        sketch.menu = new Menu(
            sketch.x,
            sketch.y,
            150,
            [
                description,
                ["Dance n°2", "Dance n°1"],
                ["Show Face", "Show Clock", "Show Pose", "Show Hands"],
            ],
            icons
        );

        sketch.activated = true;
    };


    sketch.show = () => {
        sketch.clear();
        sketch.push();
        sketch.menu.show();
        sketch.menu.update(sketch.mx, sketch.my);
        sketch.pop();
    };


    class Menu {
        constructor(x, y, d, choices, icons) {
            this.x = x;
            this.y = y;
            this.d = d;
            this.choices = choices;

            this.slots = [0, -this.d, this.d, -2 * this.d, 2 * this.d];
            this.bubbles = [];

            for (let i = 0; i < this.choices.length; i++) {
                this.bubbles.push(new Bubble(this.x, this.y, this.slots[i], this.d, this.choices[i], this, icons[i]));
            }
        }

        unselect() {
            for (let i = 0; i < this.bubbles.length; i++) {
                if (this.bubbles[i].selected) {
                    this.bubbles[i].selected = false;
                    for (let j = 0; j < this.bubbles[i].bars.length; j++) {
                        this.bubbles[i].bars[j].per = 0;
                    }
                }
            }
        }

        update(x, y) {
            for (let i = 0; i < this.bubbles.length; i++) {
                this.bubbles[i].update(x, y);
            }
        }

        show() {
            for (let i = 0; i < this.bubbles.length; i++) {
                this.bubbles[i].show();
            }
        }
    }

    class Bubble {
        constructor(x, y, slide, d, choice, parent, icon) {
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
            this.c = 0;
            this.selected = false;
            this.parent = parent;

            this.slots = [0, -3 * this.d / 4, 3 * this.d / 4, 3 * this.d / 2, -3 * this.d / 2, 2 * this.d];
            this.bars = [];
            this.icon = sketch.loadImage("components/icons/" + icon);

            if (typeof (this.choice) == "object") {
                for (let i = 0; i < this.choice.length; i++) {
                    this.bars.push(
                        new SelectBar(
                            this.rx,    // x
                            this.ry,    // y
                            this.slots[i],  // y offset
                            this.d,
                            this.choice[i],
                            this
                        )
                    );
                }

            } else if (typeof (this.choice) == "string") {
                this.bars.push(
                    new InfoPanel(
                        this.rx,     // x
                        this.ry,     // y
                        this.d * 2,    // w
                        this.d * 2,    // h
                        this.d * 0.5,    // xoffset
                        this.choice, //content
                        this         //parent
                    )
                );
            }
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
                sketch.image(this.icon, this.rx, this.ry, this.r * this.per * 2/3, this.r * this.per *2/3);
            }
            if (this.selected) {
                for (let i = 0; i < this.bars.length; i++) {
                    this.bars[i].show();
                }
            }
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
                } else {
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
                            //sketch.sliding = this.slide;
                            this.selected = true;

                            if (typeof (this.choice) !== "object") {
                                choseAction(this.choice);
                            }
                        }
                    } else {
                        this.c = 0;
                    }
                }
            }
            if (this.selected) {
                for (let i = 0; i < this.bars.length; i++) {
                    this.bars[i].update(this.rx, this.ry);
                }
            }
        }

        unselect() {
            for (let i = 0; i < this.bars.length; i++) {
                this.bars[i].selected = false;
            }
        }
    }

    class SelectBar {
        constructor(x, y, yoffset, d, choice, parent) {
            this.x = x;
            this.y = y;
            this.yoffset = yoffset;
            this.d = d / 2;
            this.w = this.d * 4;
            this.h = this.d;
            this.choice = choice;
            this.parent = parent;
            this.selected = true;

            this.c = 0;

            this.per = 0;
            this.mul = 0.92;
            this.selection_time = 40;
        }

        show() {
            if (this.parent.selected && this.per > 0.1) {
                sketch.stroke(255);
                sketch.strokeWeight(2);
                sketch.fill(0);
                sketch.rect(this.rx, this.ry - this.h / 2 * this.per, this.w * this.per, this.h * this.per);
                if (this.selected) {
                    sketch.fill(255, 129, 0);
                    sketch.stroke(255, 129, 0);
                } else {
                    sketch.fill(255);
                    sketch.stroke(255);
                }
                sketch.noStroke();
                sketch.textSize(this.per * this.h / 2);
                sketch.text(this.choice, this.rx + this.per * this.w / 2, this.ry);
                if (this.yoffset == 0) {
                    sketch.fill(255);
                    sketch.stroke(255);
                    sketch.triangle(this.rx, this.ry - this.per * this.h / 3,
                                    this.rx, this.ry + this.per * this.h / 3,
                                    this.rx - 1.7 * this.per * this.h / 3, this.ry);
                }
            }
        }

        update(x, y) {
            this.x = x;
            this.y = y;
            this.rx = this.x + 3 * this.per * this.d / 2;
            this.ry = this.y + this.per * this.yoffset - sketch.sliding;

            if (!this.parent.selected || !sketch.display_bubbles) {
                this.per *= this.mul;
            } else {
                if (this.per < 1) {
                    this.per += 0.1;
                    if(this.per > 1){
                        this.per = 1;
                    }
                } else {
                    if (sketch.cursor[0] > this.rx - this.h / 4 && sketch.cursor[0] < this.rx + this.w + this.h / 4 &&
                        sketch.cursor[1] > this.ry - 3 * this.h / 4 && sketch.cursor[1] < this.ry + 3 * this.h / 4) {

                        this.c += 1;

                        sketch.stroke(255);
                        sketch.strokeWeight(4);

                        sketch.noFill();
                        //console.log(this.c);
                        if (this.c < this.selection_time / 20) {
                            sketch.line(this.rx + this.w + this.h / 4, this.ry,
                                this.rx + this.w + this.h / 4, this.ry - 3 * this.h / 4 * this.c / (this.selection_time / 20));
                        } else if (this.c < 9 * this.selection_time / 20) {
                            sketch.line(this.rx + this.w + this.h / 4, this.ry,
                                this.rx + this.w + this.h / 4, this.ry - 3 * this.h / 4);
                            sketch.line(this.rx + this.w + this.h / 4, this.ry - 3 * this.h / 4,
                                this.rx + this.w + this.h / 4 - (this.w + this.h / 2) * (this.c - this.selection_time / 20) / (8 * this.selection_time / 20), this.ry - 3 * this.h / 4);

                        } else if (this.c < 11 * this.selection_time / 20) {
                            sketch.line(this.rx + this.w + this.h / 4, this.ry,
                                this.rx + this.w + this.h / 4, this.ry - 3 * this.h / 4);
                            sketch.line(this.rx + this.w + this.h / 4, this.ry - 3 * this.h / 4,
                                this.rx - this.h / 4, this.ry - 3 * this.h / 4);
                            sketch.line(this.rx - this.h / 4, this.ry - 3 * this.h / 4,
                                this.rx - this.h / 4, this.ry - 3 * this.h / 4 + 3 * this.h / 4 * (this.c - 9 * this.selection_time / 20) / (2 * this.selection_time / 20));

                        } else if (this.c < 19 * this.selection_time / 20) {
                            sketch.line(this.rx + this.w + this.h / 4, this.ry,
                                this.rx + this.w + this.h / 4, this.ry - 3 * this.h / 4);
                            sketch.line(this.rx + this.w + this.h / 4, this.ry - 3 * this.h / 4,
                                this.rx - this.h / 4, this.ry - 3 * this.h / 4);
                            sketch.line(this.rx - this.h / 4, this.ry - 3 * this.h / 4,
                                this.rx - this.h / 4, this.ry + 3 * this.h / 4);
                            sketch.line(this.rx - this.h / 4, this.ry + 3 * this.h / 4,
                                this.rx - this.h / 4 + (this.w + this.h / 2) * (this.c - 11 * this.selection_time / 20) / (8 * this.selection_time / 20), this.ry + 3 * this.h / 4);

                        } else if (this.c < this.selection_time) {
                            sketch.line(this.rx + this.w + this.h / 4, this.ry,
                                this.rx + this.w + this.h / 4, this.ry - 3 * this.h / 4);
                            sketch.line(this.rx + this.w + this.h / 4, this.ry - 3 * this.h / 4,
                                this.rx - this.h / 4, this.ry - 3 * this.h / 4);
                            sketch.line(this.rx - this.h / 4, this.ry - 3 * this.h / 4,
                                this.rx - this.h / 4, this.ry + 3 * this.h / 4);
                            sketch.line(this.rx - this.h / 4, this.ry + 3 * this.h / 4,
                                this.rx + this.w + this.h / 4, this.ry + 3 * this.h / 4);
                            sketch.line(this.rx + this.w + this.h / 4, this.ry + 3 * this.h / 4,
                                this.rx + this.w + this.h / 4, this.ry + 3 * this.h / 4 - 3 * this.h / 4 * (this.c - 19 * this.selection_time / 20) / (this.selection_time / 20));
                        } else if (this.c == this.selection_time) {
                            // this.parent.unselect();
                            //sketch.sliding = this.slide;
                            this.selected = !this.selected;
                            choseAction(this.choice, this.selected);
                        }
                    } else {
                        this.c = 0;
                    }
                }
            }
        }
    }

    class InfoPanel {
        constructor(x, y, w, h, offset, content, parent) {
            this.x = x;
            this.y = y;
            this.w = w;
            this.h = h;
            this.offset = offset;
            this.content = content;
            this.parent = parent;
            this.size = 25;

            this.per = 0; // To animate the display when showing / hidding
            this.mul = 0.92;
        }

        show() {
            if(this.parent.selected && this.per > 0.5){
                sketch.stroke(255);
                sketch.strokeWeight(4);
                sketch.noFill();
                sketch.rect(
                    this.x + this.offset,
                    this.y - this.h / 2,
                    this.w,
                    this.h
                );

                sketch.stroke(255);
                sketch.fill(255);
                sketch.strokeWeight(2);
                sketch.textSize(this.size);
                sketch.text(
                    this.content,
                    this.x + this.offset + this.w * 0.05,
                    this.y - 0.45 * this.h,
                    this.w * 0.9,
                    this.h * 0.9
                );
            }
        }

        update(x, y) {
            this.x = x;
            this.y = y;
            // this.rx = this.x + this.per * this.offset;
            // this.ry = this.y;

            if (!this.parent.selected || !sketch.display_bubbles) {
                this.per *= this.mul;
            } else {
                this.per = 1;
            }
        }
    }
}
