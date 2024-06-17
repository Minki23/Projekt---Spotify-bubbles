let i = 60;
const cube = document.querySelector('.cube').getBoundingClientRect();

class Button {
  constructor(button) {
    this.button = button;
    this.size = `${i / 10}vw`; // Ustaw rozmiar jako jednostka vw (viewport width)
    this.button.style.width = this.size;
    this.button.style.height = this.size; // Dodaj tę linię, aby ustawić wysokość
    i -= 1.5;
    this.reset();
  }

  reset() {
    this.gravity = 0.1;
    this.friction = 0.1;
    this.repelForce = 1.0;

    this.velocityX = 0;
    this.velocityY = 0;
  }

  move() {
    setInterval(() => {
      this.button.style.top = `${parseFloat(this.button.style.top) + this.velocityY}px`;
      this.button.style.left = `${parseFloat(this.button.style.left) + this.velocityX}px`;
      const squareCenterY = cube.height / 2;
      const squareCenterX = cube.width / 2;

      if (parseFloat(this.button.style.top) + this.button.offsetHeight / 2 > squareCenterY) {
        this.velocityY -= this.gravity;
      } else {
        this.velocityY += this.gravity;
      }

      if (parseFloat(this.button.style.left) + this.button.offsetWidth / 2 > squareCenterX) {
        this.velocityX -= this.gravity;
      } else {
        this.velocityX += this.gravity;
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
          const collisionDistance = (buttonRect.width + otherButtonRect.width) / 2;

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

const buttons = document.querySelectorAll('button');
buttons.forEach((button) => {
  button.style.top = `${Math.random() * (cube.height - button.offsetHeight)}px`;
  button.style.left = `${Math.random() * (cube.width - button.offsetWidth)}px`;
  const newButton = new Button(button);
  newButton.move();
  newButton.button.addEventListener('mousedown', (event) => {
    const buttonRect = button.getBoundingClientRect();
    const offsetX = event.clientX - buttonRect.left;
    const offsetY = event.clientY - buttonRect.top;

    const handleMouseMove = (event) => {
      button.style.left = `${event.clientX - offsetX}px`;
      button.style.top = `${event.clientY - offsetY}px`;
      newButton.velocityX = 0;
      newButton.velocityY = 0;
      newButton.gravity = 0;
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
});
