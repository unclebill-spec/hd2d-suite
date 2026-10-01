import { Canvas } from './types.js';
export declare enum TreeArchetype {
    DECIDUOUS = "deciduous",
    CONIFER = "conifer",
    DEAD = "dead",
    SAPLING = "sapling"
}
interface TreeResult {
    canvas: Canvas;
    archetype: TreeArchetype;
}
export declare function generateTree(seed: number, size?: number, archetype?: TreeArchetype): TreeResult;
export {};
