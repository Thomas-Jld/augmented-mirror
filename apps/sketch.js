let modules = [];
let objectsSelected = false;

let pose;
let hands;
let face;
let selector;
let clock;
// let pikachu;
// let pikachu_model;
let dance;

let socket;
let canvas;

let started = false;

let xoffset = -260; // millimeters
let yoffset = 70;

let screenwidth = 392.85; //millimeters
let screenheight = 698.4;

let global_data = {};
// let available = true;

// function preload(){
//     pikachu_model = loadModel("components/models/pikachu.obj");
// }

function setup() {
    canvas = createCanvas(windowWidth, windowHeight);

    frameRate(40);

    setTimeout(reshape, 1000);

    socket = io.connect('http://0.0.0.0:5000');

    socket.emit("update", true);
    socket.on("global_data", (data) => {
        for (let key in data) {
            global_data[key] = data[key];
          }
    });
}

function draw() {
    background(0);
    if (started) {
        modules.forEach(module => {
            if (module.activated) {
                if(module.to_update && global_data != {}){
                    module.update(global_data);
                }
                module.show();
            }
        });
        selection();
        socket.emit("update", true);
        // if(available){
        //     available = false;
        // }
    }
}

function selection(){
    if (hands.left_hand.hand_pose_t[8] !== undefined &&
        hands.left_hand.hand_pose_t[5] !== undefined &&
        hands.right_hand.hand_pose_t[8] !== undefined) {
        if (
            hands.left_hand.hand_pose_t[8][0] - hands.left_hand.hand_pose_t[5][0] > 80 && (
            dance.dance.init === undefined ||
            !dance.dance.init)
            ){
            selector.display_bubbles = true;
        }
        else{
            selector.display_bubbles = false;
        }
        selector.mx = hands.left_hand.hand_pose_t[8][0];
        selector.my = hands.left_hand.hand_pose_t[8][1];
        selector.cursor = hands.right_hand.hand_pose_t[8];

    }
    // if(hands.right_hand.hand_pose_t[8] != undefined){
    //     pikachu.cursor = hands.right_hand.hand_pose_t[8].copyWithin().concat([100]);
    // }
}

function reshape() {
    resizeCanvas(windowWidth, windowHeight);

    dance = new p5(Dance); // Draw first to not draw the rest over it.
    dance.set(0, 0, width, height);
    modules.push(dance);

    clock = new p5(Clock);
    clock.set(width - 200, 0, 200, 200);
    modules.push(clock);

    // let bubble = new p5(HeartBubble);
    // bubble.set(0, 0, width, height);
    // modules.push(bubble);

    // let multiplications = new p5(Multiplications);
    // multiplications.set(0, 0, 150, 150);
    // modules.push(multiplications);

    pose = new p5(Pose);
    pose.set(0, 0, width, height);
    modules.push(pose);

    hands = new p5(Hands);
    hands.set(0, 0, width, height);
    modules.push(hands);

    face = new p5(Faces);
    face.set(0, 0, width, height);
    modules.push(face);

    selector = new p5(Selector);
    selector.set(0, 0, width, height);
    modules.push(selector);

    // pikachu = new p5(Pikachu);
    // pikachu.set(0, 0, width, height);
    // modules.push(pikachu);

    started = true;
}

function choseAction(opt, action){
    switch (opt){
        case "Show Clock":
            if(action){
                clock.activated = true;
                clock.selfCanvas.show();
            }
            else{
                clock.activated = false;
                clock.selfCanvas.hide();
            }
            break;

        case "Show Face":
            if(action){
                face.activated = true;
                face.selfCanvas.show();
            }
            else{
                face.activated = false;
                face.selfCanvas.hide();
            }
            break;

        case "Show Pose":
            if(action){
                // pose.activated = true;
                pose.show_body_lines = true;
                pose.selfCanvas.show();
            }
            else{
                // pose.activated = false;
                pose.show_body_lines = false;
                pose.selfCanvas.hide();
            }
            break;

        case "Show Hands":
            if (action) hands.selfCanvas.show();
            else hands.selfCanvas.hide();
            break;

        case  "Dance n°1":
            if(action){
                dance.activated = false;
                dance.selfCanvas.clear();
                dance.dance.reset();
            }
            else{
                dance.activated = true;
            }
            break;

        case "Dance n°2":
            if(action){
                // Launch dance
            }
            else{
                // Stop dance
            }
            break;

    }
}

function keyPressed() {
    switch(key){
        case "c":
            modules.forEach(m => {
                m.clearSketch();
            });
            break;

        case "p":
            modules.forEach(m => {
                m.activated = false;
                m.selfCanvas.hide();
            });
            pose.activated = true;
            pose.selfCanvas.show();
            break;

        case "h":
            modules.forEach(m => {
                m.activated = false;
                m.selfCanvas.hide();
            });
            hands.activated = true;
            hands.selfCanvas.show();
            break;

        case "f":
            modules.forEach(m => {
                m.activated = false;
                m.selfCanvas.hide();
            });
            face.activated = true;
            face.selfCanvas.show();
            break;

        case "b":
            modules.forEach(m => {
                m.activated = false;
                m.selfCanvas.hide();
            });
            pose.activated = true;
            pose.selfCanvas.show();
            hands.activated = true;
            hands.selfCanvas.show();
            break;

        case "s":
            modules.forEach(m => {
                m.activated = false;
                m.selfCanvas.hide();
            });
            hands.activated = true;
            selector.activated = true;
            selector.selfCanvas.show();
            break;

        case "a":
            modules.forEach(m => {
                m.activated = true;
                m.selfCanvas.show();
            });
            break;
    }
}
