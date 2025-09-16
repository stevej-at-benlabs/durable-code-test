/**
 * Read-only interface for link registry consumers
 */
export interface ReadableLinkRegistry {
  getLinks(): string[];
}

/**
 * Mutation interface for link registry managers
 */
export interface ModifiableLinkRegistry extends ReadableLinkRegistry {
  addLink(link: string): void;
  removeLink(link: string): void;
}

/**
 * Full interface for backward compatibility
 */
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface LinkRegistry extends ModifiableLinkRegistry {}
