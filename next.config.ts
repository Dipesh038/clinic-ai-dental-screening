import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  turbopack: {
    // Pin the workspace root here — otherwise Turbopack picks up an unrelated
    // package-lock.json in the user's home directory as the root.
    root: path.join(__dirname),
  },
};

export default nextConfig;
