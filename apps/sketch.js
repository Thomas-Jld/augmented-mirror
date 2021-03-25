let modules = [];
let objectsSelected = false;

let pose;
let hands;
let face;
let selector;
let clock;
let pikachu;

let socket;
let canvas;

let started = false;

let xoffset = -235; // millimeters
let yoffset = 50;

let screenwidth = 392.85; //millimeters
let screenheight = 698.4;

function setup() {
    canvas = createCanvas(windowWidth, windowHeight);

    socket = io.connect('http://0.0.0.0:5000');

    frameRate(30);

    setTimeout(reshape, 1000);
}

function draw() {
    background(0);
    if (started) {
        modules.forEach(m => {
            if (m.activated) {
                m.show();
                // if (m.latched) {
                //     m.setPosition(mouseX - m.OffsetX, mouseY - m.OffsetY);
                // }
            }
        });
        selection();
        // selector.cursor = [mouseX, mouseY];
        // selector.mx = 200;
        // selector.my = height/2;
    }
}

function selection(){
    if (hands.left_hand.hand_pose_t[8] !== undefined && hands.left_hand.hand_pose_t[5] !== undefined && hands.right_hand.hand_pose_t[8] !== undefined) {
        if (hands.left_hand.hand_pose_t[8][0] - hands.left_hand.hand_pose_t[5][0] > 80){
            selector.display_bubbles = true;
        }
        else{
            selector.display_bubbles = false;
        }
        selector.mx = hands.left_hand.hand_pose_t[8][0];
        selector.my = hands.left_hand.hand_pose_t[8][1];
        selector.cursor = hands.right_hand.hand_pose_t[8];
        pikachu.cursor = hands.right_hand.hand_pose_t[8] + [1];
    }
}

function reshape() {
    resizeCanvas(windowWidth, windowHeight);

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

    pikachu = new p5(Pikachu);
    pikachu.set(0, 0, width, height);
    modules.push(pikachu);

    started = true;
}

function choseAction(opt, action){
    if (opt == "Show Clock"){
        if(action){
            clock.activated = true;
            clock.selfCanvas.show();
        }
        else{
            clock.activated = false;
            clock.selfCanvas.hide();
        }
    }
    else if (opt == "Show Face"){
        if(action){
            face.activated = true;
            face.selfCanvas.show();
        }
        else{
            face.activated = false;
            face.selfCanvas.hide();
        }
    }
    else if (opt == "Show Pose"){
        if(action){
            pose.activated = true;
            pose.selfCanvas.show();
        }
        else{
            pose.activated = false;
            pose.selfCanvas.hide();
        }
    }
    else if (opt == "Show Hands"){
        if(action){
            hands.selfCanvas.show();
        }
        else{
            hands.selfCanvas.hide();
        }
    }
}

function keyPressed() {
    if (key == "c") {
        modules.forEach(m => {
            m.clearSketch();
        });
    }

    if (key == "p") {
        modules.forEach(m => {
            m.activated = false;
            m.selfCanvas.hide();
        });
        pose.activated = true;
        pose.selfCanvas.show();
    }

    if (key == "h") {
        modules.forEach(m => {
            m.activated = false;
            m.selfCanvas.hide();
        });
        hands.activated = true;
        hands.selfCanvas.show();
    }

    if (key == "f") {
        modules.forEach(m => {
            m.activated = false;
            m.selfCanvas.hide();
        });
        face.activated = true;
        face.selfCanvas.show();
    }

    if (key == "b") {
        modules.forEach(m => {
            m.activated = false;
            m.selfCanvas.hide();
        });
        pose.activated = true;
        pose.selfCanvas.show();
        hands.activated = true;
        hands.selfCanvas.show();
    }

    if (key == "s") {
        modules.forEach(m => {
            m.activated = false;
            m.selfCanvas.hide();
        });
        hands.activated = true;
        selector.activated = true;
        selector.selfCanvas.show();
    }

    if (key == "a") {
        modules.forEach(m => {
            m.activated = true;
            m.selfCanvas.show();
        });
    }
}

// function mousePressed(){
//     selector.display_bubbles = !selector.display_bubbles;
// }

// function mousePressed() {
//     let selected = false;
//     let objectSelected = false;
//     modules.forEach(m => {
//         if (m.movable && mouseX > m.x && mouseY > m.y && mouseX < m.x + m.width && mouseY < m.y + m.height) {
//             selected = true;
//             if (!objectsSelected) {
//                 m.latched = true;
//                 objectSelected = true;
//                 m.OffsetX = mouseX - m.x;
//                 m.OffsetY = mouseY - m.y;
//             } else {
//                 m.latched = false;
//             }
//         }
//     });

//     objectsSelected = objectSelected;

//     if (!selected) {
//         modules.forEach(m => {
//             if (!m.movable && m.clickable) {
//                 m.onClicked(mouseX, mouseY);
//             }
//         });
//     }
// }
