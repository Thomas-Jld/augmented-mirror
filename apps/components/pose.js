let Pose = (sketch) => {

    let xoffset = 20; // millimeters
    let yoffset = 50;

    let screenwidth = 392.85; //millimeters
    let screenheight = 698.4;

    let junctions = [
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

    let keypoints = ['nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
        'right_eye_inner', 'right_eye', 'right_eye_outer',
        'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
        'left_shoulder', 'right_shoulder', 'left_elbow',
        'right_elbow', 'left_wrist', 'right_wrist', 'left_pinky',
        'right_pinky', 'left_index', 'right_index', 'left_thumb',
        'right_thumb', 'left_hip', 'right_hip', 'left_knee',
        'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
        'left_foot_index', 'right_foot_index'
    ];

    let particules;

    sketch.movable = false;
    sketch.latched = false;
    sketch.activated = true;
    sketch.clickable = false;

    sketch.show_particules = true;
    sketch.show_body_points = true;
    sketch.show_body_lines = true;

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);

        sketch.pose = new Body("pose");
    };


    sketch.show = () => {
        sketch.selfCanvas.clear();
        sketch.pose.show();
    }


    class Body {
        constructor(name) {
            let junctions = [
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

            let keypoints = ['nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
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
            this.name = name;

            setInterval(socket.emit('get_' + this.name, true), 40);

            socket.on('send_' + this.name,
                this.update(data)
            );
        }

        show() {
            if (this.body_pose == []) {
                return
            }
            let transposed = [];
            for (var part in this.body_pose) {
                sketch.fill(200);
                let x = width / 2 - width * (part[2] - xoffset) / screenwidth;
                let y = height * (part[3] - yoffset) / screenheight;

                transposed.push([x, y]);

                if (sketch.show_particules) {
                    if (frameCount % 5 == 0) {
                        particules.push(new Particule(x, y));
                    }
                }

                if (sketch.show_body_points) {
                    sketch.ellipse(x, y, 30);
                    sketch.text(part[1], x + 20, y + 20);
                }

            }

            if (sketch.show_body_lines) {
                this.show_lines(transposed);
            }
        }

        show_lines(transposed) {
            sketch.stroke(255);
            sketch.strokeWeight(4);
            junctions.forEach(parts => {
                parts.forEach(pair => {
                    try {
                        if (transposed[pair[0]][1] > 0 && transposed[pair[1]][1] > 0) {
                            sketch.line(transposed[pair[0]][0], transposed[pair[0]][1], transposed[pair[1]][0], transposed[pair[1]][1]);
                        }
                    } catch (e) {
                        console.log(e);
                    }
                })
            });
        }

        update(data) {
            this.body_pose = data;
        }
    }
}