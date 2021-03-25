let Pikachu = (sketch) => {
    sketch.name = "pikachu";


    sketch.movable = false;
    sketch.latched = false;
    sketch.activated = false;
    sketch.clickable = true;

    sketch.pikachu_model;
    sketch.cursor = [-100, -100, 1];

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height, WEBGL).position(sketch.x, sketch.y);

        sketch.pikachu_model = new Model(sketch.cursor[0], sketch.cursor[1], sketch.cursor[2], pikachu_model);

        sketch.activated = true;
    };


    sketch.show = () => {
        sketch.clear();
        sketch.push();
        sketch.pikachu_model.show();
        sketch.pikachu_model.update(sketch.cursor[0], sketch.cursor[1], sketch.cursor[2]);
        sketch.pop();
    };


    class Model {
        constructor(x, y, s, m) {
            this.x = x;
            this.y = y;
            this.s = s;
            this.model = m;
        }
        show() {
            sketch.push();
            sketch.translate(this.x, this.y, 0);
            sketch.scale(this.s);
            sketch.normalMaterial(); 
            sketch.model(this.model);
            sketch.pop();
        }
        update(x, y) {
            this.x = x;
            this.y = y;
        }
    }
}