let Pikachu = (sketch) => {
    sketch.name = "pikachu";


    sketch.movable = false;
    sketch.latched = false;
    sketch.activated = false;
    sketch.clickable = true;
    sketch.to_update = true;

    sketch.pikachu_model;
    sketch.cursor = [100, 100, 100];

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height, WEBGL).position(sketch.x, sketch.y);

        sketch.pikachu_model = new Model(sketch.cursor[0], sketch.cursor[1], sketch.cursor[2], pikachu_model);

        sketch.activated = true;
    };

    sketch.update = (data) => {
        if(data["right_hand_sign"] != undefined){
            sketch.pikachu_model.sign = data["right_hand_sign"]
        }
    }


    sketch.show = () => {
        sketch.clear();
        sketch.pikachu_model.show();
        sketch.pikachu_model.update(sketch.cursor[0], sketch.cursor[1], sketch.cursor[2]);
    };


    class Model {
        constructor(x, y, s, m) {
            this.x = x;
            this.y = y;
            this.s = s;
            this.model = m;
            this.sign = ["", 0]
        }
        show() {
            if(this.sign[0] == "INDEX" && this.sign[1] > 0.6){
                sketch.push();
                sketch.translate(this.x - width/2, this.y - height/2, 0);
                sketch.rotateZ(PI);
                sketch.rotateY(0.01* frameCount);
                sketch.fill(255);
                sketch.scale(this.s);
                sketch.normalMaterial();
                sketch.model(this.model);
                sketch.pop();
            }
        }
        update(x, y, s) {
            this.x = x;
            this.y = y;
            this.s = s;
        }
    }
}
