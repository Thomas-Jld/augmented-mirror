let Dance = (sketch) => {
    sketch.name = "dance";

    sketch.movable = true;
    sketch.latched = false;
    sketch.activated = false;
    sketch.clickable = false;
    sketch.to_update = true;

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);
        // sketch.selfCanvas.hide();

        sketch.dance = new Dance();

        sketch.colorMode(HSB);
        sketch.activated = true;
    };

    sketch.update = (data) => {
        if(data["body_pose"] != undefined){
            sketch.dance.body_pose = data["body_pose"]
        }
    }

    sketch.show = () => {
        sketch.selfCanvas.clear();

        sketch.dance.update("Actual body pose");
    }

    class Dance {
        constructor(path) {
            this.body_pose = [];
        }

        show() {
            
        }

        update(data) {
        }
    }
}
