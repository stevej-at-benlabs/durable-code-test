/**
 * Purpose: TypeScript type definitions for the building feature module
 * Scope: Type definitions for development tools, commands, and templates
 * Overview: Centralized type definitions for building-related data structures
 * Dependencies: None
 * Exports: Various building-related type interfaces
 * Interfaces: Command, Capability, Template, HowToGuide, Standard
 * Implementation: Type definitions for building tab functionality
 */

export interface Command {
  id: string;
  icon: string;
  type: string;
  syntax: string;
  description: string;
}

export interface Capability {
  id: string;
  icon: string;
  type: string;
  syntax: string;
  description: string;
}

export interface AiCommand {
  id: string;
  icon: string;
  name: string;
  description: string;
  features: string[];
  modes: Array<{
    syntax: string;
    description: string;
  }>;
}

export interface Template {
  id: string;
  icon: string;
  filename: string;
  description: string;
}

export interface HowToGuide {
  id: string;
  icon: string;
  title: string;
  description: string;
}

export interface Standard {
  id: string;
  icon: string;
  title: string;
  description: string;
}
