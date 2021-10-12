let Pose = (sketch) => {
    sketch.name = "pose";

    let particules = [];

    sketch.movable = false;
    sketch.latched = false;
    sketch.activated = false;
    sketch.clickable = false;
    sketch.to_update = true;

    sketch.show_particules = true;
    sketch.show_body_points = true;
    sketch.show_body_lines = true;
    sketch.show_head = false;
    sketch.show_wrist = false;

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);
        // sketch.selfCanvas.hide();

        sketch.pose = new Body("pose");

        sketch.activated = true;
    };

    sketch.update = (data) => {
        if (data["body_pose"] != undefined) {
            sketch.pose.body_pose = data["body_pose"]
        }
    }


    sketch.show = () => {
        sketch.selfCanvas.clear();
        sketch.pose.show();
    }


    class Body {
        constructor(name) {
            this.junctions = [
                [
                    [0, 1],
                    [0, 4],
                    [1, 2],
                    [2, 3],
                    [3, 7],
                    [4, 5],
                    [5, 6],
                    [6, 8]
                ],
                [
                    [9, 10]
                ],
                [
                    [11, 12],
                    [11, 13],
                    [11, 23],
                    [12, 14],
                    [12, 24],
                    [13, 15],
                    [14, 16],
                    [15, 17],
                    [15, 19],
                    [15, 21],
                    [16, 18],
                    [16, 20],
                    [16, 22],
                    [17, 19],
                    [18, 20],
                    [23, 24],
                    [23, 25],
                    [24, 26],
                    [25, 27],
                    [26, 28],
                    [27, 29],
                    [27, 31],
                    [28, 30],
                    [28, 32]
                ]
            ];


            this.keypoints = ['nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
                'right_eye_inner', 'right_eye', 'right_eye_outer',
                'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
                'left_shoulder', 'right_shoulder', 'left_elbow',
                'right_elbow', 'left_wrist', 'right_wrist', 'left_pinky',
                'right_pinky', 'left_index', 'right_index', 'left_thumb',
                'right_thumb', 'left_hip', 'right_hip', 'left_knee',
                'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
                'left_foot_index', 'right_foot_index'
            ];


            this.body_pose = [];
            this.body_pose_t = [];

            this.name = name;

        }

        show() {
            if (this.body_pose == []) {
                return
            }
            sketch.fill(200);

            for (let i = 0; i < this.body_pose.length; i++) {
                if (this.body_pose[i] != [-1, -1]) {
                    let x;
                    let y;
                    let newx;
                    let newy;
                    if (this.body_pose_t.length == this.body_pose.length) {
                        newx = width * (this.body_pose[i][0] - xoffset) / screenwidth;
                        newy = height * (this.body_pose[i][1] - yoffset) / screenheight;
                        if (newy > 0) {
                            x = lerp(this.body_pose_t[i][0], newx, 0.8);
                            y = lerp(this.body_pose_t[i][1], newy, 0.8);
                        } else { // Assume it's an artifact and slows the update
                            x = lerp(this.body_pose_t[i][0], newx, 0.01);
                            y = lerp(this.body_pose_t[i][1], newy, 0.01);
                        }

                        this.body_pose_t[i] = [x, y];
                    } else {
                        x = width * (this.body_pose[i][0] - xoffset) / screenwidth;
                        y = height * (this.body_pose[i][1] - yoffset) / screenheight;

                        this.body_pose_t.push([x, y]);
                    }

                    if (sketch.show_particules) {
                        if (frameCount % 5 == 0) {
                            particules.push(new Particule(x, y));
                        }
                    }

                    // if (sketch.show_body_points && (sketch.show_head || this.body_pose[i][1] > 10) && (sketch.show_wrist || ![17, 18, 19, 20, 21, 22].includes(this.body_pose[i][1]))) {
                    //     //sketch.fill(255);
                    //     sketch.ellipse(x, y, 30);
                    //     //sketch.text(part[1].toString(), x + 20, y + 20);
                    // }
                }
            }
            if (this.body_pose_t.length > 0) {
                global_data["body_pose_t"] = this.body_pose_t;
                let sides_offset = 20;
                let shape_length = 50;
                sketch.stroke(255);
                sketch.strokeWeight(sides_offset);
                sketch.fill(255);
                if (this.body_pose_t[0][0] < -20) {
                    sketch.line(
                        sides_offset + shape_length,
                        height - sides_offset,
                        sides_offset,
                        height - (sides_offset + shape_length)
                        );
                    sketch.line(
                        sides_offset,
                        height - (sides_offset + shape_length),
                        sides_offset + shape_length,
                        height - (sides_offset + 2 * shape_length)
                    );
                }
                if (this.body_pose_t[0][0] > width + 20) {
                    sketch.line(
                        width - (sides_offset + shape_length),
                        height - sides_offset,
                        width - sides_offset,
                        height - (sides_offset + shape_length)
                    );
                    sketch.line(
                        width - sides_offset,
                        height - (sides_offset + shape_length),
                        width - (sides_offset + shape_length),
                        height - (sides_offset + 2 * shape_length)
                    );
                }
            }

            if (sketch.show_body_lines) {
                this.show_lines(this.body_pose_t);
            }
        }

        show_lines(transposed) {
            sketch.stroke(255);
            sketch.strokeWeight(4);
            this.junctions.forEach(parts => {
                parts.forEach(pair => {
                    try {
                        if (transposed[pair[0]][1] > 0 && transposed[pair[1]][1] > 0 &&
                            (sketch.show_head || (pair[1] > 10 && pair[0] > 10)) &&
                            (sketch.show_wrist || (![17, 18, 19, 20].includes(pair[0]) && ![17, 18, 19, 20, 21, 22].includes(pair[1])))
                        ) {
                            sketch.line(transposed[pair[0]][0], transposed[pair[0]][1], transposed[pair[1]][0], transposed[pair[1]][1]);
                        }
                    } catch (e) {
                        //console.log(e);
                    }
                })
            });
        }
    }
}
