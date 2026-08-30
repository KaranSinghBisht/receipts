import type { ReactNode } from "react";

import { Reveal } from "./Reveal";

/** Centred section: pill label, big balanced heading, optional lede.
 *  `tone` sets the band it sits in — alternating tones give the page rhythm. */
export function Section({
  id,
  label,
  title,
  lede,
  children,
  tone = "plain",
  className = "",
}: {
  id?: string;
  label?: string;
  title?: ReactNode;
  lede?: ReactNode;
  children: ReactNode;
  tone?: "plain" | "band" | "dark" | "grid";
  className?: string;
}) {
  const shell =
    tone === "band"
      ? "band"
      : tone === "dark"
        ? "dark-band"
        : tone === "grid"
          ? "gridfield"
          : "";
  return (
    <section id={id} className={`${shell} px-5 py-16 sm:px-8 md:py-24 ${className}`}>
      <div className="mx-auto max-w-[1120px]">
        <Reveal>
          {label ? (
            <div className="flex justify-center">
              <span className="pill-label">{label}</span>
            </div>
          ) : null}
          {title ? (
            <h2 className="display mx-auto mt-5 max-w-[24ch] text-center text-[1.9rem] sm:text-[2.5rem]">
              {title}
            </h2>
          ) : null}
          {lede ? (
            <p className="section-lede mx-auto mt-5 max-w-[62ch] text-center text-[16px] leading-[1.65] text-ink-2">
              {lede}
            </p>
          ) : null}
        </Reveal>
        <Reveal delay={120}>{children}</Reveal>
      </div>
    </section>
  );
}

export function Breaker() {
  return (
    <div aria-hidden className="px-5 sm:px-8">
      <div className="breaker" />
    </div>
  );
}

export function Verdict({ value }: { value: string }) {
  const bad = value.startsWith("diverged");
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-2.5 py-1 font-mono text-[10.5px] tracking-[0.05em] ${
        bad ? "bg-signal-soft text-signal" : "bg-good-soft text-good"
      }`}
    >
      <span
        aria-hidden
        className={`h-[7px] w-[7px] rounded-full ${bad ? "bg-signal" : "bg-good"}`}
      />
      {value}
    </span>
  );
}

export function Button({
  href,
  children,
  variant = "solid",
}: {
  href: string;
  children: ReactNode;
  variant?: "solid" | "quiet";
}) {
  const styles =
    variant === "solid"
      ? "bg-accent text-white shadow-[0_10px_24px_-10px_rgba(15,98,254,0.55)] hover:-translate-y-0.5 hover:brightness-108"
      : "bg-card text-ink border border-rule shadow-[0_2px_10px_rgba(21,23,28,0.05)] hover:-translate-y-0.5 hover:border-ink-3";
  return (
    <a
      href={href}
      className={`inline-flex items-center gap-2 rounded-full px-6 py-3 text-[15px] font-medium transition duration-200 ${styles}`}
    >
      {children}
    </a>
  );
}

export function Terminal({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="overflow-hidden rounded-2xl bg-terminal shadow-[0_18px_50px_-22px_rgba(21,23,28,0.5)]">
      <div className="flex items-center gap-2 border-b border-white/8 px-4 py-2.5">
        <span aria-hidden className="h-[10px] w-[10px] rounded-full bg-[#FF5F57]" />
        <span aria-hidden className="h-[10px] w-[10px] rounded-full bg-[#FEBC2E]" />
        <span aria-hidden className="h-[10px] w-[10px] rounded-full bg-[#28C840]" />
        <span className="ml-2 font-mono text-[10.5px] tracking-[0.12em] text-white/35 uppercase">
          {title}
        </span>
      </div>
      <pre className="overflow-x-auto px-5 py-5 font-mono text-[12.5px] leading-[1.75] text-[#D4DAE3]">
        {children}
      </pre>
    </div>
  );
}
