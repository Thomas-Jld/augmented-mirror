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

        sketch.dance = new DanceLesson("dance02");

        sketch.colorMode(HSB);
    };

    sketch.update = (global_data) => {
        if (global_data != undefined && "body_pose_t" in global_data) {
            sketch.dance.body_pose = global_data["body_pose_t"]; // In pixels
            sketch.dance.update();
        }
    }

    sketch.show = () => {
        sketch.selfCanvas.clear();
        sketch.dance.show();
    }

    class DanceLesson {
        constructor(file_name) {
            this.body_pose = [];

            this.init = false;
            this.offset = [0, 0];
            this.ratio = 1;
            this.size = [];

            this.video = sketch.loadImage("components/videos/" + file_name + ".gif");
            this.video.pause();
            this.video_index = 0;

            this.moves = sketch.loadJSON(
                "components/movements/" + file_name + ".json",// Structure : moves["index"] = [[kpts_index, x, y], ...]
                (moves) => {
                    sketch.dance.size = moves["size"]; // Original video size
                }); 
            this.moves_index = 0;

            this.diff = 0; // The lower, the closer the moves are
            this.limit = 400; // if this.diff < this.limit, it goes on
        }

        show() {
            if (this.init && this.moves_index > this.video_index) {
                this.video_index++;
            }
            this.video.pause();
            this.video.setFrame(this.video_index);
            sketch.image(
                this.video, 
                this.offset[0], 
                this.offset[1],
                this.size[0],
                this.size[1]
                );

            sketch.stroke(255);
            sketch.fill(255);
            sketch.strokeWeight(2);
            sketch.textSize(30);
            sketch.text(
                Math.floor(this.diff), 
                20,
                80
            );
        }

        update() {
            if (this.body_pose.length > 0) {
                if (!this.init) {
                    this.init = true;

                    let mirror_nose_reference = this.body_pose[0]; // Current nose postion of the user
                    let mirror_left_hip_reference = this.body_pose[24]; // Current left hip postion of the user
                    let video_nose_reference = this.moves[Object.keys(this.moves)[0]][0].slice(1, 3); // Position in pixels of the first nose of this.moves
                    let video_left_hip_reference = this.moves[Object.keys(this.moves)[0]][23].slice(1, 3); // Position in pixels of the first left_hip of this.moves

                    let mirror_distance = sketch.dist(
                        mirror_nose_reference[0],
                        mirror_nose_reference[1],
                        mirror_left_hip_reference[0],
                        mirror_left_hip_reference[1]
                    );

                    let video_distance = sketch.dist(
                        video_nose_reference[0],
                        video_nose_reference[1],
                        video_left_hip_reference[0],
                        video_left_hip_reference[1]
                    );

                    this.ratio = mirror_distance / video_distance;
                    this.size = [
                        this.size[0] * this.ratio, 
                        this.size[1] * this.ratio
                    ];

                    this.offset = [
                        mirror_nose_reference[0] - video_nose_reference[0] * this.ratio,
                        mirror_nose_reference[1] - video_nose_reference[1] * this.ratio
                    ];
                } else {
                    if (this.moves_index in this.moves) {
                        let distances = [];
                        for (let i = 0; i < this.body_pose.length; i++) {
                            distances.push(
                                sketch.dist(
                                    this.moves[this.moves_index][i][1], //Video x
                                    this.moves[this.moves_index][i][2], //Video y
                                    this.body_pose[i][0], //Mirror x 
                                    this.body_pose[i][1], //Mirror y
                                )
                            );
                        }
                        this.diff = distances.reduce((partial_sum, a) => partial_sum + a,0) / distances.length; //Mean of kpts differences
                        if (this.diff < this.limit){
                            this.moves_index++;
                        }
                    } else {
                        this.moves_index++;
                    }
                }
            }
        }
    }
}