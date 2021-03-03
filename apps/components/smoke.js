class Particule {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.lifespan = 1;
        this.size = 10 * Math.random();
        this.backspeed = Math.random();
        this.latspeed = (Math.random() - 0.5) / 10;
    }

    show() {
        sketch.stroke(255 * this.lifespan);
        sketch.strokeWeight(this.size);
        sketch.point(this.x, this.y);
    }

    update() {
        this.y -= this.backspeed;
        this.x += this.latspeed;
        this.latspeed += (Math.random() - 0.5) / 10;
        this.lifespan *= 0.97;
        if (this.lifespan < 0.1) {
            particules = particules.slice(1);
        }
    }
}