import type { ReactNode } from "react";

export function Section({
  id,
  children,
  className = "",
}: {
  id?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section id={id} className={`px-6 py-20 sm:px-12 md:px-16 ${className}`}>
      {children}
    </section>
  );
}

export function Eyebrow({ children }: { children: ReactNode }) {
  return <p className="eyebrow mb-5">{children}</p>;
}

/** Display heading: a dark statement, then a grey continuation that carries
 *  the rest of the thought without shouting it. */
export function Display({
  lead,
  rest,
  className = "",
}: {
  lead: ReactNode;
  rest?: ReactNode;
  className?: string;
}) {
  return (
    <h2
      className={`font-serif text-[2rem] leading-[1.15] tracking-[-0.02em] text-balance sm:text-[2.6rem] ${className}`}
    >
      <span className="text-ink">{lead}</span>
      {rest ? <span className="text-ink-3"> {rest}</span> : null}
    </h2>
  );
}

export function Verdict({ value }: { value: string }) {
  const bad = value === "diverged";
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-2.5 py-1 font-mono text-[10px] tracking-[0.1em] uppercase ${
        bad ? "bg-bad-soft text-bad" : "bg-good-soft text-good"
      }`}
    >
      <span
        aria-hidden
        className={`h-[7px] w-[7px] rounded-full ${bad ? "bg-bad" : "bg-good"}`}
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
  const base =
    "inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-[15px] font-medium transition";
  const styles =
    variant === "solid"
      ? "bg-accent text-white hover:brightness-110"
      : "bg-[#F1F3F6] text-ink hover:bg-[#E8EBF0]";
  return (
    <a href={href} className={`${base} ${styles}`}>
      {children}
    </a>
  );
}
