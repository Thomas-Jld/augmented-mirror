let Hands = (sketch) => {
    sketch.name = "hands";

    // let xmul = 0.16
    // let ymul = -0.15

    let particules = [];

    sketch.movable = false;
    sketch.latched = false;
    sketch.activated = false;
    sketch.clickable = false;
    sketch.to_update = true;

    sketch.show_particules = false;
    sketch.show_hands_points = true;
    sketch.show_hands_lines = true;

    sketch.right_hand_data = [];
    sketch.left_hand_data = [];

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);
        // sketch.selfCanvas.hide();

        sketch.right_hand = new Hand("get_right_hand");
        sketch.left_hand = new Hand("get_left_hand");

        sketch.colorMode(HSB);
        sketch.activated = true;
    };

    sketch.update = (data) => {
        if(data["right_hand_pose"] != undefined){
            sketch.right_hand_data = data["right_hand_pose"]
        }
        if(data["left_hand_pose"] != undefined){
            sketch.left_hand_data = data["left_hand_pose"]
        }
    }

    sketch.show = () => {
        sketch.selfCanvas.clear();

        sketch.right_hand.update(sketch.right_hand_data);
        sketch.right_hand.show();

        sketch.left_hand.update(sketch.left_hand_data);
        sketch.left_hand.show();

        if (sketch.show_particules) {
            particules.forEach(particule => {
                particule.show();
                particule.update();
            });
        }
    }

    class Hand {
        constructor(hand_name) {
            this.junctions = [
                [
                    [0, 1],
                    [0, 5],
                    [0, 9],
                    [0, 13],
                    [0, 17],
                    [5, 9],
                    [9, 13],
                    [13, 17]
                ],
                [
                    [1, 2],
                    [2, 3],
                    [3, 4]
                ],
                [
                    [5, 6],
                    [6, 7],
                    [7, 8]
                ],
                [
                    [9, 10],
                    [10, 11],
                    [11, 12]
                ],
                [
                    [13, 14],
                    [14, 15],
                    [15, 16]
                ],
                [
                    [17, 18],
                    [18, 19],
                    [19, 20]
                ]
            ];

            this.keypoints = [
                0, 1, 2, 3, 4, 5,
                6, 7, 8, 9, 10, 11,
                12, 13, 14, 15, 16,
                17, 18, 19, 20
            ];

            this.hand_pose = [];
            this.hand_pose_t = []; //After projection
            this.hand_name = hand_name;
        }

        show() {
            if (this.hand_pose == []) {
                return
            }
            sketch.fill(200);

            for(let i = 0; i < this.hand_pose.length; i++){
                if (this.hand_pose[i] != [-1, -1]) {
                    let x;
                    let y;
                    let newx;
                    let newy;
                    if (this.hand_pose_t.length == this.hand_pose.length){
                        newx = width * (this.hand_pose[i][0] - xoffset) / screenwidth;
                        newy = height * (this.hand_pose[i][1] - yoffset) / screenheight;
                        if(newy > 0 || this.hand_pose_t[i][1] < 0){
                            x = lerp(this.hand_pose_t[i][0], newx, 0.8);
                            y = lerp(this.hand_pose_t[i][1], newy, 0.8);
                        }
                        else{ // Assume it's an artifact and slows the update
                            x = lerp(this.hand_pose_t[i][0], newx, 0.01);
                            y = lerp(this.hand_pose_t[i][1], newy, 0.01);
                        }

                        this.hand_pose_t[i] = [x, y];
                    }
                    else{
                        x = width * (this.hand_pose[i][0] - xoffset) / screenwidth;
                        y = height * (this.hand_pose[i][1] - yoffset) / screenheight;

                        this.hand_pose_t.push([x, y]);
                    }

                    if (sketch.show_particules) {
                        if (frameCount % 5 == 0) {
                            particules.push(new Particule(x, y));
                        }
                    }

                    // if (sketch.show_hands_points) {
                    //     sketch.ellipse(x, y, 10);
                    //     //sketch.text(part, x + 20, y + 20);
                    // }
                }
            }

            if (sketch.show_hands_lines && this.hand_pose_t != []) {
                this.show_lines();
            }
        }

        show_lines() {
            sketch.stroke(255);
            sketch.strokeWeight(4);
            this.junctions.forEach(parts => {
                parts.forEach(pair => {
                    try {
                        if (this.hand_pose_t[pair[0]][1] > 0 && this.hand_pose_t[pair[1]][1] > 0) {
                            sketch.line(this.hand_pose_t[pair[0]][0], this.hand_pose_t[pair[0]][1], this.hand_pose_t[pair[1]][0], this.hand_pose_t[pair[1]][1]);
                        }
                    } catch (e) {
                        //console.log(e);
                    }
                })
            });
        }

        update(data) {
            this.hand_pose = data;
            //console.log(data);
        }
    }
}
