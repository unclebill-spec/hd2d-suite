/** xoshiro128++ PRNG with SplitMix64 seeding. */
export declare class Rng {
    private s;
    constructor(seed: number);
    /** Return the next uint32 from the xoshiro128++ stream. */
    nextU32(): number;
    /** Uniform float in [0, 1) using the 53-bit mantissa technique. */
    nextFloat(): number;
    /** Uniform float in [min, max). */
    nextRange(min: number, max: number): number;
    /** Uniform integer in [min, max] inclusive. */
    nextInt(min: number, max: number): number;
    /** Deterministic spatial hash for position-keyed seeds. */
    static deriveSpatialSeed(x: number, y: number, mapSeed: number, salt: number): number;
}
