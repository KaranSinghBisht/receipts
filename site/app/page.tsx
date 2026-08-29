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
    <main className="sheet mx-auto min-h-screen max-w-[1180px]">
      <Nav repo={study.repo} />
      <Hero repo={study.repo} diverged={study.diverged} runs={study.runs} art={art} />
      <WorksWith />
      <Problem />
      <Pillars />
      <Evidence />
      <Study />
      <Reflexive />
      <Footer repo={study.repo} />
    </main>
  );
}
