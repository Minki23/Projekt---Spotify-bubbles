class Button{
  constructor(button){
    this.button = button;
    this.button.style.width = `${Math.floor(Math.random() * 100) + 50}px`;
    this.gravityX = 0.0015*parseInt(this.button.style.width);
    this.gravityY = 0.001*parseInt(this.button.style.width);
    this.friction = .06;
    this.repelForce = 0.008*parseInt(this.button.style.width);
    this.velocityX = 0;
    this.velocityY = 0;
    this.collidedX = false;
    this.collidedY = false;
  }
  reset(){
    this.gravityX = 0.0015*parseInt(this.button.style.width);
    this.gravityY = 0.001*parseInt(this.button.style.width);
    this.friction = .06;
    this.repelForce = 0.01*parseInt(this.button.style.width);
    this.velocityX = 0;
    this.velocityY = 0;
    this.collidedX = false;
    this.collidedY = false;
  }
  move(){
    setInterval(() => {
      this.button.style.top = `${parseFloat(this.button.style.top) + this.velocityY}px`;
      this.button.style.left = `${parseFloat(this.button.style.left) + this.velocityX}px`;
      const cube =  document.querySelector('.cube').getBoundingClientRect();
      squareCenterY = cube.top + cube.height / 2;
      squareCenterX = cube.left + cube.width / 2;
      
      if (parseFloat(this.button.style.top) + this.button.offsetHeight >= squareCenterY) {
        this.velocityY -= this.gravityY;
      } else {
        this.velocityY += this.gravityY;
      }
      
      if (parseFloat(this.button.style.left) + this.button.offsetWidth >= squareCenterX) {
        this.velocityX -= this.gravityX;
      } else {
        this.velocityX += this.gravityX;
      }
      
      this.velocityX *= 1 - this.friction;
      this.velocityY *= 1 - this.friction;
      
      this.collided = false;
        buttons.forEach((otherButton) => {
        if (otherButton !== this.button) {
          const buttonRect = this.button.getBoundingClientRect();
          const otherButtonRect = otherButton.getBoundingClientRect();
          const buttonCenterX = buttonRect.left + buttonRect.width / 2;
          const buttonCenterY = buttonRect.top + buttonRect.height / 2;
          const otherButtonCenterX = otherButtonRect.left + otherButtonRect.width / 2;
          const otherButtonCenterY = otherButtonRect.top + otherButtonRect.height / 2;
          const distance = Math.sqrt(Math.pow(buttonCenterX - otherButtonCenterX, 2) + Math.pow(buttonCenterY - otherButtonCenterY, 2));
          const collisionDistance = (buttonRect.width + otherButtonRect.width) / 2; // Assuming buttons have the same radius
          
          if (distance < collisionDistance) {    
          const dx = buttonCenterX - otherButtonCenterX;
          const dy = buttonCenterY - otherButtonCenterY;
          const angle = Math.atan2(dy, dx);
          
          const repelX = Math.cos(angle) * this.repelForce;
          const repelY = Math.sin(angle) * this.repelForce;
          
          this.velocityX += repelX;
          this.velocityY += repelY;
          }
        }
        });
    }, 1);
  }
}
let stop = false;
const buttons = document.querySelectorAll('button');
console.log(buttons)
window.addEventListener('DOMContentLoaded', () => {
  buttons.forEach((button) => {
    const randomX = Math.random() * (window.innerWidth);
    const randomY = Math.random() * (window.innerHeight);
    button.style.left = `${randomX}px`;
    button.style.top = `${randomY}px`;
    squareCenterX = window.innerWidth / 2;
    squareCenterY = window.innerHeight / 2;
  });
});
let before = false;
buttons.forEach((button) => {
  const newButton = new Button(button);
  newButton.move();
  newButton.button.addEventListener('mousedown', (event) => {
    const initialX = event.clientX;
    const initialY = event.clientY;
    const buttonRect = button.getBoundingClientRect();
    const offsetX = initialX - buttonRect.left;
    const offsetY = initialY - buttonRect.top;

    const handleMouseMove = (event) => {
      const newX = event.clientX - offsetX;
      const newY = event.clientY - offsetY;
      button.style.left = `${newX}px`;
      button.style.top = `${newY}px`;
      newButton.velocityX = 0;
      newButton.velocityY = 0;
      newButton.gravityX = 0;
      newButton.gravityY = 0;
      newButton.repelForce = 0;
    };

    const handleMouseUp = () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      newButton.reset();
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  });
  console.log("aaaa")
});