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

export default function Home() {
  return (
    <main className="sheet mx-auto min-h-screen max-w-[1180px]">
      <Nav repo={study.repo} />
      <Hero repo={study.repo} diverged={study.diverged} runs={study.runs} />
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
