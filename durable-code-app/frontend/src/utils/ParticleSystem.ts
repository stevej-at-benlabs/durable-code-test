export interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  color: string;
  opacity: number;
}

export class ParticleFactory {
  private colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b'];
  private maxRadius = 3;

  createParticle(canvas: HTMLCanvasElement): Particle {
    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      radius: Math.random() * this.maxRadius + 1,
      color: this.colors[Math.floor(Math.random() * this.colors.length)],
      opacity: Math.random() * 0.5 + 0.2,
    };
  }
}

export class ParticlePhysics {
  updateParticle(particle: Particle, canvas: HTMLCanvasElement): void {
    // Update position
    particle.x += particle.vx;
    particle.y += particle.vy;

    // Bounce off walls
    if (particle.x < 0 || particle.x > canvas.width) {
      particle.vx = -particle.vx;
    }
    if (particle.y < 0 || particle.y > canvas.height) {
      particle.vy = -particle.vy;
    }

    // Apply friction
    particle.vx *= 0.99;
    particle.vy *= 0.99;
  }

  applyMouseInteraction(
    particle: Particle,
    mouseX: number,
    mouseY: number,
    isMouseMoving: boolean,
  ): void {
    if (!isMouseMoving) return;

    const dx = mouseX - particle.x;
    const dy = mouseY - particle.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < 100) {
      const force = (100 - distance) / 100;
      particle.vx -= (dx / distance) * force * 0.02;
      particle.vy -= (dy / distance) * force * 0.02;
    }
  }
}

export class ParticleRenderer {
  private connectionDistance = 150;

  drawParticle(ctx: CanvasRenderingContext2D, particle: Particle): void {
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
    ctx.fillStyle = particle.color;
    ctx.globalAlpha = particle.opacity;
    ctx.fill();
  }

  drawConnections(ctx: CanvasRenderingContext2D, particles: Particle[]): void {
    for (let i = 0; i < particles.length; i++) {
      const particle = particles[i];
      for (let j = i + 1; j < particles.length; j++) {
        const other = particles[j];
        const dx = particle.x - other.x;
        const dy = particle.y - other.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < this.connectionDistance) {
          ctx.beginPath();
          ctx.moveTo(particle.x, particle.y);
          ctx.lineTo(other.x, other.y);
          ctx.strokeStyle = particle.color;
          ctx.globalAlpha = (1 - distance / this.connectionDistance) * 0.2;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }
}

export class MouseTracker {
  private mouseX = 0;
  private mouseY = 0;
  private isMouseMoving = false;

  constructor() {
    this.handleMouseMove = this.handleMouseMove.bind(this);
  }

  private handleMouseMove = (e: MouseEvent) => {
    this.mouseX = e.clientX;
    this.mouseY = e.clientY;
    this.isMouseMoving = true;
    setTimeout(() => {
      this.isMouseMoving = false;
    }, 100);
  };

  startTracking(): void {
    window.addEventListener('mousemove', this.handleMouseMove);
  }

  stopTracking(): void {
    window.removeEventListener('mousemove', this.handleMouseMove);
  }

  getMousePosition(): { x: number; y: number; isMoving: boolean } {
    return {
      x: this.mouseX,
      y: this.mouseY,
      isMoving: this.isMouseMoving,
    };
  }
}
