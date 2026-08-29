import type { ReactNode } from "react";

/** Every section carries a line reference in the gutter. The numbering is not
 *  decoration: this is a page about citing lines, so the page is citable. */
export function Row({
  id,
  line,
  label,
  children,
  className = "",
}: {
  id?: string;
  line: string;
  label?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section id={id} className={`border-b border-rule ${className}`}>
      <div className="mx-auto grid max-w-[1240px] grid-cols-1 gap-y-6 px-6 py-16 md:grid-cols-[92px_1fr] md:gap-x-8 md:px-10 md:py-24">
        <div className="md:sticky md:top-24 md:self-start">
          <p className="gutter">{line}</p>
          {label ? (
            <p className="gutter mt-1.5 text-signal uppercase">{label}</p>
          ) : null}
        </div>
        <div className="min-w-0">{children}</div>
      </div>
    </section>
  );
}

export function Heading({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <h2 className={`display max-w-[20ch] text-[2rem] sm:text-[2.6rem] ${className}`}>
      {children}
    </h2>
  );
}

export function Lede({ children }: { children: ReactNode }) {
  return (
    <p className="mt-5 max-w-[62ch] text-[16.5px] leading-[1.65] text-ink-2">{children}</p>
  );
}

export function Verdict({ value }: { value: string }) {
  const bad = value === "diverged";
  return (
    <span
      className={`inline-flex items-center gap-2 font-mono text-[11px] tracking-[0.06em] ${
        bad ? "text-signal" : "text-good"
      }`}
    >
      <span
        aria-hidden
        className={`h-[8px] w-[8px] ${bad ? "bg-signal" : "bg-good"}`}
        style={{ borderRadius: 1 }}
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
      ? "bg-ink text-paper hover:bg-[#2A2C31]"
      : "border border-rule text-ink hover:border-ink-3";
  return (
    <a
      href={href}
      className={`inline-flex items-center gap-2 px-5 py-2.5 text-[14.5px] font-medium transition ${styles}`}
      style={{ borderRadius: 2 }}
    >
      {children}
    </a>
  );
}

/** Terminal output, used as a real object on the page rather than an image. */
export function Terminal({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="overflow-hidden bg-terminal" style={{ borderRadius: 3 }}>
      <div className="flex items-center gap-2 border-b border-white/8 px-4 py-2.5">
        <span className="font-mono text-[10.5px] tracking-[0.12em] text-white/35 uppercase">
          {title}
        </span>
      </div>
      <pre className="overflow-x-auto px-5 py-5 font-mono text-[12.5px] leading-[1.75] text-[#D4DAE3]">
        {children}
      </pre>
    </div>
  );
}
