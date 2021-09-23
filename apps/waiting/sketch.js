let img;

function preload() {

}

function setup() {
    fullscreen();
    createCanvas(windowWidth, windowHeight);
    stroke(255);
    fill(255);
    textSize(32);
    img = createImg('https://cdn-icons-png.flaticon.com/512/497/497738.png');
    img.hide();
    
    setTimeout(() => {
        resizeCanvas(windowWidth, windowHeight);
    }, 1000);
}

let angle = 0;

function draw() {
    background(0, 40);
    push();
    translate(width / 2, height / 2 - 100);
    rotate(angle);
    ellipse(80, 80, 20, 20);
    rotate(0.03);
    ellipse(80, 80, 20, 20);
    rotate(0.03);
    ellipse(80, 80, 20, 20);
    pop();
    // stroke(255); // Change the color
    // strokeWeight(20);
    angle += 0.1;

    textAlign(CENTER);
    text('Work in progress\nTravaux en cours\nTrabajo en progreso\nIn Arbeit\n진행중인 작업 ', width / 2, height / 2 + 100);
    push();
    translate(150, 150);
    rotate(angle / 8);
    image(img, -75, -75, 150, 150);
    pop();

    push();
    translate(width - 150, 150);
    rotate(angle / 8);
    image(img, -75, -75, 150, 150);
    pop();

    push();
    translate(150, height - 150);
    rotate(angle / 8);
    image(img, -75, -75, 150, 150);
    pop();

    push();
    translate(width - 150, height - 150);
    rotate(angle / 8);
    image(img, -75, -75, 150, 150);
    pop();
}