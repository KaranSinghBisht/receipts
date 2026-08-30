import { del, get, list, put } from "@vercel/blob";

/**
 * JSON records in a private Blob store.
 *
 * Everything written here is private: the store was created with private
 * access, and reads go through a server-side token that never reaches a
 * browser. Nothing in this file may be imported by a client component.
 */

const ACCESS = "private" as const;

export async function putJson(pathname: string, value: unknown): Promise<void> {
  await put(pathname, JSON.stringify(value), {
    access: ACCESS,
    contentType: "application/json",
    allowOverwrite: true,
    addRandomSuffix: false,
  });
}

export async function getJson<T>(pathname: string): Promise<T | null> {
  try {
    // useCache: false — a device poll has to see an approval that landed a
    // second ago, and a stale read would look like a hung login.
    const result = await get(pathname, { access: ACCESS, useCache: false });
    if (!result?.stream) return null;
    // `blob` on the result is metadata; the body is the stream.
    const text = await new Response(result.stream).text();
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

export async function deleteJson(pathnames: string | string[]): Promise<void> {
  await del(pathnames);
}

/** How many records sit under a prefix, counting no further than `limit`.
 *  Cheaper than listJson: it never fetches the bodies. */
export async function countPrefix(prefix: string, limit = 500): Promise<number> {
  const { blobs } = await list({ prefix, limit });
  return blobs.length;
}

export async function listJson<T>(prefix: string, limit = 200): Promise<T[]> {
  const { blobs } = await list({ prefix, limit });
  const found: T[] = [];
  for (const record of await Promise.all(
    blobs.map((b) => getJson<T>(b.pathname)),
  )) {
    if (record !== null) found.push(record);
  }
  return found;
}
