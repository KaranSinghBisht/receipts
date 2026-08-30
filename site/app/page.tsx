import { existsSync } from "node:fs";
import { join } from "node:path";

import study from "@/lib/study.json";
import { Evidence } from "@/components/Evidence";
import { Footer } from "@/components/Footer";
import { Hero } from "@/components/Hero";
import { Nav } from "@/components/Nav";
import { Pillars } from "@/components/Pillars";
import { Problem } from "@/components/Problem";
import { Reflexive } from "@/components/Reflexive";
import { Study } from "@/components/Study";
import { WorksWith } from "@/components/WorksWith";
import { Breaker } from "@/components/ui";

/** Use a supplied hero backdrop if one has been dropped into public/. */
function heroArt(): string | null {
  for (const name of ["hero-bg.jpg", "hero-bg.png", "hero-bg.webp"]) {
    if (existsSync(join(process.cwd(), "public", name))) return `/${name}`;
  }
  return null;
}

export default function Home() {
  const art = heroArt();
  return (
    <main className="min-h-screen overflow-x-clip">
      <Nav repo={study.repo} />
      <Hero repo={study.repo} diverged={study.diverged} runs={study.runs} art={art} />
      <WorksWith />
      <Problem />
      <Breaker />
      <Pillars />
      <Evidence />
      <Study />
      <Breaker />
      <Reflexive />
      <Footer repo={study.repo} />
    </main>
  );
}
