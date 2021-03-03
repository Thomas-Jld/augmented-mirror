let Hands = (sketch) => {

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

        sketch.right_hand = new Hand("get_right_hand");
        sketch.left_hand = new Hand("get_left_hand");

        socket.on("send_right_hand", function (data) {
            sketch.right_hand.hand_pose = data;
        });


        socket.on("send_left_hand", function (data) {
            sketch.left_hand.hand_pose = data;
        });

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
            this.hand_pose_t = []; //After projection 
            this.name = name;

            setInterval(this.get_update, 40);
        }

        get_update() {
            socket.emit(this.name, true);
        }
 
        show() {
            if (this.hand_pose == []) {
                return
            }
            sketch.fill(200);
            
            this.hand_pose.forEach(function(part){

                if(part.slice(2,4) != [-1,-1]){
                    let x = width / 2 - width * (part[2] - xoffset) / screenwidth;
                    let y = height * (part[3] - yoffset) / screenheight;

                    hand_pose_t.push([x, y]);

                    if (sketch.show_particules) {
                        if (frameCount % 5 == 0) {
                            particules.push(new Particule(x, y));
                        }
                    }

                    if (sketch.show_hands_points) {
                        sketch.ellipse(x, y, 30);
                        //sketch.text(part, x + 20, y + 20);
                    }
                }
                else{
                    this.hand_pose_t.push([0, 0]);
                }

            });

            if (sketch.show_hands_lines) {
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
                        console.log(e);
                    }
                })
            });
        }
    }
}