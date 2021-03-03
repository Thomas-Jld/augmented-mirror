let Hands = (sketch) => {

    let xoffset = 0; // millimeters
    let yoffset = 100;

    let screenwidth = 392.85; //millimeters
    let screenheight = 698.4;

    let junctions = [
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

    let keypoints = [0, 1, 2, 3, 4, 5,
        6, 7, 8, 9, 10, 11,
        12, 13, 14, 15, 16, 17,
        18, 19, 20
    ];

    // let xmul = 0.16
    // let ymul = -0.15

    let particules = [];

    sketch.movable = false;
    sketch.latched = false;
    sketch.activated = true;
    sketch.clickable = false;

    sketch.show_particules = true;
    sketch.show_hands_points = true;
    sketch.show_hands_lines = true;

    sketch.set = (p1, p2, w, h) => {
        sketch.width = w;
        sketch.height = h;
        sketch.x = p1;
        sketch.y = p2;
        sketch.selfCanvas = sketch.createCanvas(sketch.width, sketch.height).position(sketch.x, sketch.y);

        sketch.right_hand = new Hand("right_hand");
        sketch.left_hand = new Hand("left_hand");

        sketch.colorMode(HSB);
    };


    sketch.show = () => {
        sketch.selfCanvas.clear();

        sketch.right_hand.show();
        sketch.left_hand.show();

        if (sketch.show_particules) {
            particules.forEach(particule => {
                particule.show();
                particule.update();
            });
        }
    }

    class Hand {
        constructor(name) {
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

            this.keypoints = [0, 1, 2, 3, 4, 5,
                6, 7, 8, 9, 10, 11,
                12, 13, 14, 15, 16, 17,
                18, 19, 20
            ];

            this.hand_pose = [];
            this.name = name;

            setInterval(socket.emit('get_' + this.name, true), 40);

            socket.on('send_' + this.name,
                this.update
            );
        }
 
        show() {
            if (this.hand_pose == []) {
                return
            }
            let transposed = [];
            for (var part in this.hand_pose) {
                sketch.fill(200);
                let x = width / 2 - width * (part[2] - xoffset) / screenwidth;
                let y = height * (part[3] - yoffset) / screenheight;

                transposed.push([x, y]);

                if (sketch.show_particules) {
                    if (frameCount % 5 == 0) {
                        particules.push(new Particule(x, y));
                    }
                }

                if (sketch.show_hands_points) {
                    sketch.ellipse(x, y, 30);
                    sketch.text(part, x + 20, y + 20);
                }

            }

            if (sketch.show_hands_lines) {
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
            this.hand_pose = data;
        }
    }
}