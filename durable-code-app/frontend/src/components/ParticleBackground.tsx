/**
 * Purpose: React component providing an animated particle background effect with canvas rendering
 * Scope: Full-screen animated background overlay with interactive particle system
 * Overview: Creates a fixed-position canvas that renders animated particles with physics simulation,
 *     mouse interaction, and connecting lines between nearby particles. Provides an immersive
 *     background effect for the application with configurable particle behavior through dependency
 *     injection. Handles canvas resizing, animation loops, and proper cleanup of event listeners.
 *     Optimized for performance with requestAnimationFrame and includes test environment safety.
 * Dependencies: React hooks (useEffect, useRef), ParticleSystem utilities (ParticleFactory, ParticlePhysics, ParticleRenderer, MouseTracker), HTML5 Canvas API
 * Exports: ParticleBackground component as default export
 * Props/Interfaces: ParticleBackgroundProps with optional dependency injection for particle system components
 * State/Behavior: Manages canvas ref, handles window resize events, runs continuous animation loop, tracks mouse interactions for particle repulsion effects
 */
import { useEffect, useRef } from 'react';
import type { Particle } from '../utils/ParticleSystem';
import {
  MouseTracker,
  ParticleFactory,
  ParticlePhysics,
  ParticleRenderer,
} from '../utils/ParticleSystem';

interface ParticleBackgroundProps {
  particleFactory?: ParticleFactory;
  physics?: ParticlePhysics;
  renderer?: ParticleRenderer;
  mouseTracker?: MouseTracker;
}

const ParticleBackground = ({
  particleFactory = new ParticleFactory(),
  physics = new ParticlePhysics(),
  renderer = new ParticleRenderer(),
  mouseTracker = new MouseTracker(),
}: ParticleBackgroundProps = {}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Skip canvas operations in test environment
    if (
      typeof window === 'undefined' ||
      (typeof process !== 'undefined' && process.env.NODE_ENV === 'test')
    )
      return;

    let ctx: CanvasRenderingContext2D | null = null;
    try {
      ctx = canvas.getContext('2d');
    } catch {
      // Canvas not supported in test environment
      return;
    }
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

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
  }, [particleFactory, physics, renderer, mouseTracker]);

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
