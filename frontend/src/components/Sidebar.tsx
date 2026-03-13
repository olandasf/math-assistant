export * from "./Layout";
// This file is just to satisfy imports if any other file imports Sidebar directly.
// Ideally we should fix imports, but for "rewrite from scratch" speed we redirect.
import { Layout } from "./Layout";
export { Layout as Sidebar }; // Mock export
