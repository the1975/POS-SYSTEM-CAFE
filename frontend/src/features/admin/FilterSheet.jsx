import { useEffect, useState } from "react";

// Lembar filter yang naik dari bawah. groups: [{ key, label, options: [{ value, label }] }].
// values: { [key]: value }. Perubahan baru berlaku setelah tombol Terapkan ditekan.
export default function FilterSheet({ open, title = "Filter", groups, values, onApply, onClose }) {
  const [draft, setDraft] = useState(values);

  useEffect(() => {
    if (open) setDraft(values);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  const cleared = Object.fromEntries(groups.map((g) => [g.key, ""]));

  return (
    <div className="sheet" role="dialog" aria-modal="true" aria-label={title}>
      <button type="button" className="sheet__scrim" aria-label="Tutup filter" onClick={onClose} />
      <div className="sheet__panel">
        <div className="sheet__grab" aria-hidden="true" />
        <div className="sheet__head">
          <h2 className="sheet__title">{title}</h2>
          <button type="button" className="link-btn" onClick={() => setDraft(cleared)}>
            Atur ulang
          </button>
        </div>
        {groups.map((g) => (
          <fieldset key={g.key} className="sheet__group">
            <legend className="ugroup__title">{g.label}</legend>
            <div className="sheet__grid">
              {g.options.map((o) => (
                <label key={o.value} className="sheet__opt">
                  <input
                    type="radio"
                    name={g.key}
                    value={o.value}
                    checked={draft[g.key] === o.value}
                    onChange={() => setDraft({ ...draft, [g.key]: o.value })}
                  />
                  <span>{o.label}</span>
                </label>
              ))}
            </div>
          </fieldset>
        ))}
        <button type="button" className="btn sheet__apply" onClick={() => onApply(draft)}>
          Terapkan
        </button>
      </div>
    </div>
  );
}
