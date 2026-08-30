"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

type State = "idle" | "working" | "done" | "error";

function Activate() {
  const params = useSearchParams();
  const router = useRouter();
  const [code, setCode] = useState("");
  const [state, setState] = useState<State>("idle");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fromUrl = params.get("code");
    if (fromUrl) setCode(fromUrl.toUpperCase());
  }, [params]);

  async function approve(event: React.FormEvent) {
    event.preventDefault();
    setState("working");
    setMessage("");
    try {
      const response = await fetch("/api/device/approve", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ user_code: code }),
      });
      const body = await response.json();
      if (!response.ok) {
        setState("error");
        setMessage(
          body.error === "expired"
            ? "That code has expired. Run receipts login again."
            : "No pending device is waiting on that code.",
        );
        return;
      }
      setState("done");
      router.push(`/w/${body.workspace}`);
    } catch {
      setState("error");
      setMessage("Could not reach the server. Check your connection and retry.");
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-[560px] flex-col justify-center px-6 py-20">
      <p className="gutter">device authorisation</p>
      <h1 className="display mt-3 text-[2rem]">Connect this machine</h1>
      <p className="mt-4 text-[15.5px] leading-relaxed text-ink-2">
        Your terminal printed a code. Confirm it matches, and the machine that asked
        will be authorised to push audited runs to a workspace.
      </p>

      <form onSubmit={approve} className="mt-8">
        <label htmlFor="code" className="gutter">
          code from your terminal
        </label>
        <input
          id="code"
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="ABCD-2345"
          autoComplete="off"
          spellCheck={false}
          className="mt-2 w-full border border-rule bg-card px-4 py-3 font-mono text-[18px] tracking-[0.16em] outline-none focus:border-ink"
        />
        <button
          type="submit"
          disabled={code.length < 4 || state === "working"}
          className="mt-4 w-full bg-ink px-5 py-3 text-[15px] font-medium text-white transition disabled:opacity-40"
        >
          {state === "working" ? "Authorising…" : "Authorise this machine"}
        </button>
      </form>

      {message ? (
        <p className="mt-4 border-l-2 border-signal bg-signal-soft px-4 py-3 text-[14px] text-ink-2">
          {message}
        </p>
      ) : null}

      <p className="mt-10 border-t border-rule pt-5 text-[13.5px] leading-relaxed text-ink-3">
        This authorises a machine to write to a workspace. It is not an account and does
        not identify you — there is no identity provider behind it, and saying otherwise
        would be the kind of unchecked claim this tool exists to catch.
      </p>
    </main>
  );
}

export default function Page() {
  return (
    <Suspense fallback={null}>
      <Activate />
    </Suspense>
  );
}
