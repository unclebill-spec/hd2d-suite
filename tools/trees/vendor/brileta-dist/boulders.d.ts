import { Canvas } from './types.js';
export declare enum BoulderArchetype {
    ROUNDED = "rounded",
    TALL = "tall",
    FLAT = "flat",
    BLOCKY = "blocky"
}
export declare function generateBoulder(seed: number, size?: number): {
    canvas: Canvas;
    archetype: BoulderArchetype;
};
