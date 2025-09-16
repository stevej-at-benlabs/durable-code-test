import { useEffect, useRef } from 'react';
import type { Particle } from '../utils/ParticleSystem';
import {
  ParticleFactory,
  ParticlePhysics,
  ParticleRenderer,
  MouseTracker,
} from '../utils/ParticleSystem';

const ParticleBackground = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Skip canvas operations in test environment
    const ctx = canvas.getContext?.('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize systems
    const particleFactory = new ParticleFactory();
    const physics = new ParticlePhysics();
    const renderer = new ParticleRenderer();
    const mouseTracker = new MouseTracker();

    // Create particles
    const particles: Particle[] = [];
    const particleCount = 50;
    for (let i = 0; i < particleCount; i++) {
      particles.push(particleFactory.createParticle(canvas));
    }

    // Start mouse tracking
    mouseTracker.startTracking();

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const mousePos = mouseTracker.getMousePosition();

      // Update and draw particles
      particles.forEach((particle) => {
        // Update physics
        physics.updateParticle(particle, canvas);
        physics.applyMouseInteraction(
          particle,
          mousePos.x,
          mousePos.y,
          mousePos.isMoving,
        );

        // Render particle
        renderer.drawParticle(ctx, particle);
      });

      // Draw connections between particles
      renderer.drawConnections(ctx, particles);

      ctx.globalAlpha = 1;
      requestAnimationFrame(animate);
    };

    animate();

    // Cleanup
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      mouseTracker.stopTracking();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 1,
        opacity: 0.6,
      }}
    />
  );
};

export default ParticleBackground;
