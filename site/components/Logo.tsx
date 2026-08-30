/** The mark: a receipt with a torn edge, one line flagged. The whole product
 *  in sixty-four squares — a record, and the line the audit points at. */
export function LogoMark({
  size = 26,
  tile = true,
}: {
  size?: number;
  tile?: boolean;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      aria-hidden
      focusable="false"
    >
      {tile ? <rect width="64" height="64" rx="15" fill="#0F62FE" /> : null}
      <path
        d="M19 11h26v37l-4.33-3.6-4.34 3.6-4.33-3.6-4.33 3.6-4.34-3.6L19 48V11z"
        fill="#fff"
      />
      <rect x="25" y="19" width="14" height="3" rx="1.5" fill="#B9C9EE" />
      <rect x="25" y="26" width="14" height="3" rx="1.5" fill="#B9C9EE" />
      <circle cx="26.5" cy="35.5" r="1.9" fill="#C0362C" />
      <rect x="31" y="34" width="8" height="3" rx="1.5" fill="#C0362C" />
    </svg>
  );
}
